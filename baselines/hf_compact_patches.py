"""
HuggingFace compatibility patches for IndicTrans2.
"""

import sys
import types
import transformers as _transformers
from transformers import dynamic_module_utils


def apply_hf_patches():
    """
    Apply all HuggingFace compatibility patches.
    Call ONCE before loading any HF model.
    """

    # --------------------------------------------------------------
    # Patch 1: tie_weights unexpected keyword argument
    # --------------------------------------------------------------
    orig_get_class = dynamic_module_utils.get_class_from_dynamic_module

    def get_class_from_dynamic_module_patch(*args, **kwargs):
        cls = orig_get_class(*args, **kwargs)

        if hasattr(cls, "tie_weights"):
            orig_tie_weights = cls.tie_weights

            def tie_weights_patch(self, *args, **kwargs):
                kwargs.pop("missing_keys", None)
                kwargs.pop("recompute_mapping", None)
                return orig_tie_weights(self, *args, **kwargs)

            cls.tie_weights = tie_weights_patch

        return cls

    dynamic_module_utils.get_class_from_dynamic_module = (
        get_class_from_dynamic_module_patch
    )

    # --------------------------------------------------------------
    # Patch 2: transformers.onnx shim
    # --------------------------------------------------------------
    try:
        import transformers.onnx  # noqa: F401
    except ImportError:
        onnx_mod = types.ModuleType("transformers.onnx")
        onnx_mod.__path__ = []

        class OnnxConfig:
            def __init__(self, config, task="default", patching_specs=None):
                self.config = config
                self.task = task
                self.patching_specs = patching_specs

            @property
            def inputs(self):
                return {}

            @property
            def outputs(self):
                return {}

            def generate_dummy_inputs(self, tokenizer, **kwargs):
                return {}

        class OnnxSeq2SeqConfigWithPast(OnnxConfig):
            pass

        onnx_mod.OnnxConfig = OnnxConfig
        onnx_mod.OnnxSeq2SeqConfigWithPast = OnnxSeq2SeqConfigWithPast

        onnx_utils_mod = types.ModuleType("transformers.onnx.utils")

        def compute_effective_axis_dimension(dimension, fixed_dimension, num_token_to_add):
            return dimension

        onnx_utils_mod.compute_effective_axis_dimension = (
            compute_effective_axis_dimension
        )

        sys.modules["transformers.onnx"] = onnx_mod
        sys.modules["transformers.onnx.utils"] = onnx_utils_mod
        onnx_mod.utils = onnx_utils_mod