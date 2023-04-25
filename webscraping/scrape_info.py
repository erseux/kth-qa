import json
from bs4 import BeautifulSoup
import requests
from xml.etree import cElementTree as ET

from tqdm import tqdm

from webscraping.scrape_course import fetch_url, get_url


# skapa lista med alla kurser
# vill lagra url
TOTAL_COURSES = 1257

def handle_xml(xml, content_file):
    xml_tree = ET.fromstring(xml)  
    for elem in xml_tree.iter():
        if(elem.tag and elem.text):
            content_file.write(elem.tag+":"+elem.text+"\n")

def iterate_courses():
    index_url = "https://api.kth.se/api/kopps/v1/courseRounds/2023:1"
    response = requests.get(index_url)
    root = ET.fromstring(response.text)
    for course in root.iter("courseRound"): 
        yield(course)


def scrape_heading(course_code, language, soup=None):
    if soup is None:
        url = get_url(course_code, language)
        html = fetch_url(url)

        soup = BeautifulSoup(html, 'html.parser')

    heading = soup.find('h1', {'id': 'page-heading'})
    return heading.text

def save_courses(limit=None):
    course_codes = []
    for course in iterate_courses():
        course_codes.append(course.get("courseCode"))
    # remove duplicates
    course_codes = list(dict.fromkeys(course_codes))
    courses = {}
    i = 0
    for course_code in tqdm(course_codes):
        if limit and i == limit:
            break
        heading_sv = scrape_heading(course_code, 'sv')
        heading_en = scrape_heading(course_code, 'en')
        courses[course_code] = {
            "sv": heading_sv,
            "en": heading_en,
        }
        i += 1

    with open("kth_qa/courses.json", "w") as f:
        f.write(json.dumps({"courses": courses}, ensure_ascii=False, indent=4))

def wabscrape():  

    file_name = "C:\\Users\\46705\\Documents\\Search_engines\\project_work\\kth-qa\\files\\courses.txt"
    file = open(file_name, "w",encoding='utf-8')
    index_url = "https://api.kth.se/api/kopps/v1/courseRounds/2023:1"
    response = requests.get(index_url)
    #print(response.text) # here it is correct 
    root = ET.fromstring(response.text)
    # flag = False
    counter = 0
    for course in iterate_courses():
        if counter == 5:
            break
        # if course.get("courseCode") == "ME2083":
        #     flag = True
        # if (flag):
        file.write(course.get("courseCode")+" "+course.get("startTerm")+" "+course.get("roundId")+"\n")           
        content_file_name = "C:\\Users\\46705\\Documents\\Search_engines\\project_work\\kth-qa\\files\\"+course.get("courseCode")+course.get("startTerm")+course.get("roundId")+".txt"
        content_file = open(content_file_name, "w",encoding='utf-8')
        
        # get course information
        content_url = "https://api.kth.se/api/kopps/v1/course/"+course.get("courseCode")+"/round/"+course.get("startTerm")[:-1]+":"+course.get("startTerm")[-1]+"/"+course.get("roundId")
        course_response = requests.get(content_url)
        if course_response.status_code == 200:
            handle_xml(course_response.text, content_file)
        
        # get syllabus
        syllabus_url = "https://api.kth.se/api/kopps/v1/course/"+course.get("courseCode")
        syllabus_response = requests.get(syllabus_url)
        if syllabus_response.status_code == 200:
            handle_xml(syllabus_response.text, content_file)

        # get syllabus
        syllabus_url = "https://api.kth.se/api/kopps/v1/course/"+course.get("courseCode")+"/plan"
        syllabus_response = requests.get(syllabus_url)
        if syllabus_response.status_code == 200:
            handle_xml(syllabus_response.text, content_file)

        content_file.close()
        counter  += 1
        
        
    print("saved to %s" % file_name)
    file.close()


if __name__ == "__main__":
    save_courses(limit=10)
    # wabscrape()






