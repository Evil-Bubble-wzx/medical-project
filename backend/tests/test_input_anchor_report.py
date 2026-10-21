from app.retrieval.input_anchor_report import input_anchor_outcomes


def test_completion_without_explanation_does_not_pass_input_grounding():
    data = {"cases": [{"case_id": "A", "input": {"history": "否认耳鸣"}}]}
    result = {"answer": {"status": "answered", "input_explanation": []}}
    rows = [{"case_id": "A", "result": result}]
    assert input_anchor_outcomes(data, rows)["cases"][0]["outcome"] == "missing_input_explanation"
    result["answer"]["input_explanation"] = [
        {
            "input_fields": ["history"],
            "input_anchors": [{"field": "history", "quote": "否认耳鸣", "state": "denied"}],
        }
    ]
    assert input_anchor_outcomes(data, rows)["cases"][0]["outcome"] == "nonempty_anchors_valid"
    result["answer"]["input_explanation"][0]["input_anchors"][0]["quote"] = "耳鸣"
    assert input_anchor_outcomes(data, rows)["cases"][0]["outcome"] == "invalid_input_anchors"


def test_unrun_and_withheld_are_reported_separately():
    data = {"cases": [{"case_id": "A", "input": {}}, {"case_id": "B", "input": {}}]}
    rows = [{"case_id": "A", "result": {"answer": {"status": "needs_information"}}}]
    assert [r["outcome"] for r in input_anchor_outcomes(data, rows)["cases"]] == [
        "answer_withheld",
        "not_run",
    ]


def test_literal_input_record_is_not_counted_as_medical_comparison():
    data = {"cases": [{"case_id": "A", "input": {"history": "病史未知"}}]}
    rows = [
        {
            "case_id": "A",
            "result": {
                "answer": {
                    "status": "answered",
                    "input_explanation": [
                        {
                            "source_kind": "patient_input",
                            "input_fields": ["history"],
                            "input_anchors": [
                                {"field": "history", "quote": "病史未知", "state": "unknown"}
                            ],
                        }
                    ],
                }
            },
        }
    ]
    assert input_anchor_outcomes(data, rows)["cases"][0]["outcome"] == "input_record_only"
