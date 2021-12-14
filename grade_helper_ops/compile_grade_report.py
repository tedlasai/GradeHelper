import csv
import os

import pandas as pd

import constants


def compile_grade_report(student_directories, src_path, final_grade_report_path, columns):
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
                    if len(columns) != len(reader):
                        error_msg = "Discrepancy between columns and column values"
                        break
                    student_info = {}
                    for i in range(len(columns)):
                        student_info[columns[i]] = reader[i]
                    class_grades.append(student_info)
            except Exception as e:
                error_msg = str(e)
    if grade_report_files != len(student_directories):
        error_msg = "Discrepancy between amount of students graded and amount of students in folder." \
                    " There exists a possibility that a student might not have been graded"
    df = pd.DataFrame(class_grades).set_index("First name")
    df.to_csv(final_grade_report_path)

    return {
        "error": error_msg
    }
