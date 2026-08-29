from dataset_reasoning import analyze_question


def test_analyze_question():
    result = analyze_question(
        "What is my total revenue?",
        ["orders", "payments"],
        "solomonenamudu@gmail.com"
    )

    assert isinstance(result, dict)
    assert "answerable" in result
    assert "tables" in result