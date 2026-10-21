"""Standalone CPU worker: uses the explicitly configured Python runtime, never a model API."""

import argparse
import json
import sys
from importlib.metadata import version
from pathlib import Path


def main():
    import numpy as np
    import onnxruntime as ort
    from tokenizers import Tokenizer

    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    request = (
        json.loads(sys.stdin.buffer.read())
        if str(args.input) == "-"
        else json.loads(args.input.read_text(encoding="utf-8"))
    )
    tokenizer = Tokenizer.from_file(str(args.model / "tokenizer.json"))
    tokenizer.enable_truncation(max_length=512)
    tokenizer.enable_padding(pad_id=1, pad_token="<pad>")
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(
        str(args.model / "model.onnx"), sess_options=options, providers=["CPUExecutionProvider"]
    )
    required = {item.name for item in session.get_inputs()}
    vectors = []
    for start in range(0, len(request["texts"]), 16):
        encoded = tokenizer.encode_batch(request["texts"][start : start + 16])
        ids = np.array([item.ids for item in encoded], dtype=np.int64)
        masks = np.array([item.attention_mask for item in encoded], dtype=np.int64)
        feed = {"input_ids": ids, "attention_mask": masks}
        if "token_type_ids" in required:
            feed["token_type_ids"] = np.zeros_like(ids)
        hidden = session.run(None, feed)[0]
        expanded = masks[:, :, None].astype(np.float32)
        pooled = (hidden * expanded).sum(axis=1) / expanded.sum(axis=1).clip(min=1)
        pooled /= np.linalg.norm(pooled, axis=1, keepdims=True).clip(min=1e-12)
        vectors.extend(pooled.tolist())
    result = {
        "vectors": vectors,
        "dimension": 384,
        "dependencies": {p: version(p) for p in ("numpy", "onnxruntime", "tokenizers")},
    }
    if str(args.output) == "-":
        sys.stdout.buffer.write(json.dumps(result).encode("utf-8"))
    else:
        args.output.write_text(json.dumps(result), encoding="utf-8")


if __name__ == "__main__":
    main()
