/**
 * Component: Native SVG Charts & Risk Matrix Heatmap
 */

function renderCharts(data) {
  if (!data) return;
  renderCategoryDoughnut(data.category_distribution);
  renderSeverityBar(data.severity_distribution);
  renderRiskTagBars(data.risk_tag_distribution);
  renderRiskMatrixHeatmap(data.risk_matrix);
}

function renderCategoryDoughnut(dist) {
  const svg = document.getElementById('categoryChart');
  const legend = document.getElementById('categoryLegend');
  if (!svg || !dist) return;

  const total = Object.values(dist).reduce((a, b) => a + b, 0);
  if (total === 0) return;

  const colors = { safety: '#3b82f6', environment: '#10b981', esg_compliance: '#8b5cf6' };
  const labels = { safety: 'Safety', environment: 'Environment', esg_compliance: 'ESG Compliance' };

  let startAngle = 0;
  let svgHtml = '';
  let legendHtml = '';

  Object.entries(dist).forEach(([cat, val]) => {
    if (val === 0) return;
    const sliceAngle = (val / total) * 360;
    const endAngle = startAngle + sliceAngle;
    const color = colors[cat] || '#64748b';

    const r = 70;
    const cx = 150;
    const cy = 100;
    const rad1 = (startAngle - 90) * Math.PI / 180;
    const rad2 = (endAngle - 90) * Math.PI / 180;

    const x1 = cx + r * Math.cos(rad1);
    const y1 = cy + r * Math.sin(rad1);
    const x2 = cx + r * Math.cos(rad2);
    const y2 = cy + r * Math.sin(rad2);

    const largeArc = sliceAngle > 180 ? 1 : 0;
    const pathData = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`;

    svgHtml += `<path d="${pathData}" fill="${color}" stroke="#ffffff" stroke-width="2"><title>${labels[cat] || cat}: ${val} (${Math.round((val/total)*100)}%)</title></path>`;

    legendHtml += `
      <div class="legend-item">
        <span class="legend-color" style="background:${color}"></span>
        <span>${labels[cat] || cat}: <strong>${val}</strong></span>
      </div>
    `;

    startAngle = endAngle;
  });

  // Center cutout for donut chart
  svgHtml += `<circle cx="150" cy="100" r="42" fill="#ffffff" />`;
  svgHtml += `<text x="150" y="97" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">${total}</text>`;
  svgHtml += `<text x="150" y="112" text-anchor="middle" font-size="10" fill="#64748b">INCIDENTS</text>`;

  svg.innerHTML = svgHtml;
  if (legend) legend.innerHTML = legendHtml;
}

function renderSeverityBar(dist) {
  const svg = document.getElementById('severityChart');
  const legend = document.getElementById('severityLegend');
  if (!svg || !dist) return;

  const colors = { low: '#10b981', medium: '#f59e0b', high: '#f97316', critical: '#ef4444' };
  const labels = ['low', 'medium', 'high', 'critical'];
  const maxVal = Math.max(...Object.values(dist), 1);

  let svgHtml = '';
  let legendHtml = '';
  const barWidth = 44;
  const spacing = 68;
  const startX = 26;
  const chartBottom = 155;
  const maxBarHeight = 110;

  labels.forEach((sev, i) => {
    const val = dist[sev] || 0;
    const barHeight = (val / maxVal) * maxBarHeight;
    const x = startX + i * spacing;
    const y = chartBottom - barHeight;
    const color = colors[sev];

    svgHtml += `
      <rect x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" fill="${color}" rx="5">
        <title>${sev.toUpperCase()}: ${val}</title>
      </rect>
      <text x="${x + barWidth/2}" y="${y - 8}" text-anchor="middle" font-size="13" font-weight="800" fill="#0f172a">${val}</text>
      <text x="${x + barWidth/2}" y="${chartBottom + 18}" text-anchor="middle" font-size="11.5" fill="#475569" font-weight="700">${sev.toUpperCase()}</text>
    `;

    legendHtml += `
      <div class="legend-item">
        <span class="legend-color" style="background:${color}"></span>
        <span>${sev.charAt(0).toUpperCase() + sev.slice(1)}: <strong>${val}</strong></span>
      </div>
    `;
  });

  svgHtml += `<line x1="16" y1="${chartBottom}" x2="284" y2="${chartBottom}" stroke="#cbd5e1" stroke-width="1.5" />`;

  svg.innerHTML = svgHtml;
  if (legend) legend.innerHTML = legendHtml;
}

function renderRiskTagBars(tagDist) {
  const svg = document.getElementById('riskTagChart');
  if (!svg || !tagDist) return;

  const entries = Object.entries(tagDist).sort((a, b) => b[1] - a[1]).slice(0, 5);
  if (entries.length === 0) return;

  const maxVal = Math.max(...entries.map(e => e[1]), 1);
  let svgHtml = '';
  const barHeight = 20;
  const startY = 16;
  const rowGap = 36;
  const maxBarWidth = 135;
  const barStartX = 145;

  entries.forEach(([tag, val], idx) => {
    const y = startY + idx * rowGap;
    const width = Math.max((val / maxVal) * maxBarWidth, 8);

    svgHtml += `
      <text x="10" y="${y + 15}" font-size="11.5" font-weight="600" fill="#1e293b">${tag}</text>
      <rect x="${barStartX}" y="${y}" width="${maxBarWidth}" height="${barHeight}" fill="#f1f5f9" rx="4"></rect>
      <rect x="${barStartX}" y="${y}" width="${width}" height="${barHeight}" fill="#0f3d2e" rx="4"></rect>
      <text x="${barStartX + width + 10}" y="${y + 15}" font-size="13" font-weight="800" fill="#0f172a">${val}</text>
    `;
  });

  svg.innerHTML = svgHtml;
}

function renderRiskMatrixHeatmap(matrix) {
  const container = document.getElementById('matrixContainer');
  if (!container || !matrix) return;

  const categories = [
    { key: 'safety', label: 'Safety' },
    { key: 'environment', label: 'Environment' },
    { key: 'esg_compliance', label: 'ESG Compliance' }
  ];
  const severities = ['low', 'medium', 'high', 'critical'];

  let html = '<div class="matrix-container">';
  html += '<table class="matrix-table">';
  html += '<thead><tr>';
  html += '<th class="matrix-corner">Category</th>';
  severities.forEach(s => {
    html += `<th>${s.charAt(0).toUpperCase() + s.slice(1)}</th>`;
  });
  html += '</tr></thead><tbody>';

  categories.forEach(catObj => {
    const cat = catObj.key;
    html += `<tr><td class="cat-label">${catObj.label}</td>`;
    severities.forEach(sev => {
      const count = matrix[cat] && matrix[cat][sev] ? matrix[cat][sev] : 0;
      let cellBg = '#f8fafc';
      let textColor = '#94a3b8';
      let fontBold = '600';
      let border = '1px solid #e2e8f0';

      if (count > 0) {
        fontBold = '800';
        if (sev === 'critical') {
          cellBg = '#fee2e2';
          textColor = '#b91c1c';
          border = '1px solid #fca5a5';
        } else if (sev === 'high') {
          cellBg = '#ffedd5';
          textColor = '#c2410c';
          border = '1px solid #fdba74';
        } else if (sev === 'medium') {
          cellBg = '#fef3c7';
          textColor = '#b45309';
          border = '1px solid #fcd34d';
        } else {
          cellBg = '#dcfce7';
          textColor = '#15803d';
          border = '1px solid #86efac';
        }
      }
      html += `<td class="count-cell" style="background:${cellBg}; color:${textColor}; font-weight:${fontBold}; border:${border};">${count}</td>`;
    });
    html += '</tr>';
  });

  html += '</tbody></table></div>';
  container.innerHTML = html;
}
