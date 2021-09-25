import os
import shutil
import tokenize
from bisect import bisect_left

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QMessageBox

import constants

for file in sorted(os.listdir(constants.LAB_DIRECTORY)):
    print(file)

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
        self.gradedStudentDirectories = [False] * len(
            self.studentDirectories)  # create a list of equal length as student directories that tracks if we have viewed it
        self.currentStudentGradedIndex = 0
        self.currentStudentDirectory = ""
        self.currentStudentGradesSubmitted = False
        self.programStarted = True  # just a flag when we start program

        self.usernameLayoutText = QLabel("Student Username: ", self)
        self.usernameLayoutTextSetBox = QLineEdit(self)
        self.usernameLayoutTextSetBox.setText("0")

        self.usernameLayout = QHBoxLayout(self)
        self.usernameLayout.addWidget(self.usernameLayoutText)
        self.usernameLayout.addWidget(self.usernameLayoutTextSetBox)

        self.idLayoutText = QLabel("Student ID: ", self)
        self.idLayoutTextSetBox = QLineEdit(self)
        self.idLayoutTextSetBox.setText("0")

        self.idLayout = QHBoxLayout(self)
        self.idLayout.addWidget(self.idLayoutText)
        self.idLayout.addWidget(self.idLayoutTextSetBox)

        self.gradeLayouts = []
        self.gradeLayoutSetBoxes = []
        for i in range(constants.NUM_GRADES):
            gradeLayoutText = QLabel("Grade {}: ".format(i + 1), self)
            gradeLayoutTextSetBox = QLineEdit(self)
            gradeLayoutTextSetBox.setText("0")
            self.gradeLayoutSetBoxes.append(gradeLayoutTextSetBox)

            gradeLayout = QHBoxLayout(self)
            gradeLayout.addWidget(gradeLayoutText)
            gradeLayout.addWidget(gradeLayoutTextSetBox)

            self.gradeLayouts.append(gradeLayout)

        self.submitButton = QPushButton('Submit Grades', self)
        self.nextButton = QPushButton('Next Student', self)
        self.compileButton = QPushButton('Compile Report', self)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addLayout(self.usernameLayout)
        self.verticalLayout.addLayout(self.idLayout)

        for layout in self.gradeLayouts:
            self.verticalLayout.addLayout(layout)
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
        columnNames = ["Student ID"]

        # build up a pandas dataframe (NEEDS WORK)
        data = {'Student ID': [self.idLayoutTextSetBox.text()]}
        for i, layout in enumerate(self.gradeLayoutSetBoxes):
            columnName = "Grade {}".format(i + 1)
            data[columnName] = [self.gradeLayoutSetBoxes[i].text()]
            columnNames.append(columnName)

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

            self.currentStudentGradedIndex = binarySearch(self.studentDirectories, nextUngradedStudent)
            self.loadStudentInfo(nextUngradedStudent)
            self.loadDirectoryWithStudentFiles(nextUngradedStudent)
            self.clearGrades()
        else:
            createMessagePopUpBox("Grades have not been submitted yet")
        self.programStarted = False

    # load all info into form for current student
    def loadStudentInfo(self, studentUsername):
        def findStudentID(text):
            head = text.rstrip('0123456789')
            tail = text[len(head):]
            return tail

        if not studentUsername:
            createMessagePopUpBox("Could not find next student")

        filePath = os.path.join(constants.LAB_DIRECTORY, studentUsername,
                                constants.FILE_NAME)
        file = open(filePath, "rb")
        commentWithStudentID = None
        for tokenType, token, start, end, line in tokenize.tokenize(file.readline):
            if tokenType == tokenize.COMMENT and "id" in token.lower() and "student" in token.lower():
                commentWithStudentID = token

        studentID = findStudentID(commentWithStudentID)

        self.usernameLayoutTextSetBox.setText(studentUsername)
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
        print("CLEAR GRADES")

    # function will run through all directories in self.studentDirectories load the csvs and output a final csv in the eclass format
    def compileReport(self):
        print("FUNCTION WILL DO STUFF SOON")


app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec_()
