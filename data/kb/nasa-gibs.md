# NASA GIBS

## Overview
The Global Imagery Browse Services (GIBS) from NASA provide full-resolution
satellite imagery as web tiles. Imagery is public and served through standard
protocols, so it can back a web map without per-tile processing.

## Access
GIBS supports WMTS, WMS, and TMS. Tiled WMTS endpoints are the common choice for
slippy maps (for example MapLibre or Leaflet). Many layers are updated daily,
including MODIS and VIIRS true-color and derived products.

## When to use
Use GIBS for fast visual base layers and daily global context. Use a STAC source
such as Sentinel-2 or Landsat when you need raw band data for computing indices
or running models. Argus uses STAC for analysis and can use GIBS or other open
tiles for the base map.
