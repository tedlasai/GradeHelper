import os
import constants
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QWidget, QVBoxLayout, QPushButton
import pandas as pd

for file in sorted(os.listdir(constants.LAB_DIRECTORY)):
    print(file)

#create working folder to copy files that I'm viewing to
if not os.path.exists(constants.WORKING_DIRECTORY):
    os.makedirs(constants.WORKING_DIRECTORY, exist_ok=True)

#pyqt window
class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.studentDirectories = os.listdir(constants.LAB_DIRECTORY)
        self.gradedStudentDirectories = [False] * len(self.studentDirectories) #create a list of equal length as student directories that tracks if we have viewed it
        self.currentStudentGradedIndex = 0
        self.currentStudentDirectory = ""
        self.currentStudentGradesSubmitted = False
        self.programStarted = True #just a flag when we start program

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

    #this function should write out grades to each folder in a csv file per student
    def submitGrades(self):
        #used to specify Order of output
        columnNames = ["Student ID"]

        #build up a pandas dataframe (NEEDS WORK)
        data = {'Student ID':  [self.idLayoutTextSetBox.text()]}
        for i, layout in enumerate(self.gradeLayoutSetBoxes):
            columnName = "Grade {}".format(i+1)
            data[columnName] = [self.gradeLayoutSetBoxes[i].text()]
            columnNames.append(columnName)


        df = pd.DataFrame(data)
        gradeHelperCSVPath = os.path.join(constants.LAB_DIRECTORY, self.studentDirectories[self.currentStudentGradedIndex], "gradeHelper.csv")


        df.to_csv(gradeHelperCSVPath, columns = columnNames)

        self.currentStudentGradesSubmitted = True


    #this function should get information for next student in the list that doesn't have a CSV already stored in the folder
    #if there is a grade csv already in the folder then load someone else

    def loadNextStudent(self):
        print("Write out csv for blah")
        print("Grade 0 can be asccessed with", self.gradeLayoutSetBoxes[0].text())



        #this function shouldn't go load new student info
        #unless submit was clicked or we are just loading into the program(first person laoding)
        if(self.currentStudentGradesSubmitted or self.programStarted):
            #find the next ungraded student index
            nextUngradedStudent = self.currentStudentGradedIndex

            #find next ungraded student ID
            while nextUngradedStudent <= len(self.studentDirectories):
                #build up the path for where gradeHelper.csv should exist
                gradeHelperCSVPath = os.path.join(constants.LAB_DIRECTORY, self.studentDirectories[nextUngradedStudent], "gradeHelper.csv")
                if os.path.exists(gradeHelperCSVPath):
                    nextUngradedStudent+=1
                else:
                    break

            self.currentStudentGradedIndex = nextUngradedStudent
            self.loadStudentInfo()
            self.clearGrades()
        else:
            print("NOT SUBMITTED YET") #THIS SHOULD GO TO PYQT CONSOLE SOMEWHERE - WORK ON THIS

        self.programStarted = False

    #load all info into form for current student
    #WORK ON THIS
    def loadStudentInfo(self):
        currentUsername = self.studentDirectories[self.currentStudentGradedIndex]
        self.usernameLayoutTextSetBox.setText(currentUsername)

        #copy the python files in directory to working directory(sometimes students have helper files so copy all files)
        #overwrite similiar named files in working directory

        #look for file that matches "lab4.py"
        #this is in constants.FILE_NAME
        #read info from it

    #function to clear grades in the textboxes
    def clearGrades(self):
        print("CLEAR GRADES")


    #function will run through all directories in self.studentDirectories load the csvs and output a final csv in the eclass format
    def compileReport(self):
        print("FUNCTION WILL DO STUFF SOON")




app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec_()

