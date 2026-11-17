"""Build text reports (report cards, result tables, class statistics) and save them."""

import os
from datetime import datetime

import results

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

CARD_WIDTH = 72
TABLE_WIDTH = 89


def _fmt(value, has_scores):
    return f"{value:.1f}" if has_scores else "-"


def report_card(student):
    """Return an individual report card as text."""
    lines = [
        "=" * CARD_WIDTH,
        "STUDENT REPORT CARD".center(CARD_WIDTH),
        "=" * CARD_WIDTH,
        f"Name       : {student.full_name}",
        f"Student ID : {student.student_id}",
        f"Department : {student.department}",
        f"Level      : {student.level}L",
        f"Gender     : {student.gender}",
        f"Birth date : {student.date_of_birth}",
        "-" * CARD_WIDTH,
        f"{'Course':<10}{'Title':<34}{'Score':>8}{'Date Entered':>20}",
        "-" * CARD_WIDTH,
    ]
    for code, title in student.required_courses().items():
        entry = student.scores.get(code)
        if entry:
            lines.append(
                f"{code:<10}{title:<34}{entry['score']:>8.1f}{entry['date_entered']:>20}"
            )
        else:
            lines.append(f"{code:<10}{title:<34}{'-':>8}{'not recorded':>20}")

    has_scores = bool(student.scores)
    lines += [
        "-" * CARD_WIDTH,
        f"Total   : {_fmt(student.total, has_scores)}",
        f"Average : {_fmt(student.average, has_scores)}",
        f"Grade   : {student.grade}",
    ]
    if has_scores and not student.is_complete:
        lines.append(
            "Note    : incomplete result - missing " + ", ".join(student.missing_courses())
        )
    lines.append("=" * CARD_WIDTH)
    return "\n".join(lines)


def students_table(students, title="ALL STUDENTS"):
    """Return a table of students with totals, averages and grades."""
    lines = [
        title,
        "-" * TABLE_WIDTH,
        f"{'ID':<14}{'Name':<27}{'Department':<19}{'Level':<6}"
        f"{'Total':>8}{'Avg':>8}{'Grade':>7}",
        "-" * TABLE_WIDTH,
    ]
    any_incomplete = False
    for s in students:
        has_scores = bool(s.scores)
        grade = s.grade
        if has_scores and not s.is_complete:
            grade += "*"
            any_incomplete = True
        lines.append(
            f"{s.student_id:<14}{s.full_name[:25]:<27}{s.department[:17]:<19}"
            f"{str(s.level) + 'L':<6}{_fmt(s.total, has_scores):>8}"
            f"{_fmt(s.average, has_scores):>8}{grade:>7}"
        )
    lines.append("-" * TABLE_WIDTH)
    if any_incomplete:
        lines.append("* = some courses have not been recorded yet")
    return "\n".join(lines)


def statistics_text(stats, label):
    """Return class statistics as text."""
    header = f"CLASS STATISTICS - {label}"
    if stats is None:
        return f"{header}\n{'-' * TABLE_WIDTH}\nNo scores recorded yet."

    high, low = stats["highest"], stats["lowest"]
    distribution = ", ".join(f"{g}={n}" for g, n in stats["distribution"].items())
    return "\n".join([
        header,
        "-" * TABLE_WIDTH,
        f"Students with scores : {stats['count']}",
        f"Class average        : {stats['class_average']:.2f}",
        f"Highest average      : {high.average:.2f} ({high.full_name}, {high.student_id})",
        f"Lowest average       : {low.average:.2f} ({low.full_name}, {low.student_id})",
        f"Grade distribution   : {distribution}",
    ])


def full_report(students, label):
    """Return the complete class report (ranked by average) as text."""
    ranked = sorted(students, key=lambda s: s.average, reverse=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    return "\n\n".join([
        "STUDENT RESULT MANAGEMENT SYSTEM".center(TABLE_WIDTH)
        + f"\n{('Class: ' + label).center(TABLE_WIDTH)}"
        + f"\n{('Generated: ' + generated).center(TABLE_WIDTH)}",
        students_table(ranked, "RESULTS (highest to lowest average)"),
        statistics_text(results.class_statistics(students), label),
    ])


def save_report(text, prefix="report"):
    """Save text to reports/<prefix>_<timestamp>.txt and return the path (or None)."""
    filename = f"{prefix}_{datetime.now():%Y%m%d_%H%M%S}.txt"
    path = os.path.join(REPORTS_DIR, filename)
    try:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(text + "\n")
    except OSError as error:
        print(f"  ! Could not save the report: {error}")
        return None
    return path
