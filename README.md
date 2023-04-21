# kth-qa

## Env file
You need to create a file called .env in the main folder (kth-qa) and add your openai api key.
The content should look like this:
```
OPENAI_MODEL=text-davinci-002
OPENAI_API_KEY=YOUR_KEY
OPENAI_CHAT_MODEL=gpt-3.5-turbo
```

## How to run
1. Install Poetry (https://python-poetry.org/)
- For M1 Macs: https://github.com/rybodiddly/Poetry-Pyenv-Homebrew-Numpy-TensorFlow-on-Apple-Silicon-M1 
2. cd into ``kth-qa``
3. run ``poetry install``

When the poetry venv is activated, either
- run ``python kth_qa/main.py``
- run ``make start``

## How to search
If you just want to test the search functionality, you can search for "lorem"