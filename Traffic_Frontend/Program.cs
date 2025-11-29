using Pomelo.EntityFrameworkCore.MySql.Infrastructure;
using Microsoft.EntityFrameworkCore;
var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();
builder.Services.AddControllers(); // For API controllers
builder.Services.AddSignalR();
// Register DbContext for EF Core
builder.Services.AddDbContext<Traffic_Frontend.Models.NavDrishtiDbContext>(options =>
    options.UseMySql(
        builder.Configuration.GetConnectionString("NavDrishtiDb"),
        new MySqlServerVersion(new Version(8, 0, 0))
    )
);

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}
else
{
    // Disable HTTPS redirection in development
    // app.UseHttpsRedirection();
}
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.MapControllers(); // Map API controllers

app.MapHub<Traffic_Frontend.Hubs.DashboardHub>("/dashboardHub");

app.Run();

