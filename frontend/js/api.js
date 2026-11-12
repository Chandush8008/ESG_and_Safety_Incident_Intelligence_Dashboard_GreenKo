/**
 * Centralized API Service for Backend Communication
 */

const Api = {
  async getDashboard() {
    const res = await fetch('/api/dashboard');
    if (!res.ok) throw new Error('Failed to load dashboard metrics');
    return await res.json();
  },

  async getIncidents() {
    const res = await fetch('/api/incidents');
    if (!res.ok) throw new Error('Failed to load incident records');
    const data = await res.json();
    return Array.isArray(data) ? data : (data.incidents || []);
  },

  async getEvaluation() {
    const res = await fetch('/api/evaluation');
    if (!res.ok) throw new Error('Failed to load evaluation results');
    return await res.json();
  },

  async analyzeIncident(text, addToRecords = true) {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, add_to_records: addToRecords })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Analysis request failed');
    }
    return await res.json();
  },

  async resetIncidents() {
    const res = await fetch('/api/incidents/reset', { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset records');
    return await res.json();
  }
};
