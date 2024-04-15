from flask import Flask, render_template, request, redirect, url_for
from gevent.pywsgi import WSGIServer
from flask_bootstrap import Bootstrap
import requests
import json
import configparser
import logging

app = Flask(__name__)


def get_api_key() -> str:
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        api_key = config.get('API', 'meteo_data_apiKey')
        return api_key
    except Exception as e:
        print(f"Error reading API key from config file: {e}")
        return None


# Example usage
api_key = get_api_key()
if api_key:
    print("API Key:", api_key)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        department_id = request.form['department']
        result = get_station_data(department_id)
        ids = [item['id'] for item in result] if result else []  # Extract IDs from result
        return render_template(['index.html', 'response.html'], departments=range(1, 96), ids=ids, result=result)
    return render_template('index.html', departments=range(1, 96))


#@app.route('/', methods=['GET', 'POST'])
#def index():
#   if request.method == 'POST':
#      department_id = request.form['department']
#      result = get_station_data(department_id)
#     ids = [item['id'] for item in result]
#     return render_template(['response.html', 'test2.html'], result=result, ids=ids)
# return render_template('test2.html')


def get_station_data(department_id):
    api_key = get_api_key()
    if api_key is None:
        return {'error': 'API key not found. Please try again.'}

    url = 'http://public-api.meteofrance.fr/public/DPClim/v1/liste-stations/infrahoraire-6m'
    headers = {'accept': '*/*', 'apikey': api_key}
    params = {'id-departement': str(department_id)}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for department ID {department_id}: {e}")
        return {'error': f"Failed to fetch data for department {department_id}"}


if __name__ == '__main__':
    app.run(debug=True)
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()
