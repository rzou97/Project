export const API_BASE_URL = '/api';

export const API_ENDPOINTS = {
  connexion: `${API_BASE_URL}/auth/login/`,
  rafraichirToken: `${API_BASE_URL}/auth/refresh/`,
  inscription: `${API_BASE_URL}/accounts/register/`,
  compteMe: `${API_BASE_URL}/accounts/me/`,
  activationCompteBase: `${API_BASE_URL}/accounts/activate/`,

  kpiTesteursFpyInstant: `${API_BASE_URL}/kpi/testers-fpy-instant/`,
  kpiStatutTesteurs: `${API_BASE_URL}/kpi/testers-current-status/`,
  kpiTauxPannesActuel: `${API_BASE_URL}/kpi/current-failure-rate/`,

  cartes: `${API_BASE_URL}/boards/`,
  resultatsTest: `${API_BASE_URL}/test-results/`,
  gestionPannes: `${API_BASE_URL}/failure-cases/`,

  ticketsReparation: `${API_BASE_URL}/repairs/tickets/`,
  actionsReparation: `${API_BASE_URL}/repairs/actions/`,

  maintenance: `${API_BASE_URL}/maintenance/`,
  piecesRechange: `${API_BASE_URL}/pdr/`,
  piecesRechangeParts: `${API_BASE_URL}/pdr/parts/`,
  piecesRechangeStocks: `${API_BASE_URL}/pdr/stocks/`,
  piecesRechangeMouvements: `${API_BASE_URL}/pdr/movements/`,
  etalonnage: `${API_BASE_URL}/calibration/`,
  etalonnageInstruments: `${API_BASE_URL}/calibration/instruments/`,
  etalonnageRecords: `${API_BASE_URL}/calibration/records/`,
  alertes: `${API_BASE_URL}/alerts/`,

  historiqueReparation: `${API_BASE_URL}/intelligence/repair-history/`,
  proceduresReparation: `${API_BASE_URL}/intelligence/repair-procedure-templates/`,
  predictionsReparation: `${API_BASE_URL}/intelligence/repair-predictions/`,
};
