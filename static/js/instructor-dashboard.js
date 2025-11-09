// ملف خفيف لإعداد الرسوم وفلتر التاريخ
document.addEventListener('DOMContentLoaded', function(){
  // بيانات ابتدائية جلبها من template context عبر عناصر data-*
  // إذا حبيت، يمكنك تغييرها لتأتي عبر AJAX Endpoints
  const revenueCtx = document.getElementById('revenueChart')?.getContext('2d');

  // data placeholders (if template passed arrays/update to fetch via ajax, adapt)
  const revenueLabels = window.revenue_labels || {{ revenue_labels_json|default:"[]" }};
  const revenueData = window.revenue_data || {{ revenue_data_json|default:"[]" }};

  // create chart if canvas exists
  if(revenueCtx){
    const revenueChart = new Chart(revenueCtx, {
      type: 'line',
      data: {
        labels: revenueLabels,
        datasets: [{
          label: 'إيرادات',
          data: revenueData,
          borderColor: '#0056D2',
          tension: 0.35,
          fill: true,
          backgroundColor: 'rgba(0,86,210,0.08)',
          pointRadius: 3
        }]
      },
      options:{
        responsive:true,
        maintainAspectRatio:false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: { beginAtZero:true }
        }
      }
    });
  }

  // filter range change (if you add an endpoint to update charts)
  const filterRange = document.getElementById('filterRange');
  if(filterRange){
    filterRange.addEventListener('change', function(){
      // example: call AJAX to refresh revenue chart and top lectures
      // fetch(`/lectures/api/instructor-stats/?days=${this.value}`)
      //   .then(r=>r.json()).then(updateDashboardWith)
      //   .catch(err=>console.error(err));
      // for now show tiny feedback
      const val = this.value;
      const btn = document.createElement('span');
      btn.className = 'badge bg-light text-muted ms-2';
      btn.innerText = 'تحديث...';
      this.parentNode.appendChild(btn);
      setTimeout(()=>btn.remove(), 700);
    });
  }
});
