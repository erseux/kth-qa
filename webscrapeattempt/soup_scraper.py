from selenium import webdriver
from bs4 import BeautifulSoup

class URLHelper:
    base_url = 'https://www.kth.se/student/kurser/kurs/'

def get_url(course_code, language):
    return URLHelper.base_url + course_code + '?l=' + language

def scrape_course(course_code, language):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    driver.get(get_url(course_code, language))
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    content = soup.find('section', {'id': 'courseContentBlock'})

    with open(f'../files/course_content_{language}_{course_code}.txt', 'w') as f:
        f.write(content.text)

def read_course_codes():
    with open('../files/courses.txt', 'r') as f:
        lines = f.read().splitlines()
        courses = [line.split(' ')[0] for line in lines]
        return courses

def main():
    for course_code in read_course_codes():
        scrape_course(course_code, 'en')
        scrape_course(course_code, 'sv')

if __name__ == '__main__':
    main()