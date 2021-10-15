import csv
import os

import pandas as pd

import constants


def compile_grade_report(student_directories, src_path, final_grade_report_path):
    class_grades = []
    grade_report_files = 0
    error_msg = ''
    for student in student_directories:
        student_grade_path = os.path.join(src_path, student, constants.CSV_FILE_NAME)
        if os.path.exists(student_grade_path):
            grade_report_files += 1
            try:
                with open(student_grade_path) as f:
                    reader = list(csv.reader(f, delimiter=','))[1:][0][1:]
                    studentInfo = {
                        "First name": reader[0],
                        "Surname": reader[1],
                        "ID number": reader[2],
                        "Grade": reader[3],
                        "Feedback": reader[4]
                    }
                    class_grades.append(studentInfo)
            except Exception as e:
                error_msg = str(e)
    print(class_grades)
    if grade_report_files != len(student_directories):
        error_msg = "Discrepancy between amount of students graded and amount of students in folder." \
                    " There exists a possibility that a student might not have been graded"
    df = pd.DataFrame(class_grades).set_index("First name")
    df.to_csv(final_grade_report_path)

    return {
        "error": error_msg
    }
