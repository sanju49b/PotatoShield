'use client'

// Simple PDF export function - can be enhanced with jsPDF or react-pdf
export function exportDashboardToPDF(data: any, location: string) {
  // Create a printable version
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    alert('Please allow popups to export PDF')
    return
  }

  const html = `
    <!DOCTYPE html>
    <html>
      <head>
        <title>Potato Disease Risk Report - ${location}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; background: white; color: black; }
          h1 { color: #f97316; }
          .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
          .risk-card { display: inline-block; margin: 10px; padding: 15px; border-radius: 8px; }
          .risk-high { background: #fee2e2; }
          .risk-moderate { background: #fef3c7; }
          .risk-low { background: #d1fae5; }
          table { width: 100%; border-collapse: collapse; margin: 10px 0; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background: #f3f4f6; }
        </style>
      </head>
      <body>
        <h1>🥔 Potato Disease Risk Report</h1>
        <p><strong>Location:</strong> ${location}</p>
        <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
        
        <div class="section">
          <h2>Disease Risk Summary</h2>
          <div class="risk-card risk-high">
            <strong>Late Blight:</strong> ${Math.round(data.disease_risks[0]?.late_blight_pct || 0)}%
          </div>
          <div class="risk-card risk-moderate">
            <strong>Early Blight:</strong> ${Math.round(data.disease_risks[0]?.early_blight_pct || 0)}%
          </div>
          <div class="risk-card risk-high">
            <strong>Overall Risk:</strong> ${Math.round(data.disease_risks[0]?.overall_pct || 0)}%
          </div>
        </div>

        <div class="section">
          <h2>8-Day Forecast</h2>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Temp (°C)</th>
                <th>Humidity (%)</th>
                <th>Soil (%)</th>
                <th>Risk (%)</th>
              </tr>
            </thead>
            <tbody>
              ${data.weather_data.map((day: any, i: number) => `
                <tr>
                  <td>${new Date(day.date).toLocaleDateString()}</td>
                  <td>${Math.round(day.temp_avg)}</td>
                  <td>${Math.round(day.humidity_avg)}</td>
                  <td>${Math.round((data.soil_data[i]?.soil_moisture_percent || 0) * 100)}</td>
                  <td>${Math.round(data.disease_risks[i]?.overall_pct || 0)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <div class="section">
          <h2>Recommendations</h2>
          <h3>Immediate Actions</h3>
          <ul>
            ${(data.recommendations?.immediate_actions || []).map((a: string) => `<li>${a}</li>`).join('')}
          </ul>
          <h3>Preventive Measures</h3>
          <ul>
            ${(data.recommendations?.preventive_measures || []).map((a: string) => `<li>${a}</li>`).join('')}
          </ul>
        </div>

        <div class="section">
          <h2>Weekly Outlook</h2>
          <p>${data.weekly_outlook?.risk_persistence || 'N/A'}</p>
          <p><strong>Critical Days:</strong> ${data.weekly_outlook?.critical_days?.join(', ') || 'None'}</p>
        </div>
      </body>
    </html>
  `

  printWindow.document.write(html)
  printWindow.document.close()
  printWindow.print()
}

