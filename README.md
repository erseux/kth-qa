# kth-qa

## Env file
You need to create a file called .env in the main folder (kth-qa) and add your openai api key.
The content should look like this:
```
OPENAI_API_KEY=YOUR_KEY
OPENAI_CHAT_MODEL=gpt-3.5-turbo
```

## How to run
1. Install Poetry (https://python-poetry.org/)
- For M1 Macs: https://github.com/rybodiddly/Poetry-Pyenv-Homebrew-Numpy-TensorFlow-on-Apple-Silicon-M1 
2. cd into ``kth-qa``
3. run ``poetry install``
4. make sure poetry venv is activated (.venv). If not, run ``poetry shell``

### Scrape files
1. Run ``make courses``
   This runs 
   1. ``python webscraping/scrape_info.py`` which scrapes the list of KTH courses
   2. ``python webscraping/scrape_course.py`` which scrapes the course pages

You can limit the number of courses scraped in both files by changing the variable ``limit``
You can also select what languages to scrape in

### Ingest files
1. Have .txt files in kth_qa/files/en or kth_qa/files/sv
2. Stand in root and run ```make ingest```

### Run site
Run either
- ``python kth_qa/main.py`` or
- ``make start``

## How to search
- If you just want to test the search functionality, you can search for "test"
- You can also define your own test searchs in test_queries.json
