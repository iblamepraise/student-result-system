"""Load and save student data as JSON."""

import json
import os

from student import Student

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "students.json")


def load_students(filepath=DATA_FILE):
    """Return {student_id: Student}. Never crashes if the file is missing or damaged."""
    students = {}
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("No data file found yet - starting with an empty system.")
    except json.JSONDecodeError:
        backup = filepath + ".corrupt"
        os.replace(filepath, backup)
        print(f"Data file was damaged. It was kept as '{backup}'; starting fresh.")
    except OSError as error:
        print(f"Could not read the data file: {error}")
    else:
        records = data.get("students", []) if isinstance(data, dict) else []
        for record in records:
            try:
                student = Student.from_dict(record)
            except (KeyError, TypeError, ValueError):
                print("Skipped one malformed record in the data file.")
                continue
            students[student.student_id] = student
        print(f"Loaded {len(students)} student(s) from file.")
    return students


def save_students(students, filepath=DATA_FILE):
    """Write all students to disk. Returns True on success, False on failure."""
    temp_path = filepath + ".tmp"
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        payload = {"students": [s.to_dict() for s in students.values()]}
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4)
        os.replace(temp_path, filepath)  # swap in only after a complete write
    except OSError as error:
        print(f"  ! Could not save data: {error}")
        return False
    else:
        return True
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
