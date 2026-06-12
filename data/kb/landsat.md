# Landsat

## Overview
Landsat is a joint NASA and USGS program providing the longest continuous record
of space-based land observation, beginning in 1972. Landsat 8 (2013) and
Landsat 9 (2021) are the current operational satellites. Data is public and open.

## Revisit time
A single Landsat satellite has a 16-day repeat cycle. With Landsat 8 and
Landsat 9 phased 8 days apart, the combined revisit time is 8 days.

## Bands and resolution
The Operational Land Imager (OLI) provides 30 m multispectral bands and a 15 m
panchromatic band. The thermal instrument (TIRS) provides 100 m thermal bands
resampled to 30 m.

## NDVI bands
NDVI from Landsat 8 and 9 uses band B5 (NIR) and band B4 (red):
NDVI = (B5 - B4) / (B5 + B4), at 30 m resolution.

## Comparison with Sentinel-2
Landsat offers a longer historical archive and thermal bands; Sentinel-2 offers
finer 10 m resolution and a shorter combined revisit time. The two are often
used together (harmonized Landsat-Sentinel products) for denser time series.
