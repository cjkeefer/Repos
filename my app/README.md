# My App - React + Python Backend

A full-stack application with:
- **Frontend**: React 18 with TypeScript and Vite
- **Backend**: Python Flask with REST API
- **DevOps**: Docker & Docker Compose for containerization
- **Reverse Proxy**: Nginx for routing

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Node.js 18+ (for local development without Docker)
- Python 3.11+ (for local development without Docker)

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up --build

# Access the application
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Nginx: http://localhost:80
```

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# Backend runs on http://localhost:8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

## Project Structure

```
my app/
├── frontend/                 # React TypeScript application
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   └── App.css
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile
├── backend/                  # Python Flask API
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
├── nginx/                    # Nginx reverse proxy configuration
│   └── nginx.conf
└── docker-compose.yml        # Docker orchestration
```

## Features

- **Weather Forecast**: Real-time weather with current conditions and 7-day forecast
  - Current temperature, humidity, wind speed
  - Hourly weather breakdown with 12-hour AM/PM format
  - Fahrenheit display with automatic Celsius conversion
  - Automatic geolocation-based weather lookup
  - City name detection via reverse geocoding
  - Clickable hourly forecast cards

- **Calendar Integration**: Connect to Google Calendar and Outlook
  - View Google Calendar events
  - View Microsoft Outlook/Office 365 events
  - Tab-based interface to switch between providers
  - Detailed event information display (title, time, description)
  - Setup guide for easy OAuth configuration

- **Multi-page Navigation**: React Router with responsive pages
  - Home (Weather forecast page)
  - About (Information page)
  - Calendar (Dual calendar integration)
  - Contact (Contact form)

## API Endpoints

### Weather
- `GET /api/message` - Get a test message from backend
- `GET /api/health` - Health check endpoint
- `GET /api/weather?lat=X&lon=Y` - Get weather for coordinates
- `GET /api/weather/search?name=CityName` - Search for locations
- `GET /api/weather/reverse-geocode?lat=X&lon=Y` - Get city name from coordinates

### Calendar (Backend Support)
- `POST /api/calendar/sync` - Sync calendar data
- `GET /api/calendar/events` - Get stored calendar events
- `POST /api/calendar/create-event` - Create new event

## Calendar Setup

See [CALENDAR_SETUP.md](CALENDAR_SETUP.md) for detailed instructions on:
- Setting up Google Calendar OAuth (with screenshots and step-by-step guide)
- Setting up Outlook Calendar via Azure AD (with portal navigation steps)
- Configuring API permissions for each provider
- Testing the calendar integration
- Troubleshooting common issues
- Production security best practices

## Development Tips

1. **Hot Reload**: Frontend changes in Vite are reflected instantly
2. **Backend Changes**: Restart the backend server to see changes
3. **Environment Variables**: Configure in `backend/.env`
4. **CORS**: Already enabled for frontend-backend communication

## Building for Production

```bash
# Build frontend
cd frontend
npm run build

# Frontend will be served from Docker in production
docker-compose up --build
```

## Environment Configuration

Create a `.env.local` file in the `frontend/` directory with your OAuth credentials:

```env
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
VITE_AZURE_CLIENT_ID=your_azure_client_id_here
```

See [CALENDAR_SETUP.md](CALENDAR_SETUP.md) for detailed instructions on obtaining these credentials.

## Next Steps

- Configure OAuth credentials for calendar features
- Add database support (PostgreSQL, MongoDB, etc.)
- Implement event creation UI
- Add calendar event editing and deletion
- Implement email notifications for events
- Implement authentication
- Add more API endpoints
- Create frontend components and pages
- Add testing (Jest, Pytest)
- Set up CI/CD pipeline
