# Student Result Management System

A menu-driven Python application for managing university student records and results. Built for the New Horizon *Introduction to Python Programming* practical project.

## Features

- **Students:** add, view, search (by ID or name), update and delete.
- **Scores:** record and update scores for every course a student takes; totals, averages and letter grades are calculated automatically; each score is stamped with the date and time it was entered.
- **Reports:** individual report card, list of all results sorted by average or name, class statistics (highest, lowest and class average, plus grade distribution), and a text report saved to a file.
- **Persistence:** data is saved to `data/students.json` after every change and loaded when the program starts. A missing or damaged file is handled gracefully.

## How to run

Requires Python 3.9 or newer. No extra packages are needed.

```bash
git clone https://github.com/<your-username>/student-result-system.git
cd student-result-system
python main.py
```

On Windows, use `python main.py`; on macOS/Linux you may need `python3 main.py`.

## Student ID format

`year/deptnum/id`, for example `24/sci01/157`. The format is checked with a regular expression, and IDs are stored in lowercase.

## Courses

Each student's courses depend on their **department** and **level**, plus general courses taken by everyone:

| Department | Level | Courses |
| --- | --- | --- |
| Computer Science | 300L | CSC 301, CSC 303, CSC 305, CSC 307 |
| Engineering | 300L | ENG 301, ENG 303, ENG 305, ENG 307 |
| All students | 300L | GST 205, AFE 301 |

To add a department, level or course, edit `courses.py`. No other file needs to change.

## Grading scale

| Average | Grade |
| --- | --- |
| 70 – 100 | A |
| 60 – 69 | B |
| 50 – 59 | C |
| 45 – 49 | D |
| 40 – 44 | E |
| 0 – 39 | F |

The scale is defined in `results.py` (`GRADE_SCALE`).

## Project structure

```
student_result_system/
├── main.py       # Entry point and main menu
├── student.py    # Student class and input validation
├── results.py    # Score validation, totals, averages, grades, class statistics
├── courses.py    # Course catalogue (departments, levels, general courses)
├── storage.py    # Load and save data as JSON
├── reports.py    # Report card, tables, statistics, saving text reports
├── data/
│   └── students.json   # Created automatically on first save
├── reports/            # Saved text reports (created automatically)
└── README.md
```

## Python concepts used

- Variables, data types and type conversion (`float()`, `int()`, string formatting)
- Flow control: `if/elif/else`, `for` and `while` loops
- Lists, tuples (the grade scale) and dictionaries (students, scores, course catalogue)
- Functions with parameters and return values
- Sorting with `sorted()` and `lambda` keys
- Exception handling with `try / except / else / finally`
- File handling: reading and writing JSON
- Modules: the code is split across several `.py` files
- Object-oriented programming: the `Student` class with methods, properties and a class method
- Dates and times: each score records when it was entered
- Standard library: `json`, `os`, `datetime`, `re`
- Regular expressions for validating Student IDs and names
