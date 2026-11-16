"""Score validation, totals, averages, grading and class statistics."""

# (minimum average, grade) - checked from the top down.
GRADE_SCALE = [
    (70, "A"),
    (60, "B"),
    (50, "C"),
    (45, "D"),
    (40, "E"),
    (0, "F"),
]


def validate_score(value):
    """Convert a value to a float between 0 and 100, or raise ValueError."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        raise ValueError("Score must be a number.")
    if not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100.")
    return round(score, 1)


def calculate_total(scores):
    """Sum the scores in a {course: {"score": x, ...}} dictionary."""
    return sum(entry["score"] for entry in scores.values())


def calculate_average(scores):
    """Return the average score, or 0 if there are no scores."""
    if not scores:
        return 0.0
    return round(calculate_total(scores) / len(scores), 2)


def assign_grade(average):
    """Return the letter grade for an average score."""
    for minimum, grade in GRADE_SCALE:
        if average >= minimum:
            return grade
    return "F"


def class_statistics(students):
    """Return statistics for a list of students, or None if nobody has scores."""
    scored = [s for s in students if s.scores]
    if not scored:
        return None

    averages = [s.average for s in scored]
    distribution = {grade: 0 for _, grade in GRADE_SCALE}
    for student in scored:
        distribution[student.grade] += 1

    return {
        "count": len(scored),
        "class_average": round(sum(averages) / len(averages), 2),
        "highest": max(scored, key=lambda s: s.average),
        "lowest": min(scored, key=lambda s: s.average),
        "distribution": distribution,
    }
