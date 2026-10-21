"""Download pinned Apache-2.0 reranker weights from the official model repository."""

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"


def open_with_retry(url, timeout=60):
    for attempt in range(3):
        try:
            return urllib.request.urlopen(url, timeout=timeout)
        except urllib.error.URLError:
            if attempt == 2:
                raise
            print("TLS/network request interrupted; retrying same verified HTTPS URL", flush=True)
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fp32", action="store_true", help="CPU FP32 compatibility fallback")
    args = parser.parse_args()
    directory = ROOT / "models/mmarco-minilm-reranker"
    directory.mkdir(parents=True, exist_ok=True)
    with open_with_retry(
        f"https://huggingface.co/api/models/{REPOSITORY}?blobs=true", timeout=30
    ) as response:
        info = json.load(response)
    revision = info["sha"]
    if info.get("cardData", {}).get("license") != "apache-2.0":
        raise ValueError("model_license_changed_review_required")
    names = {s["rfilename"]: s for s in info["siblings"]}
    model = "onnx/model.onnx" if args.fp32 else "onnx/model_qint8_avx512_vnni.onnx"
    files = {
        "model.onnx": model,
        "tokenizer.json": "tokenizer.json",
        "README.md": "README.md",
        "config.json": "config.json",
    }
    hashes = {}
    for local, remote in files.items():
        if remote not in names:
            raise ValueError("expected_model_file_missing")
        target = directory / local
        partial = directory / (local + ".partial")
        digest = hashlib.sha256()
        url = f"https://huggingface.co/{REPOSITORY}/resolve/{revision}/{remote}"
        print(f"Downloading {remote} at {revision}", flush=True)
        with open_with_retry(url, timeout=60) as response, partial.open("wb") as output:
            while data := response.read(1024 * 1024):
                digest.update(data)
                output.write(data)
        expected = names[remote].get("lfs", {}).get("sha256")
        if expected and expected != digest.hexdigest():
            raise ValueError("upstream_model_checksum_mismatch")
        partial.replace(target)
        hashes[local] = digest.hexdigest()
    manifest = {
        "model_id": REPOSITORY,
        "revision": revision,
        "license": "Apache-2.0",
        "source_model_file": model,
        "files": hashes,
        "task": "query-document-pair-sequence-classification",
        "max_tokens": 512,
        "prefixes": None,
        "score": "single raw relevance logit; higher is better",
    }
    (directory / "model-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
