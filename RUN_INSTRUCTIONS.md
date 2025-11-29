# Running the Solution

## Prerequisites

1. **Python 3.8+** with dependencies installed:
   ```bash
   cd Traffic_Backend
   pip install -r requirements.txt
   ```

2. **.NET 8.0 SDK** installed

## Starting the Services

### Option 1: Run Both Services (Recommended)

#### Terminal 1 - Backend (FastAPI)
```bash
cd Traffic_Backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: **http://localhost:8000**

#### Terminal 2 - Frontend (ASP.NET Core)
```bash
cd Traffic_Frontend
dotnet run
```

The frontend will be available at:
- **https://localhost:5001** (HTTPS)
- **http://localhost:5000** (HTTP)

### Option 2: Run in Background (Windows PowerShell)

```powershell
# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd Traffic_Backend; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd Traffic_Frontend; dotnet run"
```

## Accessing the Application

1. **Dashboard**: Navigate to `https://localhost:5001/Home/Dashboard`
2. **Evidence Viewer**: Click on red zones in the heatmap to view evidence photos
3. **API Documentation**: Visit `http://localhost:8000/docs` for FastAPI Swagger UI

## Verifying Services are Running

### Check Backend
```bash
curl http://localhost:8000/
```

Or open in browser: http://localhost:8000/

### Check Frontend
Open browser: https://localhost:5001/

## Troubleshooting

### Backend Issues
- Ensure Python dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available
- Verify FastAPI is installed: `pip install fastapi uvicorn`

### Frontend Issues
- Ensure .NET SDK is installed: `dotnet --version`
- Restore packages: `dotnet restore`
- Check if ports 5000/5001 are available
- For HTTPS certificate issues, trust the dev certificate: `dotnet dev-certs https --trust`

### Common Errors

1. **Port already in use**: Change the port in the command or kill the process using that port
2. **Module not found**: Install missing Python packages
3. **Certificate errors**: Trust the development certificate for HTTPS

## Next Steps

1. Upload a road network GeoJSON file via the API
2. Upload damaged roads CSV file (with Lat, Lon, Severity, Image_URL columns)
3. View the dashboard to see heatmap visualization
4. Click red zones to view evidence photos

## API Endpoints

- `POST /upload-road-network` - Upload GeoJSON road network
- `POST /ingest-damaged-roads` - Upload CSV with damaged roads
- `GET /cluster-evidence-images?lat={lat}&lon={lon}` - Get evidence images for a cluster
- `GET /road-network-status` - Check road network status
- `GET /docs` - API documentation (Swagger UI)

