"""Build the compact ONNX vegetation-segmentation model.

The graph smooths an NDVI tile with a 3x3 mean filter, then thresholds it to a
binary vegetation mask. It is deliberately small and reproducible (no training,
no download), so the whole inference pipeline runs offline and in CI. See
model_card.md for what it is, what it is not, and how to swap in a real
pretrained model (for example a torchgeo or Hugging Face land-cover network).
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "models" / "veg_segmenter.onnx"
NDVI_THRESHOLD = 0.3


def build_model(path: str | Path = DEFAULT_MODEL_PATH, threshold: float = NDVI_THRESHOLD) -> Path:
    """Construct and save the ONNX model. Returns the output path."""
    import numpy as np
    import onnx
    from onnx import TensorProto, helper, numpy_helper

    # 3x3 mean-smoothing kernel, shape [out_c=1, in_c=1, 3, 3].
    kernel = np.full((1, 1, 3, 3), 1.0 / 9.0, dtype=np.float32)
    weight = numpy_helper.from_array(kernel, name="smooth_w")
    thresh = numpy_helper.from_array(np.array([threshold], dtype=np.float32), name="thresh")

    ndvi = helper.make_tensor_value_info("ndvi", TensorProto.FLOAT, [1, 1, "H", "W"])
    mask = helper.make_tensor_value_info("mask", TensorProto.FLOAT, [1, 1, "H", "W"])

    nodes = [
        helper.make_node("Conv", ["ndvi", "smooth_w"], ["smoothed"], pads=[1, 1, 1, 1]),
        helper.make_node("Greater", ["smoothed", "thresh"], ["is_veg"]),
        helper.make_node("Cast", ["is_veg"], ["mask"], to=TensorProto.FLOAT),
    ]

    graph = helper.make_graph(nodes, "veg_segmenter", [ndvi], [mask], [weight, thresh])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    model.ir_version = 9
    onnx.checker.check_model(model)

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, str(out))
    return out


if __name__ == "__main__":
    print(f"wrote {build_model()}")
