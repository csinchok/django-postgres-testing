# django-postgres-testing [![Build Status](https://travis-ci.org/csinchok/django-postgres-testing.svg?branch=master)](https://travis-ci.org/csinchok/django-postgres-testing) [![PyPI version](https://badge.fury.io/py/django-postgres-testing.svg)](https://badge.fury.io/py/django-postgres-testing)

This package contains a simple Django TestRunner that will setup a temporary postgres instance, and remove it when testing is over.

In my personal use case, this is because I don't really like running postgres all the time on my laptop. Additionally, I don't want to have to worry about making test databases/users for each of my Django projects.

This project solves the issue by running a brand new postgres instance for each test run, deleting all data when the run is over.

## Usage

Install the package:

    $ pip install django-postgres-testing

Add this to your settings file:

    TEST_RUNNER = 'django_postgres_testing.TemporaryPostgresRunner'
