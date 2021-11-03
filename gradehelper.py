import os
from bisect import bisect_left

from PyQt5 import QtWidgets
from PyQt5.QtGui import QDoubleValidator
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
        self._student_directories = sorted(os.listdir(constants.LAB_DIRECTORY))
        self._current_student_graded_index = 0

        self._current_student_grades_submitted = False
        self._program_started = True  # just a flag when we start program

        self._student_name_layout_text = QLabel("Student Name: ")
        self._student_name_layout_text_set_box = QLineEdit()
        self._student_name_layout_text_set_box.setText("")

        self._student_name_layout = QHBoxLayout()
        self._student_name_layout.addWidget(self._student_name_layout_text)
        self._student_name_layout.addWidget(self._student_name_layout_text_set_box)

        self._username_layout_text = QLabel("Student Username: ")
        self._username_layout_text_set_box = QLineEdit()
        self._username_layout_text_set_box.setText("")

        self._username_layout = QHBoxLayout()
        self._username_layout.addWidget(self._username_layout_text)
        self._username_layout.addWidget(self._username_layout_text_set_box)

        self._id_layout_text = QLabel("Student ID: ")
        self._id_layout_text_set_box = QLineEdit()
        self._id_layout_text_set_box.setText("0")

        self._id_layout = QHBoxLayout()
        self._id_layout.addWidget(self._id_layout_text)
        self._id_layout.addWidget(self._id_layout_text_set_box)

        self._feedback_layout_text = QLabel("Feedback: ")
        self._feedback_layout_text_set_box = QLineEdit()
        self._feedback_layout_text_set_box.setText("")

        self._feedback_layout = QHBoxLayout()
        self._feedback_layout.addWidget(self._feedback_layout_text)
        self._feedback_layout.addWidget(self._feedback_layout_text_set_box)

        self._grade_layout_text = QLabel("Grade (0 - 10): ")
        self._grade_layout_text_set_box = QLineEdit(self)
        self._grade_layout_text_set_box.setValidator(QDoubleValidator(0, 10, 1))
        self._grade_layout_text_set_box.setText("0")

        self._grade_layout = QHBoxLayout()
        self._grade_layout.addWidget(self._grade_layout_text)
        self._grade_layout.addWidget(self._grade_layout_text_set_box)

        submitButton = QPushButton('Submit Grades')
        nextButton = QPushButton('Next Student')
        compileButton = QPushButton('Compile Report')

        verticalLayout = QVBoxLayout()
        verticalLayout.addLayout(self._student_name_layout)
        verticalLayout.addLayout(self._username_layout)
        verticalLayout.addLayout(self._id_layout)
        verticalLayout.addLayout(self._feedback_layout)
        verticalLayout.addLayout(self._grade_layout)

        verticalLayout.addWidget(submitButton)
        verticalLayout.addWidget(nextButton)
        verticalLayout.addWidget(compileButton)

        submitButton.clicked.connect(self.submit_grades)
        nextButton.clicked.connect(self.load_next_student)
        compileButton.clicked.connect(self.compile_report)

        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(verticalLayout)

        self.load_next_student()

    # this function should write out grades to each folder in a csv file per student
    def submit_grades(self):
        scale_factor = 10
        student_grade_path = os.path.join(constants.LAB_DIRECTORY,
                                          self._student_directories[self._current_student_graded_index],
                                          constants.CSV_FILE_NAME)
        columns = ["First name", "Surname", "ID number", "Grade", "Feedback"]
        first_name, last_name = "", ""
        if self._student_name_layout_text_set_box.text():
            try:
                first_name, last_name = self._student_name_layout_text_set_box.text().split(" ", 1)
            except ValueError:
                create_message_pop_up_box(
                    "Could not find either first or last name, please check student files or input random last "
                    "name (e.g John -> John Smith)"
                )

        row_values = [
            first_name,
            last_name,
            self._id_layout_text_set_box.text(),
            int(float(self._grade_layout_text_set_box.text()) * scale_factor),
            self._feedback_layout_text_set_box.text()
        ]
        try:
            submit_grades(student_grade_path, columns, row_values)
        except ValueError as e:
            create_message_pop_up_box(e)

        self._current_student_grades_submitted = True
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

        if self._current_student_grades_submitted or self._program_started:
            try:
                student = load_next_student(self._student_directories)
                if not student["error_message"]:
                    self._current_student_graded_index = binary_search(self._student_directories, student["username"])
                    self._username_layout_text_set_box.setText(student["username"])
                    self._student_name_layout_text_set_box.setText(student["name"])
                    self._id_layout_text_set_box.setText(student["id"])
                else:
                    create_message_pop_up_box("\n".join(student["error_message"]))
            except ValueError as e:
                create_message_pop_up_box(f"{e}")

        else:
            create_message_pop_up_box("Grades have not been submitted yet")
        self._program_started = False

    # function to clear fields in the textboxes
    def clear_fields(self):
        self._feedback_layout_text_set_box.setText("")
        self._grade_layout_text_set_box.setText("0")

    # function will run through all directories in self.studentDirectories load the csvs and output a final csv in
    # the eclass format
    def compile_report(self):
        response = compile_grade_report(self._student_directories, constants.LAB_DIRECTORY,
                                        constants.FINAL_GRADE_REPORT_PATH)
        if response["error"]:
            create_message_pop_up_box(response["error"])


app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec_()
