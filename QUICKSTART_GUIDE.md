# NavDrishti - Quick Start Guide

## 🚀 Starting the Application

### Option 1: Start Everything (Recommended)
```pwsh
.\start_all.ps1
```
This starts both backend and frontend in the background.

### Option 2: Start Services Separately
```pwsh
# Terminal 1 - Backend
.\start_backend.ps1

# Terminal 2 - Frontend  
.\start_frontend.ps1
```

## 🛑 Stopping the Application

```pwsh
.\stop_all.ps1
```

## 🌐 Accessing the Application

- **Dashboard**: http://localhost:5000/Home/Dashboard
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 🔐 Test Credentials

- **Username**: `testadmin`
- **Password**: `testpass123`
- **Roles**: admin, user

## 📊 Phase 2 Features (Current)

✅ **Backend** (Port 8001)
- FastAPI with SQLAlchemy 2.0
- SQLite database (`navdrishti.db`)
- JWT authentication
- Projects CRUD API
- Route analysis API
- Traffic data API
- Notifications API

✅ **Frontend** (Port 5000)
- ASP.NET Core 8.0
- Razor views with Mapbox GL JS
- Backend API integration via HttpClient
- Dashboard with projects list
- Route analysis UI (scaffolded)

✅ **Integration**
- Frontend → Backend communication verified
- API controllers working (`/api/projects`, `/api/routes`)
- Test suite: 6/7 tests passing

## 🧪 Running Tests

```pwsh
# Integration tests
.\.venv\Scripts\python.exe .\test_phase2_integration.py

# Backend unit tests
cd Traffic_Backend
..\.venv\Scripts\python.exe -m pytest tests/
```

## 📁 Project Structure

```
HSC_NavDrishti_AHM/
├── Traffic_Backend/          # FastAPI backend
│   ├── main.py              # App entry point
│   ├── models.py            # SQLAlchemy models
│   ├── routers/             # API endpoints
│   └── tests/               # Unit tests
├── Traffic_Frontend/         # ASP.NET Core frontend
│   ├── Controllers/         # MVC controllers
│   ├── Services/            # Backend API service
│   ├── Views/               # Razor views
│   └── wwwroot/js/          # JavaScript modules
├── start_all.ps1            # Start both servers
├── stop_all.ps1             # Stop both servers
└── test_phase2_integration.py  # Integration tests
```

## 🔧 Configuration

### Backend
- Database: SQLite (dev), MySQL (prod)
- Port: 8001
- Environment variables:
  - `DATABASE_URL`: Connection string
  - `SQLALCHEMY_DATABASE_URL`: Alternative connection string

### Frontend
- Port: 5000
- Configuration: `Traffic_Frontend/appsettings.json`
  - Backend URL: http://localhost:8001
  - Mapbox token: (configured)

## 📝 Next Steps (Phase 3)

- [ ] Implement map-based route selection
- [ ] Render alternative routes on map
- [ ] Real-time traffic overlay visualization
- [ ] Scenario comparison UI
- [ ] Traffic alerts integration

## 🐛 Troubleshooting

**Port already in use:**
```pwsh
.\stop_all.ps1
.\start_all.ps1
```

**Database issues:**
```pwsh
# Reset database
Remove-Item navdrishti.db -Force
.\.venv\Scripts\python.exe -m Traffic_Backend.init_db

# Recreate admin user
.\.venv\Scripts\python.exe -m Traffic_Backend.create_admin
```

**Frontend build issues:**
```pwsh
cd Traffic_Frontend
dotnet clean
dotnet build
```
