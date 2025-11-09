// student_dashboard.js
document.addEventListener('DOMContentLoaded', function () {
  // Chart: تقدم أسبوعي (data via endpoint)
  const ctx = document.getElementById('progressChart');
  if (!ctx) return;

  fetch('/users/api/progress_weekly/')  // endpoint سنتضيفه في urls/views
    .then(res => res.json())
    .then(data => {
      const labels = data.labels; // مثال: ["Mon","Tue",...]
      const values = data.values; // نسب مئوية
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'التقدم اليومي (%)',
            data: values,
            fill: true,
            tension: 0.35,
            pointRadius: 3,
            borderWidth: 2,
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      });
    })
    .catch(err => {
      console.error('Failed to load progress chart:', err);
    });
});
