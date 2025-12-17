using System.Text.Json;
using System.Text;

namespace Traffic_Frontend.Services
{
    /// <summary>
    /// Service to communicate with Python FastAPI backend
    /// </summary>
    public class BackendApiService
    {
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;
        private readonly ILogger<BackendApiService> _logger;
        private string? _authToken;

        public BackendApiService(HttpClient httpClient, IConfiguration configuration, ILogger<BackendApiService> logger)
        {
            _httpClient = httpClient;
            _configuration = configuration;
            _logger = logger;

            // Set base URL from configuration
            string baseUrl = configuration.GetValue<string>("BackendApi:BaseUrl") ?? "http://localhost:8000";
            _httpClient.BaseAddress = new Uri(baseUrl);
        }

        /// <summary>
        /// Login and get authentication token
        /// </summary>
        public async Task<bool> LoginAsync(string username, string password)
        {
            try
            {
                var loginData = new Dictionary<string, string>
                {
                    { "username", username },
                    { "password", password }
                };

                var content = new FormUrlEncodedContent(loginData);
                var response = await _httpClient.PostAsync("/auth/token", content);

                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    using (JsonDocument doc = JsonDocument.Parse(json))
                    {
                        _authToken = doc.RootElement.GetProperty("access_token").GetString();
                        _httpClient.DefaultRequestHeaders.Authorization = 
                            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _authToken);
                        return true;
                    }
                }
                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Login failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Register a new user
        /// </summary>
        public async Task<bool> RegisterAsync(string username, string email, string password)
        {
            try
            {
                var registerData = new
                {
                    username = username,
                    email = email,
                    password = password
                };

                var json = JsonSerializer.Serialize(registerData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync("/auth/register", content);

                return response.IsSuccessStatusCode;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Registration failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get all projects
        /// </summary>
        public async Task<List<ProjectDto>?> GetProjectsAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/projects/");
                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<List<ProjectDto>>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                }
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to get projects: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get single project details
        /// </summary>
        public async Task<ProjectDto?> GetProjectAsync(int projectId)
        {
            try
            {
                var response = await _httpClient.GetAsync($"/projects/{projectId}");
                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<ProjectDto>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                }
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to get project {projectId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Create a new project
        /// </summary>
        public async Task<ProjectDto?> CreateProjectAsync(ProjectCreateDto project)
        {
            try
            {
                var json = JsonSerializer.Serialize(project);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync("/projects/", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseJson = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<ProjectDto>(responseJson, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                }
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to create project: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update an existing project
        /// </summary>
        public async Task<ProjectDto?> UpdateProjectAsync(int projectId, ProjectUpdateDto project)
        {
            try
            {
                var json = JsonSerializer.Serialize(project);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                var response = await _httpClient.PutAsync($"/projects/{projectId}", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseJson = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<ProjectDto>(responseJson, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                }
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to update project: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Analyze a route
        /// </summary>
        public async Task<RouteAnalysisDto?> AnalyzeRouteAsync(List<List<double>> coordinates)
        {
            try
            {
                var analyzeData = new { coordinates = coordinates };
                var json = JsonSerializer.Serialize(analyzeData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync("/routes/analyze", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseJson = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<RouteAnalysisDto>(responseJson, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                }
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to analyze route: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get route recommendations
        /// </summary>
        public async Task<RecommendationResponseDto?> GetRecommendationsAsync(int routeId, double startLon, double startLat, double endLon, double endLat)
        {
            try
            {
                var url = $"/routes/{routeId}/recommend?start_lon={startLon}&start_lat={startLat}&end_lon={endLon}&end_lat={endLat}";
                var response = await _httpClient.PostAsync(url, null);

                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<RecommendationResponseDto>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                }
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to get recommendations: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get live traffic data
        /// </summary>
        public async Task<TrafficDataDto?> GetLiveTrafficAsync(int routeId)
        {
            try
            {
                var response = await _httpClient.GetAsync($"/traffic/live/{routeId}");
                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<TrafficDataDto>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                }
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to get traffic data: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Send a notification
        /// </summary>
        public async Task<bool> SendNotificationAsync(int? projectId, string recipientType, string message)
        {
            try
            {
                var notificationData = new
                {
                    project_id = projectId,
                    recipient_type = recipientType,
                    message = message
                };

                var json = JsonSerializer.Serialize(notificationData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync("/notifications/send", content);

                return response.IsSuccessStatusCode;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to send notification: {ex.Message}");
                return false;
            }
        }
    }

    // DTOs for communication

    public class ProjectDto
    {
        public int Id { get; set; }
        public string? Name { get; set; }
        public string? Description { get; set; }
        public string? Status { get; set; }
        public DateTime? CreatedAt { get; set; }
        public List<List<double>>? RouteCoordinates { get; set; }
        public double? EmissionReductionEstimate { get; set; }
        public string? StartTime { get; set; }
        public string? EndTime { get; set; }
        public double? StartLat { get; set; }
        public double? StartLon { get; set; }
        public double? EndLat { get; set; }
        public double? EndLon { get; set; }
        public string? ResourceAllocation { get; set; }
    }

    public class ProjectCreateDto
    {
        public required string Name { get; set; }
        public string? Status { get; set; }
        public DateTime? StartTime { get; set; }
        public DateTime? EndTime { get; set; }
        public double? StartLat { get; set; }
        public double? StartLon { get; set; }
        public double? EndLat { get; set; }
        public double? EndLon { get; set; }
    }

    public class ProjectUpdateDto
    {
        public string? Name { get; set; }
        public string? Status { get; set; }
        public DateTime? StartTime { get; set; }
        public DateTime? EndTime { get; set; }
    }

    public class RouteAnalysisDto
    {
        public double LengthDegrees { get; set; }
        public int NumSegments { get; set; }
        public double? ApproximateLengthKm { get; set; }
    }

    public class AlternativeRouteDto
    {
        public int RouteId { get; set; }
        public double LengthKm { get; set; }
        public int NumSegments { get; set; }
        public double SuitabilityScore { get; set; }
        public int Rank { get; set; }
    }

    public class RecommendationResponseDto
    {
        public int RouteId { get; set; }
        public int? RecommendedAlternativeId { get; set; }
        public List<AlternativeRouteDto>? AllAlternatives { get; set; }
        public string? RecommendationJustification { get; set; }
    }

    public class TrafficDataDto
    {
        public int RouteId { get; set; }
        public DateTime? Timestamp { get; set; }
        public int? VehicleCount { get; set; }
        public double? AverageSpeed { get; set; }
        public string? CongestionState { get; set; }
    }
}
