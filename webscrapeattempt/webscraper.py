from bs4 import BeautifulSoup
import requests
from xml.etree import cElementTree as ET


# skapa lista med alla kurser
# vill lagra url

def handle_xml(xml, content_file):
    
    xml_tree = ET.fromstring(xml)  
    for elem in xml_tree.iter():
        if(elem.tag and elem.text):
            content_file.write(elem.tag+":"+elem.text+"\n")

        

def wabscrape():  

    file_name = "C:\\Users\\46705\\Documents\\Search_engines\\project_work\\kth-qa\\files\\courses.txt"
    file = open(file_name, "w",encoding='utf-8')
    index_url = "https://api.kth.se/api/kopps/v1/courseRounds/2023:1"
    response = requests.get(index_url)
    #print(response.text) # here it is correct 
    root = ET.fromstring(response.text)
    # flag = False
    counter = 0
    for course in root.iter("courseRound"): 
        
        if counter == 5:
            break
        
        print(course.get("courseCode"))

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

wabscrape()






