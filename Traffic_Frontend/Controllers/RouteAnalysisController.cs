using Microsoft.AspNetCore.Mvc;
using Traffic_Frontend.Services;

namespace Traffic_Frontend.Controllers
{
    /// <summary>
    /// Controller for route analysis views and operations
    /// </summary>
    public class RouteAnalysisController : Controller
    {
        private readonly BackendApiService _backendApiService;
        private readonly ILogger<RouteAnalysisController> _logger;
        private readonly IConfiguration _configuration;

        public RouteAnalysisController(
            BackendApiService backendApiService, 
            ILogger<RouteAnalysisController> logger,
            IConfiguration configuration)
        {
            _backendApiService = backendApiService;
            _logger = logger;
            _configuration = configuration;
        }

        /// <summary>
        /// Display route analysis page with map
        /// </summary>
        public IActionResult Index(int? projectId = null)
        {
            ViewBag.MapboxAccessToken = _configuration["Mapbox:AccessToken"];
            ViewBag.BackendApiUrl = _configuration["BackendApi:BaseUrl"] ?? "http://localhost:8000";
            ViewBag.ProjectId = projectId;
            return View();
        }

        /// <summary>
        /// Get recommendations for a route
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> GetRecommendations(
            int routeId,
            [FromBody] RouteCoordinatesRequest request)
        {
            try
            {
                if (request?.Coordinates == null || request.Coordinates.Count < 2)
                {
                    return BadRequest(new { error = "At least 2 coordinates required (start and end)" });
                }

                var result = await _backendApiService.GetRecommendationsAsync(
                    routeId,
                    request.Coordinates[0][0],  // startLon
                    request.Coordinates[0][1],  // startLat
                    request.Coordinates[1][0],  // endLon
                    request.Coordinates[1][1]   // endLat
                );

                if (result == null)
                    return BadRequest(new { error = "Failed to get recommendations" });

                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error getting recommendations: {ex.Message}");
                return StatusCode(500, new { error = ex.Message });
            }
        }

        /// <summary>
        /// Analyze a route
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> AnalyzeRoute([FromBody] RouteCoordinatesRequest request)
        {
            try
            {
                if (request?.Coordinates == null || request.Coordinates.Count == 0)
                {
                    return BadRequest(new { error = "Coordinates required" });
                }

                var result = await _backendApiService.AnalyzeRouteAsync(request.Coordinates);
                if (result == null)
                    return BadRequest(new { error = "Failed to analyze route" });

                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error analyzing route: {ex.Message}");
                return StatusCode(500, new { error = ex.Message });
            }
        }
    }

    public class RouteCoordinatesRequest
    {
        public required List<List<double>> Coordinates { get; set; }
    }
}
