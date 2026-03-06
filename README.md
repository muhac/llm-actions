# LLM in GitHub Actions

[![Marketplace](https://img.shields.io/badge/Marketplace-llm--actions-red)](
https://github.com/marketplace/actions/llm-in-github-actions
)
[![License](https://img.shields.io/github/license/muhac/llm-actions)](
https://github.com/muhac/llm-actions?tab=MIT-1-ov-file
)

Run any Hugging Face model on a temporary vLLM server inside your CI pipeline.

## Quick start

```yaml
name: LLM smoke test
on: push

jobs:
  infer:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run LLM inference
        uses: muhac/llm-actions@v1
        # below are optional inputs
        with:
          model: Qwen/Qwen3.5-2B
          vllm_version: v0.16.0
          hf_token: ${{ secrets.HF_TOKEN }}

      # The rest of your workflow...
```

### Inputs

- `model`: The model to use for inference. Default is `Qwen/Qwen3.5-2B`.
- `vllm_version`: The version of [vllm](https://github.com/vllm-project/vllm) to use. Tested with `v0.16.0`. You may want a newer version for support of more models, but the compiling process may be different.
- `hf_token`: The Hugging Face token to use for downloading the model. If you are using a public model, you can leave it empty. If you are using a private model, you need to provide your Hugging Face token.

### Outputs

- `logs`: Full vLLM server log.

### Examples

[Here is an example workflow](https://github.com/muhac/llm-actions/blob/main/.github/workflows/test.yml) that runs a few models and makes api calls to them.

## For advanced users

This repository contains the code to run LLMs for inference in GitHub Actions. You can run LLMs hosted by vLLM, or write your own code to run LLMs in GitHub Actions. [Here are some examples with tested models.](https://github.com/muhac/llm-actions/blob/main/.github/workflows/dev.yml)

`Qwen/Qwen3.5-2B` is recommended as the default — it offers a good balance of speed and quality. For vision tasks, `Qwen/Qwen3-VL-2B-Instruct` is a compact multimodal model that fits comfortably within the runner's memory. If you want to disable thinking on Qwen3 models, add `/no_think` as the system prompt.

For latest models, checkout [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard#/?params=-1%2C6&official=true). Newer versions of vllm and transformers may support more models.

The largest size of the model that can be run in GitHub Actions is `6B`. `7B` models are too large to run in the current environment.
The limit is due to [the memory constraints](https://docs.github.com/en/actions/using-github-hosted-runners/using-github-hosted-runners/about-github-hosted-runners#standard-github-hosted-runners-for-public-repositories) of the GitHub Actions environment.

In extreme cases, you may run quantized `8B` (even `14B`) models to support advanced reasoning tasks. But the time will be extremely long and the workflow may be unstable.

## License

MIT

## Contributing

Pull requests are welcome.
