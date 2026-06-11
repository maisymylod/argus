# Model card: veg_segmenter (ONNX)

## Summary
A compact ONNX model that segments vegetation from a single-band NDVI tile. It
applies a 3x3 mean smoothing convolution and thresholds the result (default NDVI
> 0.3) to a binary mask. The mask is vectorized to GeoJSON polygons downstream.

## Why it exists
To demonstrate the end-to-end inference pipeline (NDVI tile in, ONNX runtime,
vector detections out) in a way that is fully reproducible, offline, and
CI-friendly. It requires no training data, no GPU, and no model download.

## Inputs and outputs
- Input `ndvi`: float32 tensor `[1, 1, H, W]`, values in [-1, 1].
- Output `mask`: float32 tensor `[1, 1, H, W]`, 1.0 = vegetation, 0.0 = other.

## What it is not
This is not a learned, benchmarked land-cover classifier. It is a deterministic
threshold model in ONNX form. It will mislabel non-vegetated bright-NIR surfaces
and is not validated against ground truth.

## Swapping in a real pretrained model
The inference wrapper (`infer.py`) only assumes an ONNX session with an `ndvi`
input and a single mask-like output. To upgrade:
1. Export a pretrained segmentation or scene-classification network to ONNX
   (for example a torchgeo land-cover model or a EuroSAT-trained classifier).
2. Adjust the input name and channel count in `infer.segment`.
3. Replace `models/veg_segmenter.onnx` (or point `MODEL_PATH` at the new file).

## Provenance
Built by `services/ml/build_model.py` at container build time and on first use.
Operates only on public Sentinel-2 derived NDVI (see README data policy).
