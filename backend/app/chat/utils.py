def get_current_question(questions: list[dict]) -> dict | None:
    for q in questions:
        if not q["used"]:
            return q
    return None


def mark_question_used(questions: list[dict], question_id: str):
    for q in questions:
        if q["question_id"] == question_id:
            q["used"] = True
            return


def apply_evaluation(questions: list[dict], evaluation: list[dict]):
    for ev in evaluation:
        for q in questions:
            if q["text"] == ev["question"]:
                q["score"] = ev["score"]
                q["mistakes"] = ev["score"] < 10