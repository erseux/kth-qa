import logging
logger = logging.getLogger()

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

from kth_qa.utils import get_courses, touch_folder
from webscraping.scrape_settings import SCRAPE_LANGUAGES, SCRAPE_LIMIT, SELECTED_COURSES


class URLHelper:
    base_url = 'https://www.kth.se/student/kurser/kurs/'

def get_url(course_code, language):
    return URLHelper.base_url + course_code + '?l=' + language

def fetch_url(url):
    return requests.get(url).text

def scrape_course(course_code, language):
    courses = get_courses()
    course_title = courses.get(course_code).get(language) 

    url = get_url(course_code, language)
    html = fetch_url(url)

    soup = BeautifulSoup(html, 'html.parser')

    content = soup.find('section', {'id': 'courseContentBlock'})
    
    # get all text, but split by divs and spans
    text = f'Course description for {course_title}:\n'
    for node in content.children:
        text += extract_text(node)

    text = text.replace('the course', f'the course ({course_title})')
    text = separate_camel_case(text)

    folder = f'kth_qa/files/{language}'
    touch_folder(folder)
    with open(f'{folder}/{course_code}?l={language}.txt', 'w', encoding="utf-8") as f:
        f.write(text)

def read_course_codes():
    courses = get_courses()
    courses = list(courses.keys())
    return courses

def separate_camel_case(text):
    for i in range(len(text)):
        if text[i].isupper() and text[i-1].islower():
            text = text[:i] + '\n' + text[i:]
    return text


def extract_text(node):
    if node.name == None:
        return node.strip()
    else:
        if node.name == 'div':
            separator = '\n'
        elif node.name == 'span':
            separator = ' '
        else:
            separator = ' '
        return separator.join([extract_text(child) for child in node.children])
    
def clean_text(text):
    text = text.replace('\n\n\n', '\n')
    text = text.replace('\n\n', '\n')
    text = text.replace('\t', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('   ', ' ')
    text = text.replace('  ', ' ')
    text = text.replace('\n\n', '\n')
    return text

def main(languages=['en'], select=None, unselect=None, limit=None):
    courses = read_course_codes()

    # only use selected courses
    
    logger.info(f"Selected courses: {select}")

    if select or unselect:
        selected = []
        for course_code in courses:
            if unselect and course_code[:2] in unselect:
                continue
            if select and course_code[:2] not in select:
                continue
            selected.append(course_code)
    else:
        selected = courses

    logger.info(f"Scraping {len(selected)} courses")
    
    for i, course_code in enumerate(tqdm(selected)):
        if limit and i == limit:
            logger.info(f"Reached limit at {i} courses, breaking")
            break
        for language in languages:
            try:
                scrape_course(course_code, language)
            except Exception as e:
                logger.error(f"Failed to scrape {course_code} in {language}: {e}")
                continue
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(languages=SCRAPE_LANGUAGES, unselect=SELECTED_COURSES, limit=SCRAPE_LIMIT)