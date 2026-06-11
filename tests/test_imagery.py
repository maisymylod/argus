import numpy as np
import pytest

from services.imagery.change import GAIN, LOSS, NONE, classify_change, ndvi_difference
from services.imagery.ndvi import compute_ndvi


def test_ndvi_range_and_values():
    red = np.array([[0.1, 0.5]], dtype=np.float32)
    nir = np.array([[0.5, 0.1]], dtype=np.float32)
    ndvi = compute_ndvi(red, nir)
    assert ndvi.dtype == np.float32
    assert np.all(ndvi <= 1.0) and np.all(ndvi >= -1.0)
    # first pixel is vegetated (nir > red) -> positive
    assert ndvi[0, 0] > 0 and ndvi[0, 1] < 0


def test_ndvi_handles_zero_denominator():
    z = np.zeros((2, 2), dtype=np.float32)
    assert np.all(compute_ndvi(z, z) == 0.0)


def test_classify_change():
    diff = np.array([[0.5, -0.5, 0.0]], dtype=np.float32)
    out = classify_change(diff, threshold=0.2)
    assert list(out.ravel()) == [GAIN, LOSS, NONE]


def test_ndvi_difference_sign():
    before = np.zeros((2, 2), dtype=np.float32)
    after = np.ones((2, 2), dtype=np.float32)
    assert np.all(ndvi_difference(before, after) == 1.0)


def test_synthetic_scene_is_deterministic():
    from services.imagery.pipeline import synthetic_scene

    a = synthetic_scene(32, seed=3, veg_fraction=0.5)
    b = synthetic_scene(32, seed=3, veg_fraction=0.5)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])


def test_demo_pipeline_writes_artifacts(tmp_path):
    pytest.importorskip("onnxruntime")
    pytest.importorskip("rasterio")
    pytest.importorskip("PIL")
    from services.imagery.pipeline import run_pipeline, synthetic_scene

    rb, nb = synthetic_scene(64, seed=1, veg_fraction=0.25)
    ra, na = synthetic_scene(64, seed=2, veg_fraction=0.6)
    bbox = [-121.6, 36.8, -121.4, 37.0]
    result = run_pipeline("test_aoi", bbox, rb, nb, ra, na, out_dir=tmp_path)

    assert result.ndvi_overlay.exists()
    assert result.change_overlay.exists()
    assert result.detections_geojson.exists()
    assert result.detection_count >= 1
    assert 0.0 <= result.coverage_fraction <= 1.0
