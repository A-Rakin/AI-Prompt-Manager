/**
 * ==============================================================================
 * PromptForge - Analytics Chart.js Integration
 * ==============================================================================
 * Fetches JSON dataset from `/analytics/data` and initializes 5 interactive charts:
 * 1. Platform Usage Distribution (Doughnut Chart)
 * 2. Category Breakdown (Bar Chart)
 * 3. Favorite Percentage (Pie Chart)
 * 4. Monthly Prompts Created (Line Chart)
 * 5. Weekly Copy Velocity (Line Chart)
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  const analyticsContainer = document.getElementById('analyticsChartsContainer');
  if (!analyticsContainer || typeof Chart === 'undefined') return;

  // Chart configuration defaults matching PromptForge dark palette
  Chart.defaults.color = '#94A3B8';
  Chart.defaults.font.family = "'Inter', sans-serif";

  fetch('/analytics/data')
    .then(res => res.json())
    .then(data => {
      // 1. Platform Usage Doughnut Chart
      const ctxPlatform = document.getElementById('chartPlatformUsage')?.getContext('2d');
      if (ctxPlatform) {
        new Chart(ctxPlatform, {
          type: 'doughnut',
          data: {
            labels: data.platforms.labels,
            datasets: [{
              data: data.platforms.data,
              backgroundColor: ['#6366F1', '#EC4899', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#06B6D4', '#64748B'],
              borderWidth: 2,
              borderColor: '#1E293B'
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' }
            }
          }
        });
      }

      // 2. Category Breakdown Bar Chart
      const ctxCategory = document.getElementById('chartCategoryBreakdown')?.getContext('2d');
      if (ctxCategory) {
        new Chart(ctxCategory, {
          type: 'bar',
          data: {
            labels: data.categories.labels,
            datasets: [{
              label: 'Prompts Count',
              data: data.categories.data,
              backgroundColor: '#6366F1',
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
              x: { grid: { display: false } }
            }
          }
        });
      }

      // 3. Favorites Pie Chart
      const ctxFavorites = document.getElementById('chartFavorites')?.getContext('2d');
      if (ctxFavorites) {
        new Chart(ctxFavorites, {
          type: 'pie',
          data: {
            labels: data.favorites.labels,
            datasets: [{
              data: data.favorites.data,
              backgroundColor: ['#EC4899', '#334155'],
              borderColor: '#1E293B'
            }]
          },
          options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } }
          }
        });
      }

      // 4. Monthly Prompts Created Line Chart
      const ctxMonthly = document.getElementById('chartMonthlyCreated')?.getContext('2d');
      if (ctxMonthly) {
        new Chart(ctxMonthly, {
          type: 'line',
          data: {
            labels: data.monthly.labels,
            datasets: [{
              label: 'Prompts Created',
              data: data.monthly.data,
              borderColor: '#10B981',
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
              x: { grid: { display: false } }
            }
          }
        });
      }

      // 5. Weekly Copy Velocity Line Chart
      const ctxCopies = document.getElementById('chartCopyVelocity')?.getContext('2d');
      if (ctxCopies) {
        new Chart(ctxCopies, {
          type: 'line',
          data: {
            labels: data.copies.labels,
            datasets: [{
              label: 'Copies Per Day',
              data: data.copies.data,
              borderColor: '#F59E0B',
              backgroundColor: 'rgba(245, 158, 11, 0.15)',
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
              x: { grid: { display: false } }
            }
          }
        });
      }
    })
    .catch(err => console.error("Error loading analytics data:", err));
});
