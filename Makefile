SSH_KEY=

-include Makefile.settings

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

ansible_staging:
	ansible-playbook -i server/ansible/staging server/ansible/site.yml -u root --ask-vault

ansible_production:
	ansible-playbook -i server/ansible/production server/ansible/site.yml -u root --ask-vault

deploy_staging:
	fab -R staging deploy

deploy_production:
	fab -R production deploy
