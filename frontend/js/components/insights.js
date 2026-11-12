/**
 * Component: Management Insights & Recurring Pattern Cards
 */

function renderPatternsAndInsights(patterns, insights) {
  const patternsDiv = document.getElementById('patternsContainer');
  const insightsDiv = document.getElementById('managementInsightsContainer');

  if (patternsDiv && patterns) {
    patternsDiv.innerHTML = patterns.map(p => `
      <div class="insight-card">
        <div style="font-size:11px; text-transform:uppercase; font-weight:700; color:var(--text-muted);">${p.pattern_type} \u2022 ${p.evidence_level}</div>
        <div class="insight-title">${p.pattern_name}</div>
        <div class="insight-body">
          <p><strong>Related Incidents:</strong> ${p.related_incident_ids.join(', ')}</p>
          <p style="margin-top:6px;">${p.possible_contributing_factors}</p>
        </div>
        <div class="insight-action">
          &#128161; Suggested Action: ${p.suggested_preventive_actions[0]}
        </div>
      </div>
    `).join('');
  }

  if (insightsDiv && insights) {
    insightsDiv.innerHTML = insights.map(i => `
      <div class="insight-card ${i.priority}">
        <div style="display:flex; justify-content:space-between; font-size:11px; text-transform:uppercase; font-weight:700; color:var(--text-muted);">
          <span>${i.category.toUpperCase()}</span>
          <span style="color:${i.priority === 'high' ? '#b91c1c' : '#b45309'}">${i.priority.toUpperCase()} PRIORITY</span>
        </div>
        <div class="insight-title">${i.title}</div>
        <div class="insight-body">${i.observation}</div>
        <div class="insight-action">
          &#127919; Recommendation: ${i.recommended_action}
        </div>
      </div>
    `).join('');
  }
}
