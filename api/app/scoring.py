SECTION_QUESTIONS = {
    "governance": ["q1", "q2", "q3"],
    "financials": ["q4", "q5", "q6"],
    "market": ["q7", "q8", "q9"],
    "operations": ["q10", "q11", "q12"],
}

SECTION_RECOMMENDATIONS = {
    "governance": "Formalize governance with documented roles, policies, and board oversight.",
    "financials": "Improve financial reporting quality and cash-flow forecasting.",
    "market": "Strengthen market validation and customer acquisition strategy.",
    "operations": "Document operational KPIs and standard operating procedures.",
}


def score_assessment(answers: dict[str, int]) -> tuple[dict[str, int], int, list[str]]:
    section_scores: dict[str, int] = {}

    for section, questions in SECTION_QUESTIONS.items():
        values = [max(1, min(5, int(answers.get(question, 1)))) for question in questions]
        max_points = len(questions) * 5
        section_scores[section] = round((sum(values) / max_points) * 100)

    total_score = round(sum(section_scores.values()) / len(section_scores))

    recommendations = [
        SECTION_RECOMMENDATIONS[section]
        for section, score in section_scores.items()
        if score < 70
    ]
    if not recommendations:
        recommendations = ["Your company is investment-ready. Maintain momentum with quarterly reviews."]

    return section_scores, total_score, recommendations
