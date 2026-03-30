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

## API Endpoints

- `GET /api/message` - Get a message from the backend
- `GET /api/health` - Health check endpoint
- `GET /` - API root endpoint

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

## Next Steps

- Add database support (PostgreSQL, MongoDB, etc.)
- Implement authentication
- Add more API endpoints
- Create frontend components and pages
- Add testing (Jest, Pytest)
- Set up CI/CD pipeline
