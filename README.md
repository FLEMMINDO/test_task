# test_task
Test task for DimaTech ltd.

# technologies
- python
- fastapi
- gunicorn/uvicorn
- sqlalchemy
- alembic
- postgresql
- docker/docker-compose

# test_data
user | email - test@mail.ru ; password - admin123
admin | email - testAdm@mail.ru ; password - admin123

# deploy with docker
## 1. clone this .git repo
Use
> git clone https://github.com/FLEMMINDO/fastapi-online-shop.git

## 2. use commands in the order down below
> docker-compose build
> docker-compose up -d
> docker-compose exec web alembic upgrade head

## 3. visit localhost:8080; localhost:8080/docs
Enjoy backend functions

# deploy without docker
## 1. clone this .git repo
Use
> git clone https://github.com/FLEMMINDO/fastapi-online-shop.git

## 2. create database with psql
run psql shell, use:
> CREATE DATABASE dimatech_db 
> OWNER postgres 
> ENCODING 'UTF8'

## 3. change .env file
change value **FROM** DB_HOST=db **TO** DB_HOST=localhost

## 4. create venv, install requirements
**WINDOWS** 
> python -m venv venv
> venv/Scripts/activate
> pip install -r requirements.txt

**LINUX** 
> python3 -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt

## 5. launch migrations and start application
use
> alembic upgrade head
> uvicorn APP.main:app --reload

## 6. visit localhost:8080; localhost:8080/docs
Enjoy backend functions
