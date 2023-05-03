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

if __name__ == '__main__':
    courses = get_courses()
    print(len(courses))
    new_courses = {}
    for c in courses.keys():
        if c[:2] in ['ME', 'DA', 'DM', 'DT', 'DH', 'MF', "EI"]:
            new_courses[c] = courses[c]

    print(len(new_courses))