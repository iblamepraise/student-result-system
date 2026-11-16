"""Student class and input-validation helpers."""

import re
from datetime import date, datetime

import courses
import results

# year/deptnum/id  ->  e.g. 24/sci01/157
STUDENT_ID_PATTERN = re.compile(r"^\d{2}/[a-z]{2,5}\d{2}/\d{1,4}$")
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'\-]{1,59}$")
GENDERS = ["Male", "Female"]
DATE_FORMAT = "%Y-%m-%d"


# ---------------------------------------------------------------- validators
def validate_student_id(raw):
    """Return the ID in lowercase, or raise ValueError if the format is wrong."""
    student_id = raw.strip().lower()
    if not STUDENT_ID_PATTERN.match(student_id):
        raise ValueError(
            "Student ID must look like year/deptnum/id, e.g. 24/sci01/157."
        )
    return student_id


def validate_name(raw):
    """Return a tidy full name, or raise ValueError."""
    name = " ".join(raw.split())
    if not NAME_PATTERN.match(name):
        raise ValueError(
            "Name must be 2-60 characters (letters, spaces, . ' - only)."
        )
    return name.title()


def validate_dob(raw):
    """Return the date of birth as YYYY-MM-DD, or raise ValueError."""
    try:
        dob = datetime.strptime(raw.strip(), DATE_FORMAT).date()
    except ValueError:
        raise ValueError("Date of birth must be YYYY-MM-DD, e.g. 2004-05-17.")
    if dob >= date.today():
        raise ValueError("Date of birth must be in the past.")
    return dob.isoformat()


# --------------------------------------------------------------------- class
class Student:
    """A student and the scores recorded for them.

    scores looks like:
        {"CSC 301": {"score": 72.0, "date_entered": "2026-11-13 10:42"}, ...}
    """

    def __init__(self, student_id, full_name, department, level,
                 gender, date_of_birth, scores=None):
        self.student_id = student_id
        self.full_name = full_name
        self.department = department
        self.level = level
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.scores = scores if scores is not None else {}

    # -- conversion to / from plain dictionaries (for JSON) ------------------
    def to_dict(self):
        return {
            "student_id": self.student_id,
            "full_name": self.full_name,
            "department": self.department,
            "level": self.level,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth,
            "scores": self.scores,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["student_id"],
            data["full_name"],
            data["department"],
            int(data["level"]),
            data["gender"],
            data["date_of_birth"],
            data.get("scores", {}),
        )

    # -- courses and scores --------------------------------------------------
    def required_courses(self):
        """Return {code: title} of the courses this student must take."""
        return courses.get_courses(self.department, self.level)

    def set_score(self, course_code, score):
        """Record or update a score and stamp the date it was entered."""
        if course_code not in self.required_courses():
            raise ValueError(f"{course_code} is not one of this student's courses.")
        self.scores[course_code] = {
            "score": results.validate_score(score),
            "date_entered": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    def missing_courses(self):
        return [code for code in self.required_courses() if code not in self.scores]

    @property
    def is_complete(self):
        return not self.missing_courses()

    @property
    def total(self):
        return results.calculate_total(self.scores)

    @property
    def average(self):
        return results.calculate_average(self.scores)

    @property
    def grade(self):
        if not self.scores:
            return "N/A"
        return results.assign_grade(self.average)

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"
