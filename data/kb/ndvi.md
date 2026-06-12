# NDVI and vegetation indices

## Definition
The Normalized Difference Vegetation Index (NDVI) measures live green vegetation
using the red and near-infrared (NIR) bands:
NDVI = (NIR - Red) / (NIR + Red). Values range from -1 to 1.

## Interpretation
Healthy, dense vegetation strongly reflects NIR and absorbs red, giving high
NDVI (roughly 0.6 to 0.9). Sparse vegetation is around 0.2 to 0.5. Bare soil,
rock, and built surfaces are near 0. Water and snow are often negative.

## Change detection
Differencing NDVI between two dates highlights vegetation gain or loss. A common
approach thresholds the NDVI delta: pixels above a positive threshold are gain,
below a negative threshold are loss. Cloud-free scenes and consistent processing
level (surface reflectance) are important to avoid false change.

## Related indices
EVI (Enhanced Vegetation Index) reduces atmospheric and soil background effects.
NDWI (Normalized Difference Water Index) maps open water. NDBI highlights
built-up areas. All follow the same normalized-difference form on different band
pairs.
