/**
 * App Configuration, Global State Store, and Presets
 */

const State = {
  allIncidents: [],
  dashboardData: null,
  evaluationData: null
};

// Preset examples for Live Analysis Studio
const PRESETS = [
  "Contractor slipped near wet walkway at solar block, minor injury, housekeeping issue",
  "Severe synthetic gear oil leakage discovered beneath nacelle during scheduled wind turbine gearbox servicing",
  "Near miss: vehicle movement close to cable trench during night shift without banksman",
  "PPE non-compliance observed during panel cleaning activity atop solar tracker array",
  "Repeated waste segregation deviation at contractor storage area with co-mingled oily rags",
  "Major electrical fire and explosion in 33kV outdoor switchyard transformer with heavy smoke"
];

// Presets for the on-demand "Test AI" component
const TEST_PRESETS = [
  { text: "Worker observed working atop 5-meter solar mounting structure without wearing safety harness or helmet.", cat: "safety", sev: "high" },
  { text: "Severe synthetic gear oil leakage discovered beneath nacelle during scheduled wind turbine gearbox servicing.", cat: "environment", sev: "high" },
  { text: "Audit non-conformance: repeated co-mingling of hazardous oily rags with municipal cardboard waste in contractor yard.", cat: "esg_compliance", sev: "low" },
  { text: "Contractor slipped on wet tiled floor in inverter control room, suffering a minor bruise on the elbow.", cat: "safety", sev: "medium" },
  { text: "Major electrical fire and explosion in 33kV outdoor switchyard transformer with heavy smoke; fire brigade called.", cat: "safety", sev: "critical" }
];

function getRiskColor(score) {
  if (score >= 85) return '#b91c1c';
  if (score >= 65) return '#c2410c';
  if (score >= 40) return '#b45309';
  return '#15803d';
}
