/**
 * Component: Incident Records Table, Filters, Search & Modal Dossier
 */

function renderIncidentsTable(incidents) {
  const tbody = document.getElementById('incidentsTableBody');
  if (!tbody) return;

  if (!incidents || incidents.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:30px; color:#64748b;">No matching incident records found.</td></tr>';
    return;
  }

  let rows = '';
  incidents.forEach(item => {
    const id = item.incident_id || 'N/A';
    const narrative = item.input || '';
    const cat = item.predicted_category;
    const sev = item.predicted_severity;
    const score = item.risk_score || 0;
    const tags = item.risk_tags || [];

    rows += `
      <tr>
        <td style="font-weight:700; color:var(--primary);">${id}</td>
        <td class="narrative-col">${narrative}</td>
        <td><span class="badge badge-${cat}">${cat.replace('_', ' ')}</span></td>
        <td><span class="badge badge-${sev}">${sev}</span></td>
        <td style="font-weight:700; color:${getRiskColor(score)}">${score} / 100</td>
        <td>
          ${tags.slice(0, 3).map(t => `<span class="tag-chip">${t}</span>`).join('')}
          ${tags.length > 3 ? `<span class="tag-chip">+${tags.length-3}</span>` : ''}
        </td>
        <td>
          <button class="action-btn" onclick="openIncidentDetails('${id}')">View Details</button>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = rows;
}

function filterIncidentsTable() {
  const q = (document.getElementById('incidentSearch')?.value || '').toLowerCase();
  const cat = document.getElementById('categoryFilter')?.value || 'all';
  const sev = document.getElementById('severityFilter')?.value || 'all';

  const filtered = State.allIncidents.filter(item => {
    const textMatch = !q || item.input.toLowerCase().includes(q) || (item.incident_id && item.incident_id.toLowerCase().includes(q));
    const catMatch = cat === 'all' || item.predicted_category === cat;
    const sevMatch = sev === 'all' || item.predicted_severity === sev;
    return textMatch && catMatch && sevMatch;
  });

  renderIncidentsTable(filtered);
}

function openIncidentDetails(incidentId) {
  const incident = State.allIncidents.find(i => i.incident_id === incidentId);
  if (!incident) return;

  document.getElementById('modalIncidentId').textContent = `Incident ${incident.incident_id} \u2022 Deep AI Breakdown`;
  const modalBody = document.getElementById('modalIncidentBody');

  let tagsHtml = incident.risk_tags.map(t => `<span class="tag-chip" style="font-size:12px; padding:4px 10px;">${t}</span>`).join(' ');

  let recsImmediate = incident.recommendations.immediate_actions.map(a => `<li>${a}</li>`).join('');
  let recsPreventive = incident.recommendations.preventive_actions.map(a => `<li>${a}</li>`).join('');
  let recsLongTerm = incident.recommendations.long_term_actions.map(a => `<li>${a}</li>`).join('');

  let similarHtml = '';
  if (incident.similar_incidents && incident.similar_incidents.length > 0) {
    similarHtml = incident.similar_incidents.map(sim => `
      <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin-top:8px;">
        <div style="display:flex; justify-content:space-between; font-weight:700; font-size:12px; color:var(--primary);">
          <span>Past Case: ${sim.retrieved_incident_id} (${sim.category})</span>
          <span style="color:#047857;">Similarity: ${(sim.similarity_score * 100).toFixed(0)}%</span>
        </div>
        <div style="font-size:12px; color:#475569; margin:4px 0;">"${sim.original_narrative}"</div>
        <div style="font-size:11px; color:#64748b;"><em>${sim.relevance_explanation}</em></div>
      </div>
    `).join('');
  } else {
    similarHtml = '<div style="font-size:12px; color:#94a3b8;">No closely related past incidents found.</div>';
  }

  modalBody.innerHTML = `
    <!-- Original Report -->
    <div class="detail-card">
      <div class="detail-title">Original Incident Report</div>
      <p style="font-size:14px; font-weight:500;">"${incident.input}"</p>
    </div>

    <!-- Category & Severity Details -->
    <div class="detail-meta-grid">
      <div class="meta-item">
        <div class="meta-label">Predicted Category</div>
        <div class="meta-val"><span class="badge badge-${incident.predicted_category}">${incident.predicted_category}</span></div>
        <div style="font-size:11px; color:#64748b; margin-top:4px;">Reference: ${incident.reference_category || 'N/A'} (Confidence: ${(incident.category_confidence*100).toFixed(0)}%)</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Predicted Severity</div>
        <div class="meta-val"><span class="badge badge-${incident.predicted_severity}">${incident.predicted_severity}</span></div>
        <div style="font-size:11px; color:#64748b; margin-top:4px;">Reference: ${incident.reference_severity || 'N/A'} (Score: ${incident.risk_score}/100)</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Analysis Method</div>
        <div class="meta-val" style="font-size:13px;">${incident.classification_method}</div>
        <div style="font-size:11px; color:#64748b; margin-top:4px;">Rule matching & TF-IDF similarity</div>
      </div>
    </div>

    <!-- AI Summary & Structured Extraction -->
    <div class="detail-card">
      <div class="detail-title">Incident Summary</div>
      <p style="font-size:13.5px; color:#1e293b; margin-bottom:12px; line-height:1.6;">${incident.summary}</p>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:12px;">
        <div style="background:#f1f5f9; padding:8px 12px; border-radius:6px;">
          <strong>Main Hazard:</strong> ${incident.structured_summary.identified_hazard}
        </div>
        <div style="background:#f1f5f9; padding:8px 12px; border-radius:6px;">
          <strong>Likely Cause:</strong> ${incident.structured_summary.possible_contributing_factor}
        </div>
      </div>
    </div>

    <!-- Risk Factors & Tags -->
    <div class="detail-card">
      <div class="detail-title">Identified Risk Tags</div>
      <div style="margin-bottom:10px;">${tagsHtml}</div>
      <ul class="action-list">
        ${incident.risk_factors.map(f => `<li>${f}</li>`).join('')}
      </ul>
    </div>

    <!-- Recommendations -->
    <div class="detail-card" style="border-left:4px solid var(--accent-emerald);">
      <div class="detail-title">Recommended Action Plan</div>
      <div style="margin-bottom:12px;">
        <strong style="font-size:12px; color:#b91c1c;">&#128680; Immediate Actions (Do Now):</strong>
        <ul class="action-list">${recsImmediate}</ul>
      </div>
      <div style="margin-bottom:12px;">
        <strong style="font-size:12px; color:#c2410c;">&#128737;&#65039; Preventive Actions (Fix the Cause):</strong>
        <ul class="action-list">${recsPreventive}</ul>
      </div>
      <div>
        <strong style="font-size:12px; color:#047857;">&#128200; Long-Term Actions (Keep Site Safe):</strong>
        <ul class="action-list">${recsLongTerm}</ul>
      </div>
    </div>

    <!-- Similar Past Incidents -->
    <div class="detail-card">
      <div class="detail-title">Similar Past Incidents</div>
      ${similarHtml}
    </div>
  `;

  document.getElementById('incidentModal').classList.add('open');
}

function closeModal() {
  document.getElementById('incidentModal').classList.remove('open');
}

async function resetRecordsToBaseline() {
  if (!confirm("Reset all incident records back to the 6 baseline incidents?")) return;
  try {
    await Api.resetIncidents();
    await loadDashboard();
    alert("Records have been reset back to the 6 baseline incidents.");
  } catch (err) {
    alert("Failed to reset records: " + err.message);
  }
}
