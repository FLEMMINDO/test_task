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
user | email - test@mail.ru ; password - admin123 <br>
admin | email - testAdm@mail.ru ; password - admin123 <br>

# deploy with docker
## 1. clone this .git repo
Use<br>
> git clone https://github.com/FLEMMINDO/fastapi-online-shop.git

## 2. use commands in the order down below
> docker-compose build<br>
> docker-compose up -d<br>
> docker-compose exec web alembic upgrade head<br> 

## 3. visit localhost:8080; localhost:8080/docs
Enjoy backend functions

# deploy without docker
## 1. clone this .git repo
Use
> git clone https://github.com/FLEMMINDO/fastapi-online-shop.git

## 2. create database with psql
run psql shell, use:
> CREATE DATABASE dimatech_db<br>
> OWNER postgres<br> 
> ENCODING 'UTF8';<br>

## 3. change .env file
change value **FROM** DB_HOST=db **TO** DB_HOST=localhost<br>

## 4. create venv, install requirements
**WINDOWS** <br>
> python -m venv venv<br>
> venv/Scripts/activate<br>
> pip install -r requirements.txt<br>

**LINUX** <br>
> python3 -m venv venv<br>
> source venv/bin/activate<br>
> pip install -r requirements.txt<br>

## 5. launch migrations and start application
use<br>
> alembic upgrade head<br>
> uvicorn APP.main:app --reload<br>

## 6. visit localhost:8080; localhost:8080/docs
Enjoy backend functions
