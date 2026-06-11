import numpy as np
import pytest


def test_build_and_segment(tmp_path):
    pytest.importorskip("onnx")
    pytest.importorskip("onnxruntime")
    from services.ml.build_model import build_model
    from services.ml.infer import segment

    model_path = tmp_path / "veg.onnx"
    build_model(model_path)
    assert model_path.exists()

    # High-NDVI block should segment as vegetation; low-NDVI background should not.
    ndvi = np.full((32, 32), -0.2, dtype=np.float32)
    ndvi[:16, :16] = 0.8
    mask = segment(ndvi, model_path=model_path)
    assert mask.shape == (32, 32)
    assert mask[:16, :16].mean() > 0.8
    assert mask[16:, 16:].mean() < 0.2


def test_mask_to_geojson():
    pytest.importorskip("rasterio")
    from services.ml.postprocess import mask_to_geojson

    mask = np.zeros((16, 16), dtype=np.uint8)
    mask[2:8, 2:8] = 1
    fc = mask_to_geojson(mask, [-121.6, 36.8, -121.4, 37.0], label="vegetation")

    assert fc["type"] == "FeatureCollection"
    assert fc["properties"]["detection_count"] >= 1
    feat = fc["features"][0]
    assert feat["geometry"]["type"] == "Polygon"
    # Coordinates must fall within the AOI bbox.
    for lon, lat in feat["geometry"]["coordinates"][0]:
        assert -121.6 <= lon <= -121.4
        assert 36.8 <= lat <= 37.0
