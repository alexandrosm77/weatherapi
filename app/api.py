""" Flask application to serve an API for getting weather forecast from 
    openweathermap.org. Needs an API key from openweathermap.org 
    that can be obtained by registering for free.
    This key needs to passed in the application by an environment variable
    named EXTERNAL_API_KEY"""
import os
import logging
import json
from flask import Flask, Response
from datetime import datetime
import requests

app = Flask(__name__)

# Setup gunicorn logging
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Get API key from environment variable or DIE
external_api_key = os.getenv('EXTERNAL_API_KEY', False)
if external_api_key:
    external_url = 'http://api.openweathermap.org/data/2.5/forecast?q=London,uk&APPID='+external_api_key
    app.logger.info('Starting app')
else:
    app.logger.error('No external API key provided')
    raise RuntimeError('No external API key provided')


def kelvin_to_celcious(k): 
    """ Function that converts Kelvin to Celcious"""
    return str(int(k - 273.15))+'C'

def format_humidity(h):
    """ Helper function to format humidity"""
    return str(h)+'%'

def get_data_from_api(external_url):
    """ Function that calls the external api and returns the response"""
    response = requests.get(external_url)
    return response.json()

def process_data(response):
    """ Function that formats a response
        to our required data"""
    return [ {
        'dt': item['dt'],
        'details': {
            'description': item['weather'][0]['description'],
            'temperature': kelvin_to_celcious(item['main']['temp']),
            'pressure': str(item['main']['pressure']),
            'humidity': format_humidity(item['main']['humidity'])
        }
    } for item in response['list'] ]

def get_response(external_url, date, time, key=None):
    """ Function that calls external api, processes data and 
        returns the response back to the main route"""
    try:
        response = get_data_from_api(external_url)
    except:
        return {"status": "error", "message": "Unable to get data from openweathermap"}

    try:
        dt = datetime.strptime(date+time, '%Y%m%d%H%M')
    except ValueError:
        return {"status": "error", "message": "Invalid date/time"}
    data = process_data(response)

    try:
        forecast = next(f['details'] for f in data if f['dt']==int(dt.timestamp()))
    except StopIteration:
        return {
            "status": "error",
            "message": "No data for %s" % dt.strftime('%Y-%m-%d %H:%M')
            }

    return {key: forecast[key]} if key else forecast

@app.route('/weather/london/<date>/<time>', defaults={'detail':None}, methods=['GET'])
@app.route('/weather/london/<date>/<time>/<detail>', methods=['GET'])
def get(date, time, detail):
    """Main routes of api"""
    if (detail not in ['temperature', 'pressure', 'humidity'] and detail is not None):
        return Response(
            json.dumps({"status": "error", "message": "Not Found"}), 
            mimetype='application/json', 
            status=404)
    app.logger.info('Incoming request for date {}, time {}'.format(date, time))
    
    response = get_response(external_url, date, time, detail)

    return Response(json.dumps(response), mimetype='application/json', status=200)

# Run flask for development only
if __name__ == '__main__':
    app.run(port=8000)
