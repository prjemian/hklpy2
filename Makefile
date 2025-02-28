# Makefile to support common developer commands

all :: style docs coverage

coverage:
	coverage run --concurrency=thread --parallel-mode -m pytest -vvv ./hklpy2
	coverage combine
	coverage report --precision 3 -m

docs ::
	make -C docs html

doc :: docs

isort:
	isort --sl ./hklpy2

pre:
	pre-commit run --all-files

style :: isort pre

test:
	pytest -vvv ./hklpy2
