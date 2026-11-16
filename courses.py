"""Course catalogue.


Structure:
    DEPARTMENT_COURSES[department][level] = {course_code: course_title}
    GENERAL_COURSES[level]                = {course_code: course_title}
                                            (taken by every student at that level)
"""

MIN_COURSES = 5  # the brief requires at least five subjects per student

# Courses taken by ALL students at a given level, whatever their department.
GENERAL_COURSES = {
    300: {
        "GST 205": "General Studies",
        "AFE 301": "Entrepreneurship",
    },
}

# Department-specific courses. Titles are placeholders - replace them with
# your university's real course titles.
DEPARTMENT_COURSES = {
    "Computer Science": {
        300: {
            "CSC 301": "Operating Systems",
            "CSC 303": "Database Systems",
            "CSC 305": "Software Engineering",
            "CSC 307": "Computer Networks",
        },
    },
    "Engineering": {
        300: {
            "ENG 301": "Engineering Mathematics III",
            "ENG 303": "Thermodynamics",
            "ENG 305": "Fluid Mechanics",
            "ENG 307": "Engineering Design",
        },
    },
}


def get_departments():
    """Return the list of department names, alphabetically."""
    return sorted(DEPARTMENT_COURSES)


def get_levels(department):
    """Return the levels (e.g. [300]) available for a department."""
    return sorted(DEPARTMENT_COURSES.get(department, {}))


def get_courses(department, level):
    """Return {code: title} of every course a student must take.

    Department courses come first, followed by the general courses.
    """
    own = DEPARTMENT_COURSES.get(department, {}).get(level, {})
    general = GENERAL_COURSES.get(level, {})
    return {**own, **general}


def check_catalogue():
    """Return a list of warnings about the catalogue (empty if all is well)."""
    warnings = []
    for department, levels in DEPARTMENT_COURSES.items():
        for level in levels:
            count = len(get_courses(department, level))
            if count < MIN_COURSES:
                warnings.append(
                    f"{department} {level}L has only {count} courses "
                    f"(minimum is {MIN_COURSES})."
                )
    return warnings
