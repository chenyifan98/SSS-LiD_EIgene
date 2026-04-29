# SSS-LiD_EIgene

Code and input data for generating elemental images for the SSS-LiD display pipeline.

## Contents

- `CODE/VF40201_GenEI_USAF.py`: main script for generating display images.
- `CODE/Func_GeneMap_360hz1080pV0927_corr.py`: lens/view mapping generation.
- `CODE/Func_TiffStackDir.py`: PNG/TIFF image I/O helpers.
- `ViewpointData/`: input multi-view PNG data.

Generated TIFF outputs under `CODE/VF40201_ImgDisp_ALL/` are not tracked in Git.

## Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run from the `CODE` directory:

```bash
python VF40201_GenEI_USAF.py
```
