.PHONY: all test coverage flake8 clean

all:	flake8 test coverage

test:
	py.test

coverage:
	coverage run --source application -m py.test && coverage report

flake8:
	flake8 application tests

init:
	pip3 install -r requirements.txt

clean:
	-find . -name "*.pyc" | xargs rm -f
	-find . -name "__pycache__" | xargs rm -rf
