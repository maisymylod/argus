# Sentinel-2

## Overview
Sentinel-2 is a wide-swath, high-resolution, multispectral imaging mission from
the European Space Agency (ESA) Copernicus programme. It carries the
MultiSpectral Instrument (MSI) with 13 spectral bands. Data is public and open.

## Revisit time
The constellation is two satellites, Sentinel-2A and Sentinel-2B. A single
satellite has a revisit time of 10 days at the equator. With both satellites
combined the effective revisit time is 5 days at the equator, and shorter at
higher latitudes due to swath overlap.

## Bands and resolution
Four bands are at 10 m resolution: B02 (blue), B03 (green), B04 (red), and B08
(near-infrared, NIR). Six bands are at 20 m and three at 60 m. The 10 m bands
are the ones most commonly used for vegetation and land-cover analysis.

## NDVI bands
NDVI from Sentinel-2 uses band B08 (NIR) and band B04 (red):
NDVI = (B08 - B04) / (B08 + B04). Both are 10 m bands, so the derived NDVI is
also 10 m.

## Processing levels
Level-1C is top-of-atmosphere reflectance. Level-2A is bottom-of-atmosphere
(surface) reflectance after atmospheric correction, and is preferred for
quantitative vegetation indices such as NDVI.
