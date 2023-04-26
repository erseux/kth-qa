from selenium import webdriver
from bs4 import BeautifulSoup

class URLHelper:
    base_url = 'https://www.kth.se/student/kurser/kurs/'

def get_url(course_code, language):
    return URLHelper.base_url + course_code + '?l=' + language

def scrape_course(driver, course_code, language):
    driver.get(get_url(course_code, language))

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    content = soup.find('section', {'id': 'courseContentBlock'})
    text = content.text

    # Clean up text

    # Add a newline before each uppercase letter
    text = ''.join(['\n' + char if char.isupper() else char for char in text])

    # Remove whitespace
    text = '\n'.join([line.strip() for line in text.splitlines() if line.strip() != ''])

    with open(f'../kth_qa/files/course_content_{language}_{course_code}.txt', 'w') as f:
        f.write(text)

def read_course_codes():
    with open('../files/courses.txt', 'r') as f:
        lines = f.read().splitlines()
        courses = [line.split(' ')[0] for line in lines]
        return courses

def main():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)

    for course_code in read_course_codes():
        scrape_course(driver, course_code, 'en')
        scrape_course(driver, course_code, 'sv')
        break

    driver.quit()

if __name__ == '__main__':
    main()