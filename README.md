# {{ project_name|title }}

## About

Describe your project here.

## Prerequisites

- Python 3.5
- pip
- virtualenv (virtualenvwrapper is recommended for use during development)

## Installation

### 1. Create virtualenv

#### If you are using pyenv:

```
    pyenv virtualenv 3.5.1 {{ project_name }}
    pyenv activate {{ project_name }}
```

#### If you are using virtualenv:

```
    virtualenv .env
    source .env/bin/activate
```

### 2. Install dependencies

```
    pip install -r requirements-dev.txt
```

### 3. Create local_settings.py file

```
    cp {{ project_name }}/local_settings.py.default {{ project_name }}/local_settings.py
```

### 4. Create database in postgresql

### 5. Migrate database

```
    python manage.py migrate
```

### 6. Create super user so you can login to admin panel

```
    python manage.py createsuperuser
```
