/**
 * Component: Live Incident Analysis Studio
 */

function loadPreset(idx) {
  const el = document.getElementById('liveInputNarrative');
  if (el && PRESETS[idx]) {
    el.value = PRESETS[idx];
  }
}

async function submitLiveAnalysis() {
  const text = document.getElementById('liveInputNarrative').value.trim();
  if (!text) {
    alert("Please enter or select an incident narrative to analyze.");
    return;
  }

  const btn = document.getElementById('btnAnalyze');
  const loading = document.getElementById('studioLoading');
  if (btn) btn.disabled = true;
  if (loading) loading.style.display = 'inline';

  try {
    const data = await Api.analyzeIncident(text, true);

    // Reload dashboard so KPI count, table, and charts refresh immediately
    await loadDashboard();

    // Render results
    renderLiveAnalysisResult(data);
  } catch (err) {
    alert("Error analyzing narrative: " + err.message);
  } finally {
    if (btn) btn.disabled = false;
    if (loading) loading.style.display = 'none';
  }
}

function switchTabAndHighlight(incidentId) {
  switchTab('incidents');
  const searchBox = document.getElementById('incidentSearch');
  if (searchBox && incidentId) {
    searchBox.value = incidentId;
    filterIncidentsTable();
  }
}

function renderLiveAnalysisResult(data) {
  const emptyState = document.getElementById('studioEmptyState');
  if (emptyState) emptyState.style.display = 'none';

  const container = document.getElementById('studioResultContent');
  if (!container) return;
  container.style.display = 'block';

  let tagsHtml = data.risk_tags.map(t => `<span class="tag-chip" style="font-size:12px;">${t}</span>`).join(' ');

  let recsImmediate = data.recommendations.immediate_actions.map(a => `<li>${a}</li>`).join('');
  let recsPreventive = data.recommendations.preventive_actions.map(a => `<li>${a}</li>`).join('');
  let recsLongTerm = data.recommendations.long_term_actions.map(a => `<li>${a}</li>`).join('');

  let similarHtml = data.similar_incidents.map(sim => `
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px; margin-top:6px; font-size:12px;">
      <div style="display:flex; justify-content:space-between; font-weight:700;">
        <span style="color:var(--primary);">${sim.retrieved_incident_id} (${sim.category})</span>
        <span style="color:#047857;">Similarity: ${(sim.similarity_score * 100).toFixed(0)}%</span>
      </div>
      <div style="color:#475569; margin:2px 0;">"${sim.original_narrative}"</div>
    </div>
  `).join('');

  let savedBanner = '';
  if (data.added_to_records && data.incident_id) {
    savedBanner = `
      <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:8px; padding:12px 16px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <div>
          <div style="font-weight:700; color:#065f46; font-size:13px;">&#9989; Incident Saved as ${data.incident_id}</div>
          <div style="font-size:12px; color:#047857;">Added to past records. Dashboard incident count increased to <strong>${data.total_incidents || State.allIncidents.length}</strong>.</div>
        </div>
        <button class="action-btn" style="background:#059669; font-size:12px; padding:6px 14px;" onclick="switchTabAndHighlight('${data.incident_id}')">&#128203; View in Incident Records</button>
      </div>
    `;
  }

  container.innerHTML = `
    ${savedBanner}
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
      <div>
        <span class="badge badge-${data.predicted_category}" style="font-size:13px; margin-right:6px;">${data.predicted_category.toUpperCase()}</span>
        <span class="badge badge-${data.predicted_severity}" style="font-size:13px;">${data.predicted_severity.toUpperCase()}</span>
      </div>
      <span style="font-size:12px; font-weight:600; color:var(--text-muted);">${data.incident_id ? 'ID: ' + data.incident_id : data.classification_method}</span>
    </div>

    <div style="background:#f8fafc; border-radius:8px; padding:12px; border:1px solid #e2e8f0; margin-bottom:14px;">
      <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:700;">
        <span>Risk Score: ${data.risk_score} / 100</span>
        <span style="color:${getRiskColor(data.risk_score)}">${data.requires_immediate_attention ? '&#9888;&#65039; REQUIRES IMMEDIATE ATTENTION' : 'Standard Priority'}</span>
      </div>
      <div class="gauge-wrap">
        <div class="gauge-bar-bg">
          <div class="gauge-bar-fill" style="width:${data.risk_score}%; background:${getRiskColor(data.risk_score)};"></div>
        </div>
      </div>
    </div>

    <div class="detail-card" style="margin-bottom:14px;">
      <div class="detail-title">Incident Summary</div>
      <p style="font-size:13.5px; line-height:1.5; color:#1e293b; margin-bottom:8px;">${data.summary}</p>
      <div style="font-size:12px; color:#64748b;">
        <div><strong>Main Hazard:</strong> ${data.structured_summary.identified_hazard}</div>
        <div><strong>Likely Cause:</strong> ${data.structured_summary.possible_contributing_factor}</div>
      </div>
    </div>

    <div class="detail-card" style="margin-bottom:14px;">
      <div class="detail-title">Identified Risk Tags</div>
      <div>${tagsHtml}</div>
    </div>

    <div class="detail-card" style="margin-bottom:14px; border-left:4px solid var(--accent-emerald);">
      <div class="detail-title">Recommended Actions</div>
      <div>
        <strong style="font-size:12px; color:#b91c1c;">Immediate Actions (Do Now):</strong>
        <ul class="action-list">${recsImmediate}</ul>
      </div>
      <div style="margin-top:8px;">
        <strong style="font-size:12px; color:#c2410c;">Preventive Actions (Fix the Cause):</strong>
        <ul class="action-list">${recsPreventive}</ul>
      </div>
      <div style="margin-top:8px;">
        <strong style="font-size:12px; color:#047857;">Long-Term Actions (Keep Site Safe):</strong>
        <ul class="action-list">${recsLongTerm}</ul>
      </div>
    </div>

    <div class="detail-card">
      <div class="detail-title">Similar Past Incidents</div>
      ${similarHtml || '<p style="font-size:12px; color:#94a3b8;">No matching past cases.</p>'}
    </div>
  `;
}
