import os
import re
import shutil
import tokenize

import constants


def load_next_student(student_directories: list):
    next_ungraded_student = next(
        filter(lambda student_directory:
               not os.path.exists(find_student_file_path(student_directory, constants.CSV_FILE_NAME)),
               student_directories), None)
    if not next_ungraded_student:
        raise ValueError("No students left to grade")

    error_msg = []

    student = load_student_info(next_ungraded_student)
    if student["error_message"]:
        error_msg.append(student['error_message'])

    res = load_working_directory_with_student_files(next_ungraded_student)
    if res["error_message"]:
        error_msg.append(res['error_message'])

    return {
        "username": next_ungraded_student,
        "name": student["name"],
        "id": student["id"],
        "error_message": error_msg
    }


# load all info into form for current student
def load_student_info(student_username):
    error_msg = ''
    student_name = ''
    student_id = ''
    if not student_username:
        error_msg = "Could not find next student"

    if not error_msg:
        student_file_path = find_student_file_path(student_username, constants.FILE_NAME)
        if not os.path.exists(student_file_path):
            error_msg = f"Could not find student {student_username}'s files"
        if not error_msg:
            file = open(student_file_path, "rb")
            comment_types = {}
            for token_type, token, start, end, line in tokenize.tokenize(file.readline):
                if token_type == tokenize.COMMENT:
                    token_lowercase = token.lower()
                    label, *value = token_lowercase.split(":")
                    if label and value:
                        if "student" in label or "name" in label:
                            if "id" in label:
                                comment_types["student_id"] = token
                            elif "name" in label:
                                comment_types["student_name"] = token
                        if "student_name" not in comment_types:
                            if "author" in token_lowercase:
                                comment_types["student_name"] = token
                if "student_name" in comment_types and "student_id" in comment_types:
                    break

            if "student_id" not in comment_types:
                error_msg = f"Check {student_username}'s folder. Could not find student ID"
            elif "student_name" not in comment_types:
                error_msg = f"Check {student_username}'s folder. Could not find student name"

            if not error_msg:
                student_name = find_student_name(comment_types["student_name"])
                student_id = find_student_id(comment_types["student_id"])

    return {
        "name": student_name,
        "id": student_id,
        "error_message": error_msg
    }


def find_student_file_path(student_username, file):
    return os.path.join(constants.LAB_DIRECTORY, student_username,
                        file)


def find_student_name(text):
    return re.search(r"^.+:(.+)$", text).group(1).strip()


def find_student_id(text):
    head = text.rstrip('0123456789')
    tail = text[len(head):]
    return tail


def load_working_directory_with_student_files(student_username):
    delete_directory_content(os.path.join(constants.WORKING_DIRECTORY))
    try:
        student_directory = os.path.join(constants.LAB_DIRECTORY, student_username)
        copy_student_files_to_directory(student_directory, constants.WORKING_DIRECTORY)
    except shutil.Error as e:
        return {
            "error_message": f"Check the student directory; Could not load student's directory into working "
                             f"directory: {constants.WORKING_DIRECTORY}; Reason: {e}"}
    return {
        "error_message": ''
    }


def copy_student_files_to_directory(src, dst):
    shutil.copytree(src, dst, dirs_exist_ok=True)


# https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
def delete_directory_content(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            return {
                "error_message": f"Check the student directory; Could not delete {folder}'s directory; Reason: {e}"
            }
