#!/usr/bin/env bash

sudo apt-get update
sudo apt-get -y install git rabbitmq-server screen python3-dev python3-pip python3.4-venv
sudo apt-get -y install python-celery
sudo apt-get -y install libpq-dev postgresql postgresql-contrib

sudo pip3 install virtualenv

cd quarterly_report_project

python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt


sudo -u postgres -H -- psql -c "CREATE DATABASE quarterly_report;"
sudo -u postgres -H -- psql -c "CREATE USER quarterly_report_user WITH PASSWORD 'develop_password';"
sudo -u postgres -H -- psql -c "ALTER ROLE quarterly_report_user SET client_encoding TO 'utf8'"
sudo -u postgres -H -- psql -c "ALTER ROLE quarterly_report_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres -H -- psql -c "ALTER ROLE quarterly_report_user SET timezone TO 'UTC';"
sudo -u postgres -H -- psql -c "GRANT ALL PRIVILEGES ON DATABASE quarterly_report TO quarterly_report_user;"