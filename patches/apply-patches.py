#!/usr/bin/env python3
"""Apply compatibility patches to vLLM source before building."""

import sys


def patch_dispatch_cpu_unquantized_gemm(vllm_path: str) -> None:
    """Fix dispatch_cpu_unquantized_gemm to handle non-2D weight tensors.

    Hybrid SSM/attention models like Qwen3.5 have Mamba layers whose weight
    tensors are >2D. The existing code unconditionally does
    `N, K = layer.weight.size()` which raises ValueError for these layers.
    Fall back to standard linear for non-2D weights.

    See: vllm/model_executor/layers/utils.py
    """
    path = f"{vllm_path}/vllm/model_executor/layers/utils.py"
    with open(path) as f:
        content = f.read()

    old = "    N, K = layer.weight.size()\n    dtype = layer.weight.dtype"
    new = (
        "    if layer.weight.dim() != 2:\n"
        "        # Non-2D weights (e.g., Mamba/SSM layers) cannot use optimized CPU kernels\n"
        "        layer.cpu_linear = torch.nn.functional.linear\n"
        "        return\n"
        "    N, K = layer.weight.size()\n"
        "    dtype = layer.weight.dtype"
    )

    if old not in content:
        print(f"WARNING: fix already applied or pattern changed in {path}")
        return

    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print(f"Patched: {path}")


if __name__ == "__main__":
    vllm_source = sys.argv[1] if len(sys.argv) > 1 else "."
    patch_dispatch_cpu_unquantized_gemm(vllm_source)
