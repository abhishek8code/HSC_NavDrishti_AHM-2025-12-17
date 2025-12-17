using Microsoft.AspNetCore.Mvc;
using Traffic_Frontend.Services;

namespace Traffic_Frontend.Controllers
{
    public class ProjectsController : Controller
    {
        private readonly BackendApiService _backendApiService;
        private readonly ILogger<ProjectsController> _logger;

        public ProjectsController(BackendApiService backendApiService, ILogger<ProjectsController> logger)
        {
            _backendApiService = backendApiService;
            _logger = logger;
        }

        public async Task<IActionResult> Index()
        {
            try
            {
                var projects = await _backendApiService.GetProjectsAsync();
                ViewBag.Projects = projects ?? new List<ProjectDto>();
            }
            catch (Exception ex)
            {
                _logger.LogError($"Failed to fetch projects: {ex.Message}");
                ViewBag.Projects = new List<ProjectDto>();
            }

            return View();
        }
    }
}
