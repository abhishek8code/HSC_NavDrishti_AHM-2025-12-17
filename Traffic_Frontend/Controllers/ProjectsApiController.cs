using Microsoft.AspNetCore.Mvc;
using Traffic_Frontend.Services;

namespace Traffic_Frontend.Controllers
{
    /// <summary>
    /// API Controller for project management, delegates to backend
    /// </summary>
    [ApiController]
    [Route("api/projects")]
    public class ProjectsApiController : ControllerBase
    {
        private readonly BackendApiService _backendApiService;
        private readonly ILogger<ProjectsApiController> _logger;

        public ProjectsApiController(BackendApiService backendApiService, ILogger<ProjectsApiController> logger)
        {
            _backendApiService = backendApiService;
            _logger = logger;
        }

        /// <summary>
        /// Get all projects from backend
        /// </summary>
        [HttpGet]
        public async Task<IActionResult> GetProjects()
        {
            try
            {
                var projects = await _backendApiService.GetProjectsAsync();
                return Ok(projects);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error fetching projects: {ex.Message}");
                return StatusCode(500, new { error = ex.Message });
            }
        }

        /// <summary>
        /// Get single project
        /// </summary>
        [HttpGet("{id}")]
        public async Task<IActionResult> GetProject(int id)
        {
            try
            {
                var project = await _backendApiService.GetProjectAsync(id);
                if (project == null)
                    return NotFound();
                return Ok(project);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error fetching project {id}: {ex.Message}");
                return StatusCode(500, new { error = ex.Message });
            }
        }

        /// <summary>
        /// Create a new project
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> CreateProject([FromBody] ProjectCreateDto project)
        {
            try
            {
                var result = await _backendApiService.CreateProjectAsync(project);
                if (result == null)
                    return BadRequest(new { error = "Failed to create project" });
                return CreatedAtAction(nameof(GetProject), new { id = result.Id }, result);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error creating project: {ex.Message}");
                return StatusCode(500, new { error = ex.Message });
            }
        }

        /// <summary>
        /// Update a project
        /// </summary>
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateProject(int id, [FromBody] ProjectUpdateDto project)
        {
            try
            {
                var result = await _backendApiService.UpdateProjectAsync(id, project);
                if (result == null)
                    return NotFound();
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error updating project {id}: {ex.Message}");
                return StatusCode(500, new { error = ex.Message });
            }
        }
    }
}
