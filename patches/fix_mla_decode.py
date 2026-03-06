#!/usr/bin/env python3
"""
Patch csrc/cpu/mla_decode.cpp for vLLM v0.16.0 to fix BFloat16 compilation
on x86 CPUs without AVX512BF16 (e.g. AVX2-only GitHub Actions runners).

Root cause: v0.16.0 only specialised KernelVecType<BFloat16> for __AVX512BF16__,
__s390x__, and __aarch64__.  On plain x86/AVX2 the type falls back to the base
template where qk_vec_type = void, causing a compile error at:
    constexpr int QK_NUM_ELEM = qk_vec_type::VEC_ELEM_NUM;

The fix matches the upstream correction already merged to vLLM main: collapse the
three architecture-specific specialisations into a simple #ifdef __AVX512BF16__ /
#else so that every non-AVX512 platform gets the BF16Vec16 / FP32Vec16 path.
"""

import sys

FILENAME = "csrc/cpu/mla_decode.cpp"

# Block present in vLLM v0.16.0 after the closing }; of the __AVX512BF16__
# specialisation (lines 41-57).  The leading newline is intentional — it
# anchors the match to the blank separator line between the two blocks.
OLD = """
#elif defined(__s390x__)
template <>
struct KernelVecType<c10::BFloat16> {
  using qk_load_vec_type = vec_op::BF16Vec16;
  using qk_vec_type = vec_op::FP32Vec16;
  using v_load_vec_type = vec_op::BF16Vec16;
};

#elif defined(__aarch64__)
template <>
struct KernelVecType<c10::BFloat16> {
  using qk_load_vec_type = vec_op::BF16Vec16;
  using qk_vec_type = vec_op::FP32Vec16;
  using v_load_vec_type = vec_op::BF16Vec16;
};
#endif"""

# Replacement matching the fix already merged to vLLM main
NEW = """
#else
template <>
struct KernelVecType<c10::BFloat16> {
  using qk_load_vec_type = vec_op::BF16Vec16;
  using qk_vec_type = vec_op::FP32Vec16;
  using v_load_vec_type = vec_op::BF16Vec16;
};
#endif"""

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

print(f"Applied BFloat16 AVX2 fallback fix to {FILENAME}")
