import json
import pytest
from app.api import app
from unittest.mock import patch
from requests.exceptions import Timeout

@pytest.fixture
def client():
    return app.test_client()

def api_fake_response():
    fake_response = {'list':[{
        'dt': 1555437600,
        'weather': [{'description':'sunny'}],
        'main': {
            'temp': 280,
            'humidity': 55,
            'pressure': 1019
        }}]
    }
    return fake_response

@patch('app.api.requests.get')
def test_response(mock_get, client):
    """Test that a proper response is returned"""
    mock_get.return_value.json.return_value = api_fake_response()
    result = client.get('/weather/london/20190416/1900')
    response_body = json.loads(result.get_data())
    #import pdb; pdb.set_trace()
    assert result.status_code == 200
    assert result.headers['Content-Type'] == 'application/json'
    assert response_body['temperature'] == '6C'

@patch('app.api.requests.get')
def test_response_unknown_detail(mock_get, client):
    """Test that error is returned when calling unknown route"""
    mock_get.return_value.json.return_value = api_fake_response()
    result = client.get('/weather/london/20190416/1900/unknown')
    response_body = json.loads(result.get_data())
    assert result.status_code == 404
    assert response_body['status'] == 'error'
    assert response_body['message'] == 'Not Found'

@patch('app.api.requests.get')
def test_response_invalid_date_time(mock_get, client):
    """Test that an error is returned when passing an invalid date"""
    mock_get.return_value.json.return_value = api_fake_response()
    result = client.get('/weather/london/20190416/19001')
    response_body = json.loads(result.get_data())
    assert result.status_code == 200
    assert response_body['status'] == 'error'
    assert response_body['message'] == 'Invalid date/time'

@patch('app.api.requests.get')
def test_response_external_api_call_fail(mock_get, client):
    """Test to simulate external api call failure. Should return an error"""
    mock_get.side_effect = Timeout
    result = client.get('/weather/london/20190416/1900')
    response_body = json.loads(result.get_data())
    assert result.status_code == 200
    assert response_body['status'] == 'error'
    assert response_body['message'] == 'Unable to get data from openweathermap'

@patch('app.api.requests.get')
def test_response_date_not_found(mock_get, client):
    """Test that passing an out of range date fails"""
    mock_get.return_value.json.return_value = api_fake_response()
    result = client.get('/weather/london/20190416/1600')
    response_body = json.loads(result.get_data())
    assert result.status_code == 200
    assert response_body['status'] == 'error'
    assert response_body['message'] == 'No data for 2019-04-16 16:00'

