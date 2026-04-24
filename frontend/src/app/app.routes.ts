import { Routes } from '@angular/router';
import { authGuard } from './coeur/gardes/auth-guard';
import { ROUTE_PATHS } from './coeur/constantes/routes.const';

export const routes: Routes = [
  {
    path: ROUTE_PATHS.connexion,
    loadComponent: () =>
      import('./fonctionnalites/authentification/pages/connexion/connexion.component')
        .then(m => m.ConnexionComponent),
  },
  {
    path: `${ROUTE_PATHS.activationCompte}/:uidb64/:token`,
    loadComponent: () =>
      import('./fonctionnalites/authentification/pages/activation-compte/activation-compte.component')
        .then(m => m.ActivationCompteComponent),
  },
  {
    path: ROUTE_PATHS.accueil,
    canActivate: [authGuard],
    loadComponent: () =>
      import('./mise-en-page/coquille/coquille.component')
        .then(m => m.CoquilleComponent),
    children: [
      {
        path: ROUTE_PATHS.accueil,
        loadComponent: () =>
          import('./mise-en-page/accueil/accueil.component')
            .then(m => m.AccueilComponent),
      },

      {
        path: ROUTE_PATHS.cartes,
        loadComponent: () =>
          import('./fonctionnalites/cartes/pages/liste-cartes/liste-cartes')
            .then(m => m.ListeCartes),
      },

      {
        path: ROUTE_PATHS.gestionPannes,
        loadComponent: () =>
          import('./fonctionnalites/gestion-pannes/pages/liste-pannes/liste-pannes')
            .then(m => m.ListePannes),
      },

      {
        path: ROUTE_PATHS.actionsReparation,
        loadComponent: () =>
          import('./fonctionnalites/actions-reparation/pages/liste-actions/liste-actions')
            .then(m => m.ListeActions),
      },

      {
        path: ROUTE_PATHS.maintenance,
        loadComponent: () =>
          import('./fonctionnalites/maintenance/pages/accueil-maintenance/accueil-maintenance')
            .then(m => m.AccueilMaintenance),
      },

      {
        path: ROUTE_PATHS.piecesRechange,
        loadComponent: () =>
          import('./fonctionnalites/pieces-rechange/pages/accueil-pdr/accueil-pdr')
            .then(m => m.AccueilPdr),
      },

      {
        path: ROUTE_PATHS.etalonnage,
        loadComponent: () =>
          import('./fonctionnalites/etalonnage/pages/accueil-etalonnage/accueil-etalonnage')
            .then(m => m.AccueilEtalonnage),
      },

      {
        path: ROUTE_PATHS.alertes,
        loadComponent: () =>
          import('./fonctionnalites/alertes/pages/accueil-alertes/accueil-alertes')
            .then(m => m.AccueilAlertes),
      },

      {
        path: ROUTE_PATHS.agentPrediction,
        loadComponent: () =>
          import('./fonctionnalites/agent-prediction/pages/accueil-agent-prediction/accueil-agent-prediction')
            .then(m => m.AccueilAgentPrediction),
      },
    ],
  },

  {
    path: '**',
    redirectTo: '',
  },
];
