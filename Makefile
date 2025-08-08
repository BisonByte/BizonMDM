.RECIPEPREFIX := >
.PHONY: setup dev test format

setup:
>pip install -r server/requirements.txt
>npm install --prefix web-admin
>pre-commit install

dev:
>python server/server.py

test:
>pytest server/tests

format:
>pre-commit run --all-files
