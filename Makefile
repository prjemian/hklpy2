# Makefile to support common developer commands

all :: style docs coverage

clean ::
	make -C docs clean

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

realclean :: clean
	/bin/rm -rf ./docs/build
	/bin/rm -rf ./docs/source/generated

style :: isort pre

test:
	pytest -vvv ./hklpy2
