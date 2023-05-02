import asyncio
import re
import logging

from kth_qa.schema import Answer, Question
logger = logging.getLogger()
import re
from ingest import KURS_URL, DEFAULT_LANGUAGE

from config import Config

COURSE_PATTERN = r"\w{2,3}\d{3,4}\w?" # e.g. DD1315

def blocking_chain(chain, request):
    return chain(request, return_only_outputs=False)

async def question_handler(question: Question, config: Config) -> Answer:
    question = question.question
    logger.info(f"Q: {question}")

    result = await asyncio.to_thread(blocking_chain, config.chain, {"question": question})
    logger.debug(f"result: {result}")

    answer = result['answer']
    logger.info(f"A: {answer}")
    
    if answer.startswith("I cannot help"):
        answer = "I'm sorry, " + answer
        return Answer(**{"answer": answer, "url": ""})
    
    logger.info(result)
    
    sources = result.get('sources')
    logger.info(f"Sources: {sources}")
    if sources:
        sources = re.findall(COURSE_PATTERN, sources)
    else:
        answer, sources = split_sources(answer)

    courses = [source for source in sources if config.course_exists(source)] # filter out courses that don't exist
    sources = set(courses)
    logger.info(f"unique courses: {courses}")

    urls = [KURS_URL.format(course_code=course, language=DEFAULT_LANGUAGE) for course in courses] # format into urls
    logger.info(f"urls: {urls}")

    answer = answer.rsplit(".", 1)[0] + "." # remove everything after the last period

    if (not answer or len(answer) < 3) and urls:
        answer = "Something went wrong, but I found a link."

    return Answer(answer=answer, urls=urls if urls else [])

def split_sources(answer: str):
    patterns = [
        "Sources", 
        "Source",
        "References",
        "Reference",
        "sources",
        "source",
        "SOURCE"
    ]
    for pattern in patterns:
        if pattern in answer:
            ans, sources = answer.split(pattern, 1)
            courses = re.findall(COURSE_PATTERN, sources)
            return ans, courses
        
    return answer, []
