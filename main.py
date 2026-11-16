"""Student Result Management System - entry point and main menu."""

import courses
import reports
import results
import storage
from student import (
    GENDERS,
    Student,
    validate_dob,
    validate_name,
    validate_student_id,
)

KEEP = "Keep current value"


def level_label(level):
    return f"{level}L"


# ------------------------------------------------------------ input helpers
def ask_valid(prompt, validator, allow_blank=False):
    """Keep asking until validator accepts the input (blank returns None if allowed)."""
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        try:
            return validator(raw)
        except ValueError as error:
            print(f"  ! {error}")


def choose_option(title, options, label=str):
    """Show a numbered list and return the option the user picks."""
    print(title)
    for number, option in enumerate(options, start=1):
        print(f"  {number}. {label(option)}")
    while True:
        raw = input("Enter number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  ! Please enter a number from 1 to {len(options)}.")


def confirm(question):
    return input(f"{question} (y/n): ").strip().lower() == "y"


def persist(db):
    storage.save_students(db)


def find_student(db):
    """Ask for an ID and return the matching Student, or None."""
    student_id = ask_valid(
        "Student ID, e.g. 24/sci01/157 (blank to cancel): ",
        validate_student_id,
        allow_blank=True,
    )
    if student_id is None:
        return None
    student = db.get(student_id)
    if student is None:
        print("  ! No student found with that ID.")
    return student


def select_group(db):
    """Let the user pick a class (department + level) or all students."""
    groups = sorted({(s.department, s.level) for s in db.values()})
    options = [None] + groups

    def label(group):
        if group is None:
            return "All students"
        return f"{group[0]} {level_label(group[1])}"

    choice = choose_option("Select class:", options, label)
    if choice is None:
        return list(db.values()), "All students"
    students = [s for s in db.values() if (s.department, s.level) == choice]
    return students, label(choice)


# ------------------------------------------------------ A. student management
def add_student(db):
    print("\n--- Add New Student ---")
    student_id = ask_valid("Student ID (e.g. 24/sci01/157): ", validate_student_id)
    if student_id in db:
        print("  ! That ID is already registered.")
        return
    name = ask_valid("Full name: ", validate_name)
    department = choose_option("Department:", courses.get_departments())
    level = choose_option(
        "Level:", courses.get_levels(department), label=level_label
    )
    gender = choose_option("Gender:", GENDERS)
    dob = ask_valid("Date of birth (YYYY-MM-DD): ", validate_dob)

    student = Student(student_id, name, department, level, gender, dob)
    db[student_id] = student
    persist(db)
    print(f"\n  Registered {student}.")
    print("  Courses to be scored:")
    for code, title in student.required_courses().items():
        print(f"    {code} - {title}")


def view_all(db):
    print()
    if not db:
        print("No students registered yet.")
        return
    ordered = sorted(db.values(), key=lambda s: s.student_id)
    print(reports.students_table(ordered))


def search_students(db):
    print("\n--- Search Students ---")
    query = input("Enter ID or part of a name (blank to cancel): ").strip().lower()
    if not query:
        return
    matches = [
        s for s in db.values()
        if query in s.student_id or query in s.full_name.lower()
    ]
    if matches:
        print(reports.students_table(matches, f"{len(matches)} MATCH(ES)"))
    else:
        print("  No matching students found.")


def update_student(db):
    print("\n--- Update Student ---")
    student = find_student(db)
    if student is None:
        return
    print(f"Editing {student}. Leave blank to keep the current value.")

    name = ask_valid(f"Full name [{student.full_name}]: ", validate_name, allow_blank=True)
    if name:
        student.full_name = name

    dob = ask_valid(
        f"Date of birth [{student.date_of_birth}]: ", validate_dob, allow_blank=True
    )
    if dob:
        student.date_of_birth = dob

    gender = choose_option(f"Gender [{student.gender}]:", GENDERS + [KEEP])
    if gender != KEEP:
        student.gender = gender

    if confirm("Change department/level?"):
        department = choose_option("Department:", courses.get_departments())
        level = choose_option(
            "Level:", courses.get_levels(department), label=level_label
        )
        new_courses = courses.get_courses(department, level)
        orphaned = [code for code in student.scores if code not in new_courses]
        proceed = True
        if orphaned:
            print(
                f"  Scores for {', '.join(orphaned)} do not belong to the new "
                "class and would be removed."
            )
            proceed = confirm("  Continue?")
        if proceed:
            student.department = department
            student.level = level
            for code in orphaned:
                del student.scores[code]
        else:
            print("  Department/level left unchanged.")

    persist(db)
    print("  Student updated.")


def delete_student(db):
    print("\n--- Delete Student ---")
    student = find_student(db)
    if student is None:
        return
    if confirm(f"Permanently delete {student}?"):
        del db[student.student_id]
        persist(db)
        print("  Student deleted.")
    else:
        print("  Deletion cancelled.")


# ----------------------------------------------------- B. score management
def record_scores(db):
    print("\n--- Record / Update Scores ---")
    student = find_student(db)
    if student is None:
        return
    print(f"\nScores for {student}")
    print("Enter a score from 0 to 100. Press Enter to skip a course.")
    changed = False
    for code, title in student.required_courses().items():
        current = student.scores.get(code)
        shown = f"{current['score']}" if current else "none"
        while True:
            raw = input(f"  {code} - {title} (current: {shown}): ").strip()
            if raw == "":
                break
            try:
                student.set_score(code, raw)
                changed = True
                break
            except ValueError as error:
                print(f"  ! {error}")

    if changed:
        persist(db)
        print(
            f"\n  Saved. Total: {student.total:.1f} | "
            f"Average: {student.average:.2f} | Grade: {student.grade}"
        )
    else:
        print("  No changes made.")


def show_report_card(db):
    print("\n--- Report Card ---")
    student = find_student(db)
    if student is None:
        return
    card = reports.report_card(student)
    print()
    print(card)
    if confirm("\nSave this report card to a file?"):
        safe_id = student.student_id.replace("/", "-")
        path = reports.save_report(card, prefix=f"report_card_{safe_id}")
        if path:
            print(f"  Saved to {path}")


# --------------------------------------------------- C. reporting & analysis
def list_results(db):
    print("\n--- List Results ---")
    if not db:
        print("No students registered yet.")
        return
    students, label = select_group(db)
    sort_by = choose_option(
        "Sort by:",
        ["Average (highest to lowest)", "Name (A-Z)", "Student ID"],
    )
    if sort_by.startswith("Average"):
        ordered = sorted(students, key=lambda s: s.average, reverse=True)
    elif sort_by.startswith("Name"):
        ordered = sorted(students, key=lambda s: s.full_name.lower())
    else:
        ordered = sorted(students, key=lambda s: s.student_id)
    print()
    print(reports.students_table(ordered, f"RESULTS - {label} (sorted by {sort_by})"))


def class_stats(db):
    print("\n--- Class Statistics ---")
    if not db:
        print("No students registered yet.")
        return
    students, label = select_group(db)
    print()
    print(reports.statistics_text(results.class_statistics(students), label))


def save_text_report(db):
    print("\n--- Save Text Report ---")
    if not db:
        print("No students registered yet.")
        return
    students, label = select_group(db)
    text = reports.full_report(students, label)
    path = reports.save_report(text, prefix="class_report")
    if path:
        print(f"  Report saved to {path}")


# ---------------------------------------------------------------------- menu
MENU = [
    ("1", "Add student", add_student),
    ("2", "View all students", view_all),
    ("3", "Search student (ID or name)", search_students),
    ("4", "Update student information", update_student),
    ("5", "Delete student", delete_student),
    ("6", "Record / update scores", record_scores),
    ("7", "Show student report card", show_report_card),
    ("8", "List results (sort by average or name)", list_results),
    ("9", "Class statistics", class_stats),
    ("10", "Save text report to file", save_text_report),
]


def print_menu():
    print("\n" + "=" * 46)
    print(" STUDENT RESULT MANAGEMENT SYSTEM")
    print("=" * 46)
    for key, text, _ in MENU:
        print(f" {key:>2}. {text}")
    print("  0. Exit")


def main():
    for warning in courses.check_catalogue():
        print(f"Catalogue warning: {warning}")

    db = storage.load_students()
    actions = {key: action for key, _, action in MENU}

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("  ! Invalid option, please try again.")
            continue
        action(db)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting. Your data is saved after every change.")
