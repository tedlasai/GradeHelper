import pandas as pd


def merge_csv(csv1, csv2, output_file):
    data1 = pd.read_csv(csv1)
    data2 = pd.read_csv(csv2)
    output = pd.merge(data1, data2, on=["First name", "Surname", "ID number", "Feedback"])
    output.to_csv(output_file, index=False)


merge_csv("FinalGrades.csv", "FinalGrades1.csv", "Final_grades_merged.csv")
