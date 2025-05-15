# ================================================================
#  medrouter_client.py   (GUI-friendly)
# ================================================================
from __future__ import annotations
import os, time, tempfile, zipfile, shutil, random, sys
from pathlib import Path
from typing import Dict, Optional

import requests, slicer
from qt import QProgressDialog  # Qt comes with Slicer


# ----------------------------------------------------------------
#  Helper utilities
# ----------------------------------------------------------------
def _find_first_volume():
    n = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
    if not n:
        raise RuntimeError("Load a volume before using MedRouterClient.")
    return n


def _export_nifti(vol):
    tmp = Path(tempfile.mkdtemp())
    out = tmp / "input.nii.gz"
    slicer.util.saveNode(vol, str(out))
    return out, tmp


def _export_dicom_zip(vol):
    tmp = Path(tempfile.mkdtemp())
    dicom_dir = tmp / "dicom"; dicom_dir.mkdir()

    sh = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    itm = sh.GetItemByDataNode(vol)
    pat = sh.CreateSubjectItem(sh.GetSceneItemID(), "TempPatient")
    std = sh.CreateStudyItem(pat, "TempStudy")
    sh.SetItemParent(itm, std)

    import DICOMScalarVolumePlugin
    exp = DICOMScalarVolumePlugin.DICOMScalarVolumePluginClass()
    for ex in exp.examineForExport(itm):
        ex.directory = str(dicom_dir)
        exp.export([ex])

    zip_path = tmp / "dicom.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(dicom_dir):
            for f in files:
                p = Path(root) / f
                zf.write(p, p.relative_to(dicom_dir))
    return zip_path, tmp


def _rand_rgb():
    from random import random
    return random(), random(), random()


# ----------------------------------------------------------------
#  Main client
# ----------------------------------------------------------------
class MedRouterClient:
    INFERENCE_URL = "https://api.medrouter.co/api/inference/use/"
    REQUEST_URL   = "https://api.medrouter.co/api/requests/{rid}"

    # ------------------------------------------------------------
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        model_id: int | str,
        upload_format: str = "nifti",       # "nifti" | "dicom"
        download_format: str = "nifti",     # "nifti" | "stl"
        extra_output_type: Optional[str] = None,
        poll_delay: int = 20,
        show_progress: bool = True,
    ):
        if upload_format not in ("nifti", "dicom"):
            raise ValueError("upload_format must be 'nifti' or 'dicom'")
        if download_format not in ("nifti", "stl"):
            raise ValueError("download_format must be 'nifti' or 'stl'")

        self.api_key, self.model, self.model_id = api_key, model, str(model_id)
        self.upload_format, self.download_format = upload_format, download_format
        self.extra_output, self.poll_delay = extra_output_type, poll_delay
        self._progress = QProgressDialog("Waiting for MedRouter…", "Cancel", 0, 0) if show_progress else None

    # ------------------------------------------------------------
    #  public API
    # ------------------------------------------------------------
    def run(self, notes: str = "") -> None:
        vol = _find_first_volume()

        src, work_dir = (_export_nifti(vol) if self.upload_format == "nifti"
                         else _export_dicom_zip(vol))

        try:
            rid = self._post(src, notes)
            outputs = self._poll_until_ready(rid)
            files, dl_dir = self._download(outputs)
            try:
                self._import(vol, files)
                self._log("🎉 All done.")
            finally:
                shutil.rmtree(dl_dir, ignore_errors=True)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)
            if self._progress:
                self._progress.close()

    # ------------------------------------------------------------
    #  internals
    # ------------------------------------------------------------
    def _log(self, msg: str):
        print(f"[MedRouter] {msg}", flush=True)
        slicer.app.processEvents()          # keeps Interactor & GUI alive
        if self._progress:
            self._progress.setLabelText(msg)
            slicer.app.processEvents()

    def _post(self, src: Path, notes: str) -> str:
        payload = {"model": self.model, "model_id": self.model_id, "notes": notes}
        if self.extra_output: payload["extra_output_type"] = self.extra_output

        self._log("Uploading case …")
        with open(src, "rb") as f:
            r = requests.post(
                self.INFERENCE_URL,
                headers={"Authorization": self.api_key},
                files={"file": (src.name, f)},
                data=payload,
            )
        r.raise_for_status()
        rid = r.json().get("request_id")
        if not rid:
            raise RuntimeError("Upload succeeded but no request_id returned.")
        self._log(f"Upload OK – request_id = {rid}")
        return rid

    def _poll_until_ready(self, rid: str) -> Dict:
        while True:
            r = requests.get(self.REQUEST_URL.format(rid=rid),
                             headers={"Authorization": self.api_key})
            r.raise_for_status()
            info = r.json(); status = info.get("status")
            if status == "processed":
                self._log("Job processed ✓")
                return info["output"]
            self._log(f"Status = '{status}', waiting {self.poll_delay}s …")
            for _ in range(self.poll_delay):
                slicer.app.processEvents()
                time.sleep(1)

    def _download(self, outputs: Dict[str, Dict[str, str]]):
        want = self.download_format
        if want not in outputs:
            raise RuntimeError(f"No '{want}' outputs from server.")
        tmp = Path(tempfile.mkdtemp()); local = {}
        for name, url in outputs[want].items():
            ext = "nii.gz" if want == "nifti" else "stl"
            dst = tmp / f"{name}.{ext}"
            self._log(f"Downloading {name} …")
            r = requests.get(url, stream=True); r.raise_for_status()
            with open(dst, "wb") as f: shutil.copyfileobj(r.raw, f)
            local[name] = dst
        return local, tmp

    # ---- Slicer import ------------------------------------------------------
    def _import(self, vol, files: Dict[str, Path]):
        if self.download_format == "nifti":
            self._import_masks(vol, files)
        else:
            self._import_meshes(files)

    def _import_masks(self, vol, masks):
        seg = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLSegmentationNode", "MedRouter Segmentation"
        )
        seg.CreateDefaultDisplayNodes()
        seg.SetReferenceImageGeometryParameterFromVolumeNode(vol)
        logic = slicer.modules.segmentations.logic()

        for name, path in masks.items():
            lbl = slicer.util.loadVolume(str(path), properties={"labelmap": True})
            logic.ImportLabelmapToSegmentationNode(lbl, seg)
            seg_id = seg.GetSegmentation().GetNthSegmentID(
                seg.GetSegmentation().GetNumberOfSegments() - 1
            )
            s = seg.GetSegmentation().GetSegment(seg_id)
            s.SetName(name); s.SetColor(*_rand_rgb())
            slicer.mrmlScene.RemoveNode(lbl)

        self._log(f"{seg.GetSegmentation().GetNumberOfSegments()} segments imported.")

    def _import_meshes(self, meshes):
        for name, path in meshes.items():
            mdl = slicer.util.loadModel(str(path)); mdl.SetName(name)
        self._log(f"{len(meshes)} STL meshes imported.")


# ----------------------------------------------------------------
#  USAGE EXAMPLE
# ----------------------------------------------------------------

client = MedRouterClient(
    api_key="API-KEY",
    model="total-segmentator",
    model_id=570,
    upload_format="nifti",   
    download_format="nifti",    
    extra_output_type=None,    
    poll_delay=20,              # seconds
)
client.run(notes="Sent from Slicer")
