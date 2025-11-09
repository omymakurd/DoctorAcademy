document.addEventListener('DOMContentLoaded', function(){

  // === Sidebar toggle for small screens ===
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  sidebarToggle?.addEventListener('click', () => {
    sidebar?.classList.toggle('open');
  });

  // === Theme toggle ===
  const themeToggle = document.getElementById('themeToggle');
  themeToggle?.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    themeToggle.querySelector('i')?.classList.toggle('bi-moon-fill');
    themeToggle.querySelector('i')?.classList.toggle('bi-sun-fill');
  });

  // === AOS animations ===
  if(window.AOS) AOS.init({ duration: 600, once: true });

  // === Revenue Chart ===
  const revenueCtx = document.getElementById('revenueChart')?.getContext('2d');
  const revenueLabels = window.revenue_labels || [];
  const revenueData = window.revenue_data || [];

  if(revenueCtx){
    new Chart(revenueCtx, {
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
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero:true } }
      }
    });
  }

  // === Filter range change ===
  const filterRange = document.getElementById('filterRange');
  if(filterRange){
    filterRange.addEventListener('change', function(){
      const val = this.value;
      const badge = document.createElement('span');
      badge.className = 'badge bg-light text-muted ms-2';
      badge.innerText = 'تحديث...';
      this.parentNode.appendChild(badge);
      setTimeout(()=>badge.remove(), 700);
    });
  }

});
