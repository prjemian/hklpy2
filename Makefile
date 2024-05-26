# Makefile to support common developer commands

all :: isort ruff docs test

coverage:
	coverage run --concurrency=thread --parallel-mode -m pytest -vvv .
	coverage combine
	coverage report --precision 3 -m

docs ::
	make -C docs html

doc :: docs

isort:
	isort --sl ./hklpy2

ruff:
	ruff check

test:
	pytest -vvv
