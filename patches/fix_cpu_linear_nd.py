#!/usr/bin/env python3
"""
Patch vllm/model_executor/layers/utils.py in vLLM v0.16.1rc0 to fix a
ValueError when loading Qwen3.5 (and similar hybrid) models on CPU.

Root cause: dispatch_cpu_unquantized_gemm unconditionally does:
    N, K = layer.weight.size()
This raises "too many values to unpack (expected 2)" for layers that carry
a non-2D weight tensor (e.g. the 1-D convolutional linear-attention layers
in Qwen3.5 whose weights have shape [out, in, kernel]).

The fix adds a dimension guard: if the weight is not 2-D the function falls
back to standard torch.nn.functional.linear, which handles arbitrary shapes
correctly, and returns early without attempting the oneDNN / SGL-kernel path.
"""

import sys

FILENAME = "vllm/model_executor/layers/utils.py"

OLD = """\
    N, K = layer.weight.size()"""

NEW = """\
    if layer.weight.dim() != 2:
        layer.cpu_linear = torch.nn.functional.linear
        return
    N, K = layer.weight.size()"""

with open(FILENAME) as f:
    content = f.read()

count = content.count(OLD)
if count == 0:
    print(f"Pattern not found in {FILENAME} — already patched or unexpected version.")
    sys.exit(0)
if count > 1:
    print(f"ERROR: pattern found {count} times in {FILENAME} — refusing to patch.")
    sys.exit(1)

patched = content.replace(OLD, NEW, 1)
with open(FILENAME, "w") as f:
    f.write(patched)

print(f"Applied CPU dispatch_cpu_unquantized_gemm N-D weight fallback fix to {FILENAME}")
