/**
 * Component: KPI Cards Renderer
 */

function renderKPIs(kpis) {
  if (!kpis) return;
  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setEl('kpiTotal', kpis.total_incidents);
  setEl('kpiSafety', kpis.safety_incidents);
  setEl('kpiEnv', kpis.environment_incidents);
  setEl('kpiCompliance', kpis.esg_compliance_incidents);
  setEl('kpiHighRisk', kpis.high_critical_incidents);
  setEl('kpiPatterns', kpis.recurring_patterns_count);
}
