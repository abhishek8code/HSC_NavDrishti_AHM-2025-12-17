using Microsoft.AspNetCore.SignalR;

namespace Traffic_Frontend.Hubs
{
    public class DashboardHub : Hub
    {
        public async Task SendDashboardUpdate(object data)
        {
            await Clients.All.SendAsync("UpdateDashboard", data);
        }
    }
}

