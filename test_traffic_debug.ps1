$response = Invoke-RestMethod -Uri 'http://localhost:8002/traffic/live'
Write-Output "Total segments: $($response.segments.Count)"
Write-Output "Mock: $($response.mock)"
if ($response.segments.Count -gt 0) {
    Write-Output "First segment: $($response.segments[0].name)"
    Write-Output "Coordinates count: $($response.segments[0].coordinates.Count)"
    Write-Output "Congestion: $($response.segments[0].congestion_level)"
}
