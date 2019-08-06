TEST_WIKI_PATH = tests/testwikis/userwiki

help:
	@echo "clean - remove all build, test, coverage and Python artifacts, and reset test wikis"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "test-wiki - run composer against an actual wiki set up for testing. Set jump=1 to set the jump flag."
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "sdist - package"

build:
	pip install -e .[dev]

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr coverage_html_report/
	./reset-tests.sh

lint:
	flake8 composer tests

test:
	nose2

test-all:
	tox

test-wiki:
	@echo "Operating on TEST wiki at location:" ${TEST_WIKI_PATH}
ifeq ($(jump),1)
	whats-next ${TEST_WIKI_PATH} --test --jump
else
	whats-next ${TEST_WIKI_PATH} --test
endif

coverage:
	coverage run --source composer setup.py test
	coverage report -m
	coverage html
	open coverage_html_report/index.html

sdist: clean
	python setup.py sdist
	ls -l dist

.PHONY: help build clean clean-pyc clean-build clean-test lint test test-all coverage sdist
