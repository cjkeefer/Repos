from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests
from config import config
from db import (init_db, get_all_chores, add_chore, toggle_chore, delete_chore, update_chore,
                get_all_menu, add_menu_item, delete_menu_item,
                get_all_grocery, add_grocery_item, toggle_grocery_purchased, delete_grocery_item)

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])

# Enable CORS for all routes
CORS(app)

# Initialize database
with app.app_context():
    init_db()

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
                'daily': data.get('daily', {}),
                'hourly': data.get('hourly', {})
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
    Reverse geocode coordinates to get city name using Nominatim
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
        
        # Use Nominatim for reverse geocoding (free, no API key needed)
        nominatim_url = 'https://nominatim.openstreetmap.org/reverse'
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'zoom': 10
        }
        
        # Nominatim requires a user agent
        headers = {
            'User-Agent': 'MyApp/1.0'
        }
        
        response = requests.get(nominatim_url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Extract city name from the address
        address = data.get('address', {})
        city = address.get('city') or address.get('town') or address.get('village') or 'Unknown'
        country = address.get('country', 'Unknown')
        
        return jsonify({
            'status': 'success',
            'city': city,
            'country': country,
            'latitude': lat,
            'longitude': lon
        })
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to reverse geocode: {str(e)}',
            'status': 'error',
            'city': f'{lat}, {lon}'
        }), 200  # Return 200 with fallback data to avoid errors
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'status': 'error',
            'city': f'{lat}, {lon}'
        }), 200  # Return 200 with fallback data

@app.route('/api/calendar/sync', methods=['POST'])
def sync_calendar():
    """
    Sync calendar data from Google or Outlook
    POST body: {
        "provider": "google" or "outlook",
        "token": "access_token",
        "user_id": "user_id"
    }
    """
    try:
        data = request.get_json()
        provider = data.get('provider')
        token = data.get('token')
        user_id = data.get('user_id')
        
        if not all([provider, token, user_id]):
            return jsonify({
                'error': 'Missing required fields: provider, token, user_id'
            }), 400
        
        if provider == 'google':
            # Store Google token (in production, encrypt this)
            return jsonify({
                'status': 'success',
                'message': f'Google calendar synced for user {user_id}',
                'provider': 'google'
            })
        elif provider == 'outlook':
            # Store Outlook token (in production, encrypt this)
            return jsonify({
                'status': 'success',
                'message': f'Outlook calendar synced for user {user_id}',
                'provider': 'outlook'
            })
        else:
            return jsonify({
                'error': f'Unknown provider: {provider}'
            }), 400
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to sync calendar: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    """
    Get stored calendar events for a user
    Query params: user_id, provider (optional)
    """
    try:
        user_id = request.args.get('user_id')
        provider = request.args.get('provider')
        
        if not user_id:
            return jsonify({
                'error': 'Missing user_id parameter'
            }), 400
        
        # In a real app, fetch from database
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'provider': provider,
            'events': []
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch calendar events: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/calendar/create-event', methods=['POST'])
def create_calendar_event():
    """
    Create a new calendar event
    POST body: {
        "provider": "google" or "outlook",
        "title": "Event Title",
        "description": "Event Description",
        "start_time": "2024-01-01T10:00:00",
        "end_time": "2024-01-01T11:00:00",
        "attendees": []
    }
    """
    try:
        data = request.get_json()
        required_fields = ['provider', 'title', 'start_time', 'end_time']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': f'Missing required fields: {required_fields}'
            }), 400
        
        return jsonify({
            'status': 'success',
            'message': f'Event created on {data["provider"]} calendar',
            'event_id': 'new_event_123'
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to create event: {str(e)}',
            'status': 'error'
        }), 500

# Chore List API Endpoints
@app.route('/api/chores', methods=['GET'])
def get_chores():
    """
    Get all chores from the database
    """
    try:
        chores = get_all_chores()
        return jsonify({
            'status': 'success',
            'chores': chores
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch chores: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/chores', methods=['POST'])
def create_chore():
    """
    Create a new chore
    POST body: {
        "title": "Wash dishes",
        "assignedTo": "John",
        "dueDate": "2026-03-31"
    }
    """
    try:
        data = request.get_json()
        title = data.get('title')
        assigned_to = data.get('assignedTo')
        due_date = data.get('dueDate')
        
        if not all([title, assigned_to, due_date]):
            return jsonify({
                'error': 'Missing required fields: title, assignedTo, dueDate'
            }), 400
        
        chore = add_chore(title, assigned_to, due_date)
        return jsonify({
            'status': 'success',
            'message': 'Chore created successfully',
            'chore': chore
        }), 201
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to create chore: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/chores/<int:chore_id>', methods=['PUT'])
def update_chore_status(chore_id):
    """
    Update a chore (toggle completed status or update fields)
    PUT body: {
        "completed": true,  # optional - toggles if not provided
        "title": "New title",  # optional
        "assignedTo": "John",  # optional
        "dueDate": "2026-04-01"  # optional
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        # If no data provided, just toggle completed status
        if not data or 'completed' in data:
            chore = toggle_chore(chore_id)
        else:
            # Update specific fields
            title = data.get('title')
            assigned_to = data.get('assignedTo')
            due_date = data.get('dueDate')
            chore = update_chore(chore_id, title, assigned_to, due_date)
        
        if not chore:
            return jsonify({
                'error': 'Chore not found',
                'status': 'not_found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Chore updated successfully',
            'chore': chore
        })
    
    except Exception as e:
        print(f"Error in update_chore_status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Failed to update chore: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/chores/<int:chore_id>', methods=['DELETE'])
def remove_chore(chore_id):
    """
    Delete a chore
    """
    try:
        success = delete_chore(chore_id)
        
        if not success:
            return jsonify({
                'error': 'Chore not found',
                'status': 'not_found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Chore deleted successfully'
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to delete chore: {str(e)}',
            'status': 'error'
        }), 500

# Menu API Endpoints
@app.route('/api/menu', methods=['GET'])
def get_menu():
    """Get all menu items"""
    try:
        items = get_all_menu()
        return jsonify({
            'status': 'success',
            'items': items
        })
    except Exception as e:
        print(f"Error in get_menu: {str(e)}")
        return jsonify({
            'error': f'Failed to fetch menu: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/menu', methods=['POST'])
def create_menu():
    """Create a new menu item"""
    try:
        data = request.get_json() or {}
        name = data.get('name')
        day = data.get('day')
        ingredients = data.get('ingredients')
        
        if not name or not day:
            return jsonify({
                'error': 'Missing required fields: name, day'
            }), 400
        
        item = add_menu_item(name, day, ingredients)
        return jsonify({
            'status': 'success',
            'message': 'Menu item added',
            'item': item
        }), 201
    except Exception as e:
        print(f"Error in create_menu: {str(e)}")
        return jsonify({
            'error': f'Failed to add menu item: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/menu/<int:item_id>', methods=['DELETE'])
def remove_menu(item_id):
    """Delete a menu item"""
    try:
        success = delete_menu_item(item_id)
        if not success:
            return jsonify({
                'error': 'Menu item not found',
                'status': 'not_found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Menu item deleted'
        })
    except Exception as e:
        print(f"Error in remove_menu: {str(e)}")
        return jsonify({
            'error': f'Failed to delete menu item: {str(e)}',
            'status': 'error'
        }), 500

# Grocery API Endpoints
@app.route('/api/grocery', methods=['GET'])
def get_grocery():
    """Get all grocery items"""
    try:
        items = get_all_grocery()
        return jsonify({
            'status': 'success',
            'items': items
        })
    except Exception as e:
        print(f"Error in get_grocery: {str(e)}")
        return jsonify({
            'error': f'Failed to fetch grocery items: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/grocery', methods=['POST'])
def create_grocery():
    """Create a new grocery item"""
    try:
        data = request.get_json() or {}
        name = data.get('name')
        quantity = data.get('quantity')
        
        if not name:
            return jsonify({
                'error': 'Missing required field: name'
            }), 400
        
        item = add_grocery_item(name, quantity)
        return jsonify({
            'status': 'success',
            'message': 'Grocery item added',
            'item': item
        }), 201
    except Exception as e:
        print(f"Error in create_grocery: {str(e)}")
        return jsonify({
            'error': f'Failed to add grocery item: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/grocery/<int:item_id>', methods=['PUT'])
def update_grocery(item_id):
    """Toggle purchased status of a grocery item"""
    try:
        item = toggle_grocery_purchased(item_id)
        if not item:
            return jsonify({
                'error': 'Grocery item not found',
                'status': 'not_found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Grocery item updated',
            'item': item
        })
    except Exception as e:
        print(f"Error in update_grocery: {str(e)}")
        return jsonify({
            'error': f'Failed to update grocery item: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/grocery/<int:item_id>', methods=['DELETE'])
def remove_grocery(item_id):
    """Delete a grocery item"""
    try:
        success = delete_grocery_item(item_id)
        if not success:
            return jsonify({
                'error': 'Grocery item not found',
                'status': 'not_found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Grocery item deleted'
        })
    except Exception as e:
        print(f"Error in remove_grocery: {str(e)}")
        return jsonify({
            'error': f'Failed to delete grocery item: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
