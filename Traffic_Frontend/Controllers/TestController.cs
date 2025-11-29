using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.SignalR;
using Traffic_Frontend.Hubs;

namespace Traffic_Frontend.Controllers
{
    /// <summary>
    /// Test controller for sending sample dashboard updates via SignalR
    /// This can be used for testing the dashboard functionality
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class TestController : ControllerBase
    {
        private readonly IHubContext<DashboardHub> _hubContext;

        public TestController(IHubContext<DashboardHub> hubContext)
        {
            _hubContext = hubContext;
        }

        /// <summary>
        /// Send a test dashboard update
        /// POST /api/test/dashboard-update
        /// </summary>
        [HttpPost("dashboard-update")]
        public async Task<IActionResult> SendDashboardUpdate([FromBody] DashboardUpdateData data)
        {
            await _hubContext.Clients.All.SendAsync("UpdateDashboard", data);
            return Ok(new { message = "Dashboard update sent", data });
        }

        /// <summary>
        /// Send sample heatmap data
        /// POST /api/test/heatmap-data
        /// Body: Array of {lat, lon, severity}
        /// </summary>
        [HttpPost("heatmap-data")]
        public async Task<IActionResult> SendHeatmapData([FromBody] object heatmapData)
        {
            var updateData = new
            {
                heatmapData = heatmapData
            };
            await _hubContext.Clients.All.SendAsync("UpdateDashboard", updateData);
            return Ok(new { message = "Heatmap data sent", data = heatmapData });
        }

        /// <summary>
        /// Send traffic line updates
        /// POST /api/test/traffic-lines
        /// Body: { lines: [{ id, coordinates: [[lng, lat], ...], flowStability: "stable|unstable|congested" }] }
        /// </summary>
        [HttpPost("traffic-lines")]
        public async Task<IActionResult> SendTrafficLines([FromBody] TrafficLinesData data)
        {
            await _hubContext.Clients.All.SendAsync("UpdateTrafficLines", data);
            return Ok(new { message = "Traffic lines update sent", data });
        }
    }

    public class TrafficLinesData
    {
        public TrafficLineDto[] Lines { get; set; } = Array.Empty<TrafficLineDto>();
    }

    public class TrafficLineDto
    {
        public string Id { get; set; } = string.Empty;
        public double[][] Coordinates { get; set; } = Array.Empty<double[]>();
        public string FlowStability { get; set; } = "stable"; // stable, unstable, congested
        public Dictionary<string, object>? Properties { get; set; }
    }

    public class DashboardUpdateData
    {
        public int? ActiveProjects { get; set; }
        public int? CriticalAlerts { get; set; }
        public double? Co2Saved { get; set; }
        public object? HeatmapData { get; set; }
    }
}

