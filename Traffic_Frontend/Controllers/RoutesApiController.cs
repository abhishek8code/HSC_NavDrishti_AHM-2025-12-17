using Microsoft.AspNetCore.Mvc;
using Traffic_Frontend.Services;

namespace Traffic_Frontend.Controllers
{
    /// <summary>
    /// API Controller for route analysis, delegates to backend
    /// </summary>
    [ApiController]
    [Route("api/routes")]
    public class RoutesApiController : ControllerBase
    {
        private readonly BackendApiService _backendApiService;
        private readonly ILogger<RoutesApiController> _logger;

        public RoutesApiController(BackendApiService backendApiService, ILogger<RoutesApiController> logger)
        {
            _backendApiService = backendApiService;
            _logger = logger;
        }

        /// <summary>
        /// Analyze a route given coordinates
        /// </summary>
        [HttpPost("analyze")]
        public async Task<IActionResult> AnalyzeRoute([FromBody] AnalyzeRouteRequest request)
        {
            try
            {
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

        /// <summary>
        /// Get route recommendations
        /// </summary>
        [HttpPost("{routeId}/recommend")]
        public async Task<IActionResult> RecommendRoute(int routeId, [FromQuery] double startLon, [FromQuery] double startLat, [FromQuery] double endLon, [FromQuery] double endLat)
        {
            try
            {
                var result = await _backendApiService.GetRecommendationsAsync(routeId, startLon, startLat, endLon, endLat);
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
        /// Get live traffic data for a route
        /// </summary>
        [HttpGet("{routeId}/traffic")]
        public async Task<IActionResult> GetTraffic(int routeId)
        {
            try
            {
                var result = await _backendApiService.GetLiveTrafficAsync(routeId);
                if (result == null)
                    return NotFound();
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error getting traffic data: {ex.Message}");
                return StatusCode(500, new { error = ex.Message });
            }
        }
    }

    public class AnalyzeRouteRequest
    {
        public required List<List<double>> Coordinates { get; set; }
    }
}
