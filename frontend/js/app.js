/**
 * Application Entrypoint & Main Controller
 * Coordinates UI components, tab switching, and initial data loading.
 */

function switchTab(tabId) {
  // Update nav buttons
  const navButtons = document.querySelectorAll('.nav-btn');
  navButtons.forEach(btn => {
    if (btn.dataset.tab === tabId) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Update tab panes
  const tabPanes = document.querySelectorAll('.tab-pane');
  tabPanes.forEach(pane => {
    if (pane.id === `tab-${tabId}`) {
      pane.classList.add('active');
    } else {
      pane.classList.remove('active');
    }
  });

  // If opening evaluation or benchmark tab, load evaluation data
  if (tabId === 'evaluation' && !State.evaluationData) {
    loadEvaluation();
  }
}

async function loadDashboard() {
  try {
    const dashData = await Api.getDashboard();
    State.dashboardData = dashData;

    const incidents = await Api.getIncidents();
    State.allIncidents = incidents;

    // Update status badge
    const badge = document.getElementById('statusBadge');
    if (badge) {
      badge.textContent = `\u25cf System Online \u2022 ${incidents.length} Incidents Loaded`;
    }

    // Render components
    renderKPIs(dashData.kpis);
    renderCharts(dashData);
    renderIncidentsTable(incidents);
    renderPatternsAndInsights(dashData.recurring_patterns, dashData.management_insights);

    return dashData;
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
  }
}

// Global initialization
window.addEventListener('DOMContentLoaded', async () => {
  // Attach search and filter events
  const searchInput = document.getElementById('incidentSearch');
  if (searchInput) {
    searchInput.addEventListener('input', filterIncidentsTable);
  }

  const catFilter = document.getElementById('categoryFilter');
  if (catFilter) {
    catFilter.addEventListener('change', filterIncidentsTable);
  }

  const sevFilter = document.getElementById('severityFilter');
  if (sevFilter) {
    sevFilter.addEventListener('change', filterIncidentsTable);
  }

  // Modal backdrop close
  const modal = document.getElementById('incidentModal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target.id === 'incidentModal') {
        closeModal();
      }
    });
  }

  // Escape key closes modal
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeModal();
    }
  });

  // Load initial dashboard metrics & records
  await loadDashboard();
});
