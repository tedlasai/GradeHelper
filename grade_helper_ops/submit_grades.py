import pandas as pd


def submit_grades(student_grade_csv_path: str, column_names: list, row_values: list):
    if not column_names or not row_values or len(column_names) != len(row_values):
        raise ValueError("Columns and rows must not be empty and equal in length")

    csv_data = {}
    for row, col in zip(row_values, column_names):
        csv_data[col] = [row]
    data_frame = pd.DataFrame(csv_data)
    data_frame.to_csv(student_grade_csv_path, columns=column_names)
