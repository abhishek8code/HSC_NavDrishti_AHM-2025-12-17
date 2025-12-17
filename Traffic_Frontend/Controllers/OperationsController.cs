using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Traffic_Frontend.Services;

namespace Traffic_Frontend.Controllers
{
    public class OperationsController : Controller
    {
        private readonly IConfiguration _configuration;
        private readonly BackendApiService _backendApiService;
        private readonly ILogger<OperationsController> _logger;

        public OperationsController(IConfiguration configuration, BackendApiService backendApiService, ILogger<OperationsController> logger)
        {
            _configuration = configuration;
            _backendApiService = backendApiService;
            _logger = logger;
        }

        public IActionResult Index()
        {
            ViewBag.MapboxAccessToken = _configuration["Mapbox:AccessToken"];
            ViewBag.BackendApiUrl = _configuration["BackendApi:BaseUrl"] ?? "http://localhost:8002";
            return View();
        }
    }
}
