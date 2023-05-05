from config import State
from langchain.callbacks import get_openai_callback
from ingest import KURS_URL, DEFAULT_LANGUAGE
import asyncio
import re
import logging

from kth_qa.schema import Answer, Question
logger = logging.getLogger()


COURSE_PATTERN = r"\w{2,3}\d{3,4}\w?"  # e.g. DD1315


def blocking_chain(chain, request):
    return chain(request, return_only_outputs=True)


async def question_handler(question: Question, state: State) -> Answer:
    question = question.question
    logger.info(f"Q: {question}")

    cost = 0
    with get_openai_callback() as cb:
        result = await asyncio.to_thread(blocking_chain, state.chain, {"question": question})
        cost = cb.total_cost
    logger.debug(f"result: {result}")

    answer = result['answer']
    logger.info(f"A: {answer}")

    if answer.startswith("I cannot help"):
        answer = "I'm sorry, " + answer  # Be more polite
        return Answer(**{"answer": answer, "urls": []})

    sources = result.get('sources')
    logger.info(f"Sources: {sources}")
    if sources:
        sources = re.findall(COURSE_PATTERN, sources)
    else:
        answer, sources = split_sources(answer)

    courses = [source.upper() for source in sources if state.course_exists(
        source)]  # filter out courses that don't exist
    courses = set(courses)
    logger.info(f"unique courses: {courses}")

    urls = [KURS_URL.format(course_code=course, language=DEFAULT_LANGUAGE)
            for course in courses]  # format into urls
    logger.info(f"urls: {urls}")

    answer = answer.strip().removesuffix("(").strip()

    if (not answer or len(answer) < 3) and urls:
        answer = "Something went wrong, but I found a link."

    logging.info(f"Cost of query: ${'{0:.2g}'.format(cost)}")

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
            all_answers = answer.split(pattern)
            if len(all_answers) == 2:
                ans, sources = all_answers
                courses = re.findall(COURSE_PATTERN, sources)
            elif len(all_answers) > 2:
                ans = ""
                courses = []
                for i, a in enumerate(all_answers):
                    if i % 2 == 0:
                        ans += a
                    else:
                        courses = re.findall(COURSE_PATTERN, a)
                        courses.extend(courses)
            return ans, courses

    return answer, []
