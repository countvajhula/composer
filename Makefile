export PYTEST_DISABLE_PLUGIN_AUTOLOAD = 1
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
	rm -fr pip-wheel-metadata/
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

lint-source:
	flake8 composer

lint-tests:
	flake8 tests

lint-all: lint-source lint-tests

lint: lint-source

black:
	black composer tests

test-unit:
	python setup.py test --addopts tests/unit

test-functional:
	python setup.py test --addopts tests/functional

test-all: test-unit test-functional

test:
ifdef DEST
	$(eval OPTS := --addopts $(DEST))
else
	$(eval OPTS := --addopts tests/unit)
endif
	python setup.py test $(OPTS)

# stop on first failing test
test-stop:
	python setup.py test --addopts -x

# debug on first failing test
test-debug:
	python setup.py test --addopts "-x --pudb"

test-matrix:
	tox

test-tldr:
ifdef DEST
	$(eval OPTS := --addopts "-p tldr -p no:sugar $(DEST)")
else
	$(eval OPTS := --addopts "-p tldr -p no:sugar tests/unit")
endif
	python setup.py test $(OPTS)

test-wiki:
	@echo "Operating on TEST wiki at location:" ${TEST_WIKI_PATH}
ifeq ($(jump),1)
	whats-next ${TEST_WIKI_PATH} --test --jump
else
	whats-next ${TEST_WIKI_PATH} --test
endif

# ideally this should launch pudb to step through the specified tests
debug: test-debug

tldr: test-tldr

coverage:
	coverage run --source composer setup.py test
	coverage report -m
	coverage html
	open coverage_html_report/index.html

sdist: clean
	python setup.py sdist
	ls -l dist

.PHONY: help build clean clean-build clean-pyc clean-test lint-source lint-tests lint-all lint black test-unit test-functional test-all test test-stop test-debug test-matrix test-tldr test-wiki debug coverage sdist
