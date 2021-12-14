import os
import random
import shutil
import string
import unittest
import uuid

import pandas as pd

import constants
from grade_helper_ops.compile_grade_report import compile_grade_report


class TestCompileGradeReport(unittest.TestCase):

    def test_compile_grade_report_all_students_graded(self):
        path = os.path.join("test_lab")
        students_amt = 10
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        column_names = ["First name", "Surname", "ID number", "Grade", "Feedback"]
        for i in range(students_amt):
            row_values = [''.join(random.choices(string.ascii_uppercase, k=i)),
                          ''.join(random.choices(string.ascii_uppercase, k=i)), uuid.uuid4(), f"{i}", "Try harder!"]
            student_path = os.path.join(path, f"student_{i}")
            os.makedirs(student_path, exist_ok=True)
            csv_path = os.path.join(student_path, constants.CSV_FILE_NAME)

            csv_data = {}
            for row, col in zip(row_values, column_names):
                csv_data[col] = [row]
            data_frame = pd.DataFrame(csv_data)
            data_frame.to_csv(csv_path, columns=column_names)

        response = compile_grade_report(os.listdir(path), path, os.path.join(path, constants.FINAL_GRADE_REPORT_PATH),
                                        column_names)
        self.assertFalse(response["error"])
        shutil.rmtree(path)


if __name__ == '__main__':
    unittest.main()
