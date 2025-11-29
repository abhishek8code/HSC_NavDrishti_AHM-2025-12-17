using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;

namespace Traffic_Frontend.Controllers
{
    public class HomeController : Controller
    {
        private readonly IConfiguration _configuration;

        public HomeController(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public IActionResult Index()
        {
            ViewBag.MapboxAccessToken = _configuration["Mapbox:AccessToken"];
            return View();
        }

        public IActionResult Dashboard()
        {
            ViewBag.MapboxAccessToken = _configuration["Mapbox:AccessToken"];
            ViewBag.BackendApiUrl = _configuration["BackendApi:BaseUrl"] ?? "http://localhost:8000";
            return View();
        }

        public IActionResult EvidenceViewer(double? lat, double? lon)
        {
            ViewBag.Latitude = lat;
            ViewBag.Longitude = lon;
            ViewBag.BackendApiUrl = _configuration["BackendApi:BaseUrl"] ?? "http://localhost:8000";
            return View();
        }
    }
}

