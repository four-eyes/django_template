run:
	python manage.py runserver

check_dependencies:
	pip list --outdated

lint_python:
	prospector

clean:
	find . -name "*.pyc" -exec rm -rf {} \;

test:
	python manage.py test $(TESTS) --failfast --settings={{ project_name }}.test_settings

