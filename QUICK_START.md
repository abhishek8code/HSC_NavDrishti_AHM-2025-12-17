# Quick Start Guide

## Services Status

Both services are starting in the background. Please wait a few moments for them to fully initialize.

## Access Points

### Backend API (FastAPI)
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Status**: Starting...

### Frontend (ASP.NET Core)
- **HTTP**: http://localhost:5000
- **HTTPS**: https://localhost:5001
- **Dashboard**: https://localhost:5001/Home/Dashboard
- **Status**: Starting...

## Quick Access Links

Once services are ready, open these in your browser:

1. **Dashboard**: https://localhost:5001/Home/Dashboard
2. **API Documentation**: http://localhost:8000/docs
3. **API Root**: http://localhost:8000/

## Verify Services

### Check Backend
```powershell
curl http://localhost:8000/
```

### Check Frontend
Open browser: https://localhost:5001/

## If Services Don't Start

### Manual Start - Backend
```powershell
cd Traffic_Backend
python -m uvicorn main:app --reload --port 8000
```

### Manual Start - Frontend
```powershell
cd Traffic_Frontend
dotnet run
```

## Next Steps

1. Wait 10-15 seconds for services to fully start
2. Open the Dashboard: https://localhost:5001/Home/Dashboard
3. Upload road network GeoJSON via API
4. Upload damaged roads CSV with evidence images
5. View heatmap and click red zones to see evidence photos

## Troubleshooting

- **Port already in use**: Kill the process using that port or change the port
- **Certificate errors**: Trust dev certificate: `dotnet dev-certs https --trust`
- **Module not found**: Install dependencies: `pip install -r requirements.txt`

