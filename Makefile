export PYTEST_DISABLE_PLUGIN_AUTOLOAD = 1
TEST_WIKI_PATH = tests/testwikis/userwiki
UNIT_TESTS_PATH = tests/unit
FUNCTIONAL_TESTS_PATH = tests/functional

help:
	@echo "clean - remove all build, test, coverage and Python artifacts, and reset test wikis"
	@echo "build - install package and dependencies for local development"
	@echo "clean - clean all build and test artifacts and reset any test wikis"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint-source - check style for source with flake8"
	@echo "lint-tests - check style for tests with flake8"
	@echo "lint-all - check style with flake8"
	@echo "lint - alias for lint-source"
	@echo "black - run black auto-formatting on all code"
	@echo "test-unit - run unit tests"
	@echo "test-functional - run functional tests"
	@echo "test-all - run unit and functional tests"
	@echo "test - run specified tests, e.g.:"
	@echo "       make test DEST=tests/unit/my_module.py"
	@echo "       (defaults to unit tests if none specified)"
	@echo "test-stop - run tests and stop on the first failure"
	@echo "test-debug - run specified tests and enter debugger on the first failure. e.g."
	@echo "             make test-debug DEST=tests/unit/my_module.py"
	@echo "             (defaults to unit tests if none specified)"
	@echo "test-matrix - run tests on every Python version with tox"
	@echo "test-tldr - run specified tests and output just the stacktrace, e.g."
	@echo "             make test-tldr DEST=tests/unit/my_module.py"
	@echo "             (defaults to unit tests if none specified)"
	@echo "test-wiki - run composer against an actual wiki set up for testing. Set jump=1 to set the jump flag."
	@echo "debug - alias for test-debug"
	@echo "tldr - alias for test-tldr"
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
	python setup.py test --addopts $(UNIT_TESTS_PATH)

test-functional: clean-test
	python setup.py test --addopts $(FUNCTIONAL_TESTS_PATH)

test-all: clean-test test-unit test-functional

test:
ifdef DEST
	$(eval OPTS := --addopts $(DEST))
else
	$(eval OPTS := --addopts $(UNIT_TESTS_PATH))
endif
	python setup.py test $(OPTS)

# stop on first failing test
test-stop:
	python setup.py test --addopts -x

# debug on first failing test
test-debug:
ifdef DEST
	$(eval OPTS := --addopts "-x --pudb $(DEST)")
else
	$(eval OPTS := --addopts "-x --pudb $(UNIT_TESTS_PATH)")
endif
	python setup.py test $(OPTS)

test-matrix:
	tox

test-tldr:
ifdef DEST
	$(eval OPTS := --addopts "-p tldr -p no:sugar $(DEST)")
else
	$(eval OPTS := --addopts "-p tldr -p no:sugar $(UNIT_TESTS_PATH)")
endif
	python setup.py test $(OPTS)

test-wiki: build
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
