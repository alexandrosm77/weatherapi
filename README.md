Sample flask api that exposes endpoints for retrieving weather forecast data.

Application is deployed in heroku using the heroku container service and 
can be curled at:
http://pure-springs-54522.herokuapp.com

To run locally you first need to get a free API key from http://api.openweathermap.org

clone the repo
enter the repo directory

create a virtual environment and activate it:
$python3 -m venv venv
$source venv/bin/activate

export your openweathermap API key:
$export EXTERNAL_API_KEY=<your-key>

install requirement:
$pip install -r requirements-dev.txt

run the application:
$python app/api.py

application can be accessed at http://127.0.0.1:8000

to run the tests:
$pytest


if you prefer to run the app in a docker container:

build the container:
$docker build --build-arg EXT_API_KEY=${EXTERNAL_API_KEY} -t myflask:latest .

start the app:
$docker run --rm -p 8000:8000 -e PORT=8000 myflask
