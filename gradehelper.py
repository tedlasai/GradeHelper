import os
from bisect import bisect_left

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QMessageBox

import constants
from grade_helper_ops.compile_grade_report import compile_grade_report
from grade_helper_ops.load_next_student import load_next_student
from grade_helper_ops.submit_grades import submit_grades

# create working folder to copy files that I'm viewing to
if not os.path.exists(constants.WORKING_DIRECTORY):
    os.makedirs(constants.WORKING_DIRECTORY, exist_ok=True)


def create_message_pop_up_box(text):
    msg = QMessageBox()
    msg.setWindowTitle("Error")
    msg.setText(text)
    msg.setIcon(QMessageBox.Critical)
    msg.exec_()


# pyqt window
class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.studentDirectories = sorted(os.listdir(constants.LAB_DIRECTORY))
        self.currentStudentGradedIndex = 0

        self.currentStudentGradesSubmitted = False
        self.programStarted = True  # just a flag when we start program

        self.studentNameLayoutText = QLabel("Student Name: ")
        self.studentNameLayoutTextSetBox = QLineEdit()
        self.studentNameLayoutTextSetBox.setText("")

        self.studentNameLayout = QHBoxLayout()
        self.studentNameLayout.addWidget(self.studentNameLayoutText)
        self.studentNameLayout.addWidget(self.studentNameLayoutTextSetBox)

        self.usernameLayoutText = QLabel("Student Username: ")
        self.usernameLayoutTextSetBox = QLineEdit()
        self.usernameLayoutTextSetBox.setText("")

        self.usernameLayout = QHBoxLayout()
        self.usernameLayout.addWidget(self.usernameLayoutText)
        self.usernameLayout.addWidget(self.usernameLayoutTextSetBox)

        self.idLayoutText = QLabel("Student ID: ")
        self.idLayoutTextSetBox = QLineEdit()
        self.idLayoutTextSetBox.setText("0")

        self.idLayout = QHBoxLayout()
        self.idLayout.addWidget(self.idLayoutText)
        self.idLayout.addWidget(self.idLayoutTextSetBox)

        self.feedbackLayoutText = QLabel("Feedback: ")
        self.feedbackLayoutTextSetBox = QLineEdit()
        self.feedbackLayoutTextSetBox.setText("")

        self.feedbackLayout = QHBoxLayout()
        self.feedbackLayout.addWidget(self.feedbackLayoutText)
        self.feedbackLayout.addWidget(self.feedbackLayoutTextSetBox)

        self.gradeLayoutText = QLabel("Grade (0 - 10): ")
        self.gradeLayoutTextSetBox = QLineEdit(self)
        self.gradeLayoutTextSetBox.setValidator(QIntValidator())
        self.gradeLayoutTextSetBox.setText("0")

        self.gradeLayout = QHBoxLayout()
        self.gradeLayout.addWidget(self.gradeLayoutText)
        self.gradeLayout.addWidget(self.gradeLayoutTextSetBox)

        self.submitButton = QPushButton('Submit Grades')
        self.nextButton = QPushButton('Next Student')
        self.compileButton = QPushButton('Compile Report')

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.addLayout(self.studentNameLayout)
        self.verticalLayout.addLayout(self.usernameLayout)
        self.verticalLayout.addLayout(self.idLayout)
        self.verticalLayout.addLayout(self.feedbackLayout)
        self.verticalLayout.addLayout(self.gradeLayout)

        self.verticalLayout.addWidget(self.submitButton)
        self.verticalLayout.addWidget(self.nextButton)
        self.verticalLayout.addWidget(self.compileButton)

        self.submitButton.clicked.connect(self.submit_grades)
        self.nextButton.clicked.connect(self.load_next_student)
        self.compileButton.clicked.connect(self.compile_report)

        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(self.verticalLayout)

        self.load_next_student()

    # this function should write out grades to each folder in a csv file per student
    def submit_grades(self):
        scale_factor = 10
        student_grade_path = os.path.join(constants.LAB_DIRECTORY,
                                          self.studentDirectories[self.currentStudentGradedIndex],
                                          constants.CSV_FILE_NAME)
        columns = ["First name", "Surname", "ID number", "Grade", "Feedback"]
        first_name, last_name = "", ""
        if self.studentNameLayoutTextSetBox.text():
            first_name, last_name = self.studentNameLayoutTextSetBox.text().split(" ", 1)

        row_values = [
            first_name,
            last_name,
            self.idLayoutTextSetBox.text(),
            int(self.gradeLayoutTextSetBox.text()) * scale_factor,
            self.feedbackLayoutTextSetBox.text()
        ]
        try:
            submit_grades(student_grade_path, columns, row_values)
        except ValueError as e:
            create_message_pop_up_box(e)

        self.currentStudentGradesSubmitted = True
        self.clear_fields()

    # Gets information for next student in the list that doesn't have a CSV already stored in the folder and replaces
    # working directory with next student's files
    def load_next_student(self):
        def binary_search(students, student_name):
            i = bisect_left(students, student_name)
            if i != len(students) and students[i] == student_name:
                return i
            else:
                return -1
        if self.currentStudentGradesSubmitted or self.programStarted:
            try:
                student = load_next_student(self.studentDirectories)
                if not student["error_message"]:
                    self.currentStudentGradedIndex = binary_search(self.studentDirectories, student["username"])
                    self.usernameLayoutTextSetBox.setText(student["username"])
                    self.studentNameLayoutTextSetBox.setText(student["name"])
                    self.idLayoutTextSetBox.setText(student["id"])
                else:
                    create_message_pop_up_box("\n".join(student["error_message"]))
            except ValueError as e:
                create_message_pop_up_box(f"{e}")

        else:
            create_message_pop_up_box("Grades have not been submitted yet")
        self.programStarted = False

    # function to clear fields in the textboxes
    def clear_fields(self):
        self.feedbackLayoutTextSetBox.setText("")
        self.gradeLayoutTextSetBox.setText("0")

    # function will run through all directories in self.studentDirectories load the csvs and output a final csv in
    # the eclass format
    def compile_report(self):
        response = compile_grade_report(self.studentDirectories, constants.LAB_DIRECTORY,
                                        constants.FINAL_GRADE_REPORT_PATH)
        if response["error"]:
            create_message_pop_up_box(response["error"])


app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec_()
