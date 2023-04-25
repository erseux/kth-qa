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

### Ingest files
1. Have .txt files in kth_qa/files
2. Stand in root and run ```make ingest```

### Run site
Run either
- ``python kth_qa/main.py`` or
- ``make start``

## How to search
- If you just want to test the search functionality, you can search for "test"
- You can also define your own test searchs in test_queries.json
