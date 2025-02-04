import argparse
from . import __version__

def main():
    parser = argparse.ArgumentParser(description="MedRouter library CLI.")
    parser.add_argument("--version", action="version", version=f"MedRouter version {__version__}")
    args = parser.parse_args()

if __name__ == "__main__":
    main()