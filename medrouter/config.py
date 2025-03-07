AVAILABLE_MODELS = [
    "total-segmentator"
]

ACCEPTED_FILE_TYPES = [
    ".nii",
    ".nii.gz",
    ".zip"
] 

ACCEPTED_EXTRA_OUTPUTS_TYPES = [
    "stl",
    "ply"
]

TASKS = {
    0: "total", 
    1: "total_mr",
    258: "lung_vessels",
    260: "hip_implant",
    315: "pleural_pericard_effusion",
    775: "head_glands_cavities",
    776: "headneck_bones_vessels",
    777: "head_muscles",
    778779: "headneck_muscles",
    351: "oculomotor_muscles",
    913: "lung_nodules",
    789: "kidney_cysts",
    527: "breasts",
    552: "ventricle_parts",
    570: "liver_segments",
    576: "liver_segments_mr",
    756: "vertebrae_mr",
    291: "abdominal_organs_and_vessels_segmentation",
    292: "spine_vertebrae_segmentation",
    293: "cardiovascular_system_segmentation",
    294: "musculoskeletal_system_segmentation",
    295: "rib_cage_and_sternum_segmentation",
    850: "custom",
    851: "custom",
}