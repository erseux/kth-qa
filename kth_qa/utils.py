import json
import os

def touch_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def get_courses():
    try:
        with open('kth_qa/courses.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        try:
            with open('courses.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError('courses.json not found')
    courses = data.get('courses')
    return courses