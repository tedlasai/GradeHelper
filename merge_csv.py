import pandas as pd


def merge_csv(csv1, csv2):
    return pd.merge(csv1, csv2, on=["First name", "Surname", "ID number"])


def merge_feedback_columns(df, columns):
    feedback_x, feedback_y = columns
    df["Feedback"] = df[feedback_x].map(str) + " And " + df[feedback_y].map(str)
    df = df.drop(feedback_x, axis=1)
    df = df.drop(feedback_y, axis=1)
    return df


data1 = pd.read_csv("FinalGrades.csv")
data2 = pd.read_csv("FinalGrades1.csv")
output = merge_csv(data1, data2)
output = merge_feedback_columns(output, ["Feedback_x", "Feedback_y"])
output.to_csv("Final_grades_merged.csv", index=False)
