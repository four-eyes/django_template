run:
	python manage.py runserver

check_dependencies:
	pip list --outdated

lint_python:
	prospector

clean:
	find . -name "*.pyc" -exec rm -rf {} \;
