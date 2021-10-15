import csv
import os
import shutil
import tokenize
from bisect import bisect_left

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QMessageBox

import constants

# create working folder to copy files that I'm viewing to
if not os.path.exists(constants.WORKING_DIRECTORY):
    os.makedirs(constants.WORKING_DIRECTORY, exist_ok=True)


# https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
def deleteDirectoryContent(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            createMessagePopUpBox(f"Failed to delete {file_path}. Reason:{e}. Check student directory")


def findStudentID(text):
    head = text.rstrip('0123456789')
    tail = text[len(head):]
    return tail


def createMessagePopUpBox(text):
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
        # create a list of equal length as student directories that tracks if we have viewed it
        self.gradedStudentDirectories = [False] * len(self.studentDirectories)
        self.currentStudentGradedIndex = 0
        self.currentStudentDirectory = ""
        self.currentStudentGradesSubmitted = False
        self.programStarted = True  # just a flag when we start program

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
        self.verticalLayout.addLayout(self.usernameLayout)
        self.verticalLayout.addLayout(self.idLayout)
        self.verticalLayout.addLayout(self.feedbackLayout)
        self.verticalLayout.addLayout(self.gradeLayout)

        self.verticalLayout.addWidget(self.submitButton)
        self.verticalLayout.addWidget(self.nextButton)
        self.verticalLayout.addWidget(self.compileButton)

        self.submitButton.clicked.connect(self.submitGrades)
        self.nextButton.clicked.connect(self.loadNextStudent)
        self.compileButton.clicked.connect(self.compileReport)

        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(self.verticalLayout)

        self.loadNextStudent()

    # this function should write out grades to each folder in a csv file per student
    def submitGrades(self):
        # used to specify Order of output
        scaleFactor = 10
        columnNames = ["Student ID", "Grade", "Feedback"]
        data = {'Student ID': [self.idLayoutTextSetBox.text()], "Grade": [
            int(self.gradeLayoutTextSetBox.text()) * scaleFactor],
                "Feedback": [self.feedbackLayoutTextSetBox.text()]}

        df = pd.DataFrame(data)
        gradeHelperCSVPath = os.path.join(constants.LAB_DIRECTORY,
                                          self.studentDirectories[self.currentStudentGradedIndex], "gradeHelper.csv")

        df.to_csv(gradeHelperCSVPath, columns=columnNames)

        self.currentStudentGradesSubmitted = True

    # Gets information for next student in the list that doesn't have a CSV already stored in the folder and replaces
    # working directory with next student's files
    def loadNextStudent(self):
        def binarySearch(students, studentName):
            i = bisect_left(students, studentName)
            if i != len(students) and students[i] == studentName:
                return i
            else:
                return -1

        if self.currentStudentGradesSubmitted or self.programStarted:
            nextUngradedStudent = next(filter(lambda studentDirectory:
                                              not os.path.exists(os.path.join(constants.LAB_DIRECTORY, studentDirectory,
                                                                              "gradeHelper.csv")),
                                              self.studentDirectories), None)
            if not nextUngradedStudent:
                self.gradedStudentDirectories[0:len(self.studentDirectories)] = [True] * len(self.studentDirectories)
                createMessagePopUpBox("Done grading all students. You can compile the report now")
                return

            self.currentStudentGradedIndex = binarySearch(self.studentDirectories, nextUngradedStudent)
            # Done so list of bools is updated on startup
            self.gradedStudentDirectories[0:self.currentStudentGradedIndex] = [True] * self.currentStudentGradedIndex
            self.loadStudentInfo(nextUngradedStudent)
            self.loadDirectoryWithStudentFiles(nextUngradedStudent)
            self.clearGrades()
        else:
            createMessagePopUpBox("Grades have not been submitted yet")
        self.programStarted = False

    # load all info into form for current student
    def loadStudentInfo(self, studentUsername):
        if not studentUsername:
            createMessagePopUpBox("Could not find next student")
            return

        self.usernameLayoutTextSetBox.setText(studentUsername)

        if not os.path.exists(os.path.join(constants.LAB_DIRECTORY, studentUsername,
                                           constants.FILE_NAME)):
            createMessagePopUpBox(f"Could not find student {studentUsername}'s files")
            self.idLayoutTextSetBox.setText("0")
            return

        filePath = os.path.join(constants.LAB_DIRECTORY, studentUsername,
                                constants.FILE_NAME)
        file = open(filePath, "rb")
        commentWithStudentID = None
        for tokenType, token, start, end, line in tokenize.tokenize(file.readline):
            if tokenType == tokenize.COMMENT and "id" in token.lower() and "student" in token.lower():
                commentWithStudentID = token
        if not commentWithStudentID:
            createMessagePopUpBox(f"Check {studentUsername}'s folder. Could not find student ID")
            return
        studentID = findStudentID(commentWithStudentID)

        self.idLayoutTextSetBox.setText(studentID)

    def loadDirectoryWithStudentFiles(self, studentUsername):
        deleteDirectoryContent(os.path.join(constants.WORKING_DIRECTORY))
        try:
            shutil.copytree(os.path.join(constants.LAB_DIRECTORY, studentUsername),
                            os.path.join(constants.WORKING_DIRECTORY),
                            dirs_exist_ok=True)
        except Exception as e:
            createMessagePopUpBox(
                f"Check the student directory; Could not load student's directory into "
                f"working directory: {constants.WORKING_DIRECTORY}")

    # function to clear grades in the textboxes
    def clearGrades(self):
        self.gradeLayoutTextSetBox.setText("0")

    # function will run through all directories in self.studentDirectories load the csvs and output a final csv in the eclass format
    def compileReport(self):
        classGrades = []
        compiledReportPath = "FinalGrades.csv"
        for i, x in enumerate(self.studentDirectories):
            perStudentCSVPath = os.path.join(constants.LAB_DIRECTORY,
                                             self.studentDirectories[i], "gradeHelper.csv")
            if self.gradedStudentDirectories[i]:
                try:
                    with open(perStudentCSVPath) as f:
                        reader = list(csv.reader(f, delimiter=','))[1:][0][1:]
                        studentInfo = {'studentId': reader[0], "grade": reader[1], "feedback": reader[2]}
                        classGrades.append(studentInfo)
                except Exception as e:
                    createMessagePopUpBox(str(e))

        df = pd.DataFrame(classGrades).set_index('studentId')
        df.to_csv(compiledReportPath)


app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec_()
