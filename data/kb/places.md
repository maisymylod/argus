# Sample areas of interest

## Central Valley, California
A major agricultural region in California. Strong seasonal NDVI signal from
irrigated crops makes it a clear example for vegetation phenology and
month-to-month change. Bounding box roughly -121.6, 36.8 to -121.4, 37.0.

## Rondonia, Brazil
A region of the Amazon in western Brazil that is a classic example for
deforestation monitoring. Year-over-year NDVI change reveals forest loss.
Bounding box roughly -63.0, -9.5 to -62.8, -9.3.

## Choosing dates
For change detection, pick two cloud-free scenes separated enough in time to
capture the change of interest: a few months for crop seasonality, a year or
more for deforestation. Argus searches for the least-cloudy scene in a window
around each requested date.
