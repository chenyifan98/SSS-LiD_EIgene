# SSS-LiD_EIgene

This project is used to generate the element images required for SSS-LiD.

## Contents

- `CODE/VF40201_GenEI_USAF.py`: main script for generating display images.
- `CODE/Func_GeneMap_360hz1080pV0927_corr.py`: lens/view mapping generation.
- `CODE/Func_TiffStackDir.py`: PNG/TIFF image I/O helpers.

Generated TIFF outputs under `CODE/VF40201_ImgDisp_ALL/` and local input data under `ViewpointData/PlantTestUSAF/` are not tracked in Git.

## Data

The generated TIFF image data is not included in this GitHub repository. Please download the ZIP archive from Zenodo:

https://doi.org/10.5281/zenodo.19877166

After downloading, extract the data to:

```text
CODE/VF40201_ImgDisp_ALL/ALL_Img_Disp/
```

## Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run from the `CODE` directory:

```bash
python VF40201_GenEI_USAF.py
```
