# GradeHelper

## Pay close attention to comments in student files

Usually an error would pop up when a file or comment is improperly formatted but here are some examples to be on the
lookout

1. Cannot handle improperly handled file names (e.g Lab4, llab4, etc...)
1. Cannot handle improperly formatted comments since it splits comments based on a ":" separator value (e.g Class :-,
   Student: ID:, Student ID: xxx-yyy-zzz)

## How to use

- Run `gradehelper.py` (Initial run will install dependencies)
    - Alternatively run `pip install -r requirements.txt` to install dependencies

- The program will attempt to load the student's information as shown below

![image](https://user-images.githubusercontent.com/41768142/142752784-93b7fd9a-bb5f-4476-8e38-2341bcb29aaa.png)

- Input the corresponding grade and feedback. The WD directory will have all of the current student's lab files. You can
  use this directory to check the student's files and run them

- Press the `Submit Grades` button to save the student's grades
- Press the `Next Student` button to go to the next student
- Press the `Compile Report` button when you are finished grading all students
    - It will output a `FinalGrades.csv` file which you can then use for inputting grades

# How to use (Alt)

- Run the following commands

```
docker build -t python-gradehelper .
docker run -e "DISPLAY=$DISPLAY" -v "$HOME/.Xauthority:/root/.Xauthority:ro" --network host python-gradehelper
```
