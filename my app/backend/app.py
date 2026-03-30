from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests
from config import config

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])

# Enable CORS for all routes
CORS(app)

# Weather API endpoints
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"

@app.route('/api/message', methods=['GET'])
def get_message():
    """Return a simple message from the backend"""
    return jsonify({
        'message': 'Hello from Python Flask Backend!',
        'status': 'success'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'backend'
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Welcome to the backend API',
        'version': '1.0.0'
    })

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Get current weather and forecast for given latitude and longitude
    Query params: lat (latitude), lon (longitude)
    Example: /api/weather?lat=40.7128&lon=-74.0060
    """
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if not lat or not lon:
            return jsonify({
                'error': 'Missing latitude or longitude parameters',
                'example': '/api/weather?lat=40.7128&lon=-74.0060'
            }), 400
        
        # Fetch weather data from Open-Meteo API
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
            'hourly': 'temperature_2m,weather_code',
            'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum',
            'timezone': 'auto'
        }
        
        response = requests.get(WEATHER_API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        return jsonify({
            'status': 'success',
            'location': {
                'latitude': float(lat),
                'longitude': float(lon),
                'timezone': data.get('timezone', 'Unknown')
            },
            'current_weather': {
                'temperature': data['current'].get('temperature_2m'),
                'humidity': data['current'].get('relative_humidity_2m'),
                'weather_code': data['current'].get('weather_code'),
                'wind_speed': data['current'].get('wind_speed_10m')
            },
            'forecast': {
                'daily': data.get('daily', {})
            }
        })
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to fetch weather data: {str(e)}',
            'status': 'error'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/weather/search', methods=['GET'])
def search_location():
    """
    Search for location by name to get latitude and longitude
    Query params: name (location name)
    Example: /api/weather/search?name=New+York
    """
    try:
        name = request.args.get('name')
        
        if not name:
            return jsonify({
                'error': 'Missing name parameter',
                'example': '/api/weather/search?name=London'
            }), 400
        
        params = {
            'name': name,
            'count': 5,
            'language': 'en',
            'format': 'json'
        }
        
        response = requests.get(GEOCODING_API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if 'results' not in data or len(data['results']) == 0:
            return jsonify({
                'error': 'Location not found',
                'status': 'not_found'
            }), 404
        
        results = []
        for result in data['results'][:5]:
            results.append({
                'name': result.get('name'),
                'country': result.get('country'),
                'latitude': result.get('latitude'),
                'longitude': result.get('longitude'),
                'admin1': result.get('admin1'),
                'timezone': result.get('timezone')
            })
        
        return jsonify({
            'status': 'success',
            'results': results
        })
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to search location: {str(e)}',
            'status': 'error'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/weather/reverse-geocode', methods=['GET'])
def reverse_geocode():
    """
    Reverse geocode coordinates to get city name
    Query params: lat (latitude), lon (longitude)
    Example: /api/weather/reverse-geocode?lat=40.7128&lon=-74.0060
    """
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if not lat or not lon:
            return jsonify({
                'error': 'Missing latitude or longitude parameters'
            }), 400
        
        params = {
            'latitude': lat,
            'longitude': lon,
            'language': 'en'
        }
        
        response = requests.get(GEOCODING_API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if 'results' not in data or len(data['results']) == 0:
            return jsonify({
                'city': f'{lat}, {lon}',
                'country': 'Unknown'
            })
        
        result = data['results'][0]
        city_name = result.get('name', 'Unknown')
        country = result.get('country', 'Unknown')
        admin1 = result.get('admin1', '')
        
        return jsonify({
            'status': 'success',
            'city': city_name,
            'region': admin1,
            'country': country,
            'latitude': lat,
            'longitude': lon
        })
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to reverse geocode: {str(e)}',
            'status': 'error'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
