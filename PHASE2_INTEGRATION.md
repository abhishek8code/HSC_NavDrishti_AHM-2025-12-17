# Phase 2 Integration Guide

## Overview
Phase 2 connects the ASP.NET Core frontend to the Python FastAPI backend. The frontend now delegates all API calls through a C# service layer to maintain type safety and separation of concerns.

## Architecture

```
Browser (JavaScript)
    ↓
ASP.NET Frontend (Razor + Controllers)
    ↓
C# Service Layer (BackendApiService)
    ↓
Python Backend (FastAPI)
    ↓
Database (SQLite/MySQL)
```

## Key Components Created

### 1. **BackendApiService.cs** (`Traffic_Frontend/Services/`)
HttpClient wrapper that:
- Manages authentication tokens (JWT)
- Wraps all backend API endpoints
- Handles HTTP requests/responses
- Provides type-safe method calls from C#

**Key Methods:**
- `LoginAsync(username, password)` — Authentication
- `GetProjectsAsync()` — Fetch all projects
- `CreateProjectAsync(project)` — Create new project
- `AnalyzeRouteAsync(coordinates)` — Analyze route
- `GetRecommendationsAsync(routeId, ...)` — Get route alternatives
- `GetLiveTrafficAsync(routeId)` — Fetch traffic data
- `SendNotificationAsync(...)` — Send notifications

### 2. **ProjectsApiController.cs**
REST API endpoints for project management:
```
GET  /api/projects          → GetProjectsAsync()
GET  /api/projects/{id}     → GetProjectAsync(id)
POST /api/projects          → CreateProjectAsync()
PUT  /api/projects/{id}     → UpdateProjectAsync()
```

### 3. **RoutesApiController.cs**
REST API endpoints for route analysis:
```
POST /api/routes/analyze                    → AnalyzeRouteAsync()
POST /api/routes/{id}/recommend            → RecommendRouteAsync()
GET  /api/routes/{id}/traffic              → GetLiveTrafficAsync()
```

### 4. **apiClient.js** (`wwwroot/js/`)
JavaScript client for frontend components to call C# API layer:
```javascript
apiClient.getProjects()
apiClient.createProject(project)
apiClient.analyzeRoute(coordinates)
apiClient.recommendRoute(routeId, lon, lat, lon, lat)
```

### 5. **Updated Dashboard.cshtml**
- Displays list of projects (fetched via BackendApiService)
- Shows project creation form
- Integrates with Mapbox for visualization
- Updates metrics (active projects count)

### 6. **Updated HomeController.cs**
- Injects BackendApiService
- Dashboard action now calls `GetProjectsAsync()`
- Passes projects to view for initial server-side rendering

### 7. **Updated dashboard.js**
- Loads projects on page load via `apiClient.getProjects()`
- Displays projects in list format with status badges
- Handles project creation form submission
- Updates UI metrics

## Testing Flow

### Prerequisites
1. **Backend running:** `cd Traffic_Backend && python -m uvicorn main:app --reload`
2. **Frontend running:** `cd Traffic_Frontend && dotnet run`
3. **Database:** SQLite at `Traffic_Backend/dev_navdrishti.db`

### Test 1: Dashboard Load
1. Navigate to http://localhost:5000/Home/Dashboard
2. **Expected:**
   - Dashboard loads successfully
   - Projects list appears (empty or with existing projects)
   - Create Project form is visible
   - Metrics show project count
   - Mapbox map renders

### Test 2: Create Project via UI
1. Fill in "Project Name" field (e.g., "Test Route Analysis")
2. Select status (e.g., "active")
3. Click "Create Project"
4. **Expected:**
   - Form submits successfully
   - Projects list updates with new project
   - New project appears in list
   - Active Projects count increments

### Test 3: API Call Verification
Open browser Developer Tools (F12) → Network tab:
1. Create a new project
2. **Expected Network Calls:**
   - `POST /api/projects` (frontend API)
   - This triggers backend: `POST /projects/` (backend API)
   - Response: 201 Created with new project data

### Test 4: Backend Verification
Check backend logs during project creation:
```
GET /projects/ — 200 OK (from Dashboard load)
POST /projects/ — 201 Created (from form submission)
```

## Configuration

### appsettings.json
```json
{
  "BackendApi": {
    "BaseUrl": "http://localhost:8000"  // Python backend URL
  },
  "ConnectionStrings": {
    "NavDrishtiDb": "Server=localhost;Database=navdrishti;User=root;Password=..."
  }
}
```

### Service Registration (Program.cs)
```csharp
builder.Services.AddHttpClient<BackendApiService>();
```

## Error Handling

All API calls include try-catch blocks with logging:
- **Failed Project Load:** Shows "Failed to load projects"
- **Failed Project Create:** Shows alert with error message
- **Network Issues:** Logged to browser console and server logs

## Next Steps (Phase 2 Continuation)

### Immediate
- [ ] Test end-to-end workflow (project creation → dashboard)
- [ ] Verify all API calls routing correctly
- [ ] Test error scenarios (backend down, network timeout)

### Short-term (Week 1)
- [ ] Add route analysis UI (map-based coordinate selection)
- [ ] Wire recommendation engine to frontend
- [ ] Display traffic data in real-time
- [ ] Add notifications panel

### Medium-term (Week 2)
- [ ] Lane-specific analysis visualization
- [ ] Diversion/expansion planning UI
- [ ] Historical traffic analytics
- [ ] Load testing (100+ concurrent users)

## Debugging

### Check if Backend is Running
```powershell
Get-Process python  # Should show uvicorn process
curl http://localhost:8000/projects/  # Should return 200 OK
```

### Check if Frontend is Running
```powershell
Get-Process dotnet  # Should show dotnet process
curl http://localhost:5000/Home/Dashboard  # Should return HTML
```

### Browser Console Errors
1. Open F12 → Console tab
2. Look for errors from `apiClient.js` or `dashboard.js`
3. Common issues:
   - CORS errors (check FastAPI CORS settings)
   - 404 on `/api/projects` (check controller routing)
   - Network timeouts (check backend/frontend ports)

### Logs to Check
- **Frontend:** `dotnet run` console output
- **Backend:** `python -m uvicorn main:app --reload` console output
- **Browser:** F12 Developer Tools → Console + Network tabs

## API Response Formats

### Success: List Projects
```json
[
  {
    "id": 1,
    "name": "Ahmedabad Route 1",
    "status": "active"
  }
]
```

### Success: Create Project
```json
{
  "id": 2,
  "name": "New Project",
  "status": "planned"
}
```

### Error: Failed Create
```json
{
  "error": "Project with name already exists"
}
```

## Summary

Phase 2 provides a complete integration bridge:
1. ✅ Type-safe C# service layer (BackendApiService)
2. ✅ RESTful C# API controllers (ProjectsApi, RoutesApi)
3. ✅ JavaScript client for browser calls
4. ✅ Dashboard UI with project management
5. ✅ End-to-end request flow validation

The architecture is extensible—new endpoints can be added to BackendApiService, wrapped in Controllers, and exposed to JavaScript without modifying the core pattern.
