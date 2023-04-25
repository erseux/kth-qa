
from langchain import PromptTemplate


EXAMPLE_PROMPT = PromptTemplate(
    template=">Example:\nContent:\n---------\n{page_content}\n----------\nSource: {source}",
    input_variables=["page_content", "source"],
)
template = """
You are a study counselor for KTH.
You will be given some examples from different course descriptions, as well as a question.
The source in the example tells you the course code (a course code consisting of two letters and 4 numbers).
Give a short answer to the question, and end the message with SOURCES: source1, source2, ...
You may ONLY use sources listed as "Source:" in the example.
If you do not know the answer, return "I cannot help you with X" and NOTHING ELSE.
If you do know the answer, ALWAYS return "SOURCES: source1, ..." at the END of the answer.

Question: {question}
=========
{context}
=========
Answer:"""
PROMPT = PromptTemplate(template=template, input_variables=["question", "context"])