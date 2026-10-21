"""Standalone offline CPU cross-encoder, no remote model code."""

import json
import sys
from importlib.metadata import version
from pathlib import Path


def main():
    import numpy as np
    import onnxruntime as ort
    from tokenizers import Tokenizer

    directory, request, response = map(Path, sys.argv[1:])
    payload = (
        sys.stdin.buffer.read() if str(request) == "-" else request.read_text(encoding="utf-8")
    )
    pairs = json.loads(payload)["pairs"]
    tokenizer = Tokenizer.from_file(str(directory / "tokenizer.json"))
    tokenizer.enable_truncation(max_length=512, strategy="only_second")
    tokenizer.enable_padding(pad_id=1, pad_token="<pad>")
    options = ort.SessionOptions()
    options.intra_op_num_threads, options.inter_op_num_threads = 2, 1
    session = ort.InferenceSession(
        str(directory / "model.onnx"), sess_options=options, providers=["CPUExecutionProvider"]
    )
    required = {i.name for i in session.get_inputs()}
    scores = []
    for start in range(0, len(pairs), 8):
        encodings = tokenizer.encode_batch([tuple(p) for p in pairs[start : start + 8]])
        ids = np.asarray([e.ids for e in encodings], dtype=np.int64)
        feed = {
            "input_ids": ids,
            "attention_mask": np.asarray([e.attention_mask for e in encodings], dtype=np.int64),
        }
        if "token_type_ids" in required:
            feed["token_type_ids"] = np.asarray([e.type_ids for e in encodings], dtype=np.int64)
        logits = session.run(None, feed)[0]
        if logits.shape != (len(encodings), 1):
            raise ValueError("expected_one_relevance_logit")
        scores.extend(logits[:, 0].tolist())
    result = json.dumps(
        {
            "scores": scores,
            "runtime": {p: version(p) for p in ("numpy", "onnxruntime", "tokenizers")},
        }
    )
    if str(response) == "-":
        sys.stdout.buffer.write(result.encode("utf-8"))
    else:
        response.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
