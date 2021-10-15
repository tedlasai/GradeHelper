import os
import unittest

import pandas as pd

from grade_helper_ops.submit_grades import submit_grades


class TestSubmitGrades(unittest.TestCase):

    def test_submit_grades_valid_input(self):
        path = os.path.join("test_lab")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        column_names = ["First name", "Surname", "ID number", "Grade", "Feedback"]
        row_values = ["Java", "Python", "21567", "50", "Try harder!"]
        csv_path = os.path.join(path, "student.csv")
        submit_grades(csv_path, column_names, row_values)
        data_frame = pd.read_csv(csv_path)

        for column in range(1, len(data_frame.columns)):
            self.assertEqual(data_frame.columns[column], column_names[column - 1])
        for row, col in zip(row_values, column_names):
            self.assertEqual(str(data_frame.iloc[0][col]), row)


if __name__ == '__main__':
    unittest.main()
