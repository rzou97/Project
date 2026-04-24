import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { ROUTE_PATHS } from '../../coeur/constantes/routes.const';

@Component({
  selector: 'app-barre-laterale',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './barre-laterale.component.html',
  styleUrl: './barre-laterale.component.scss',
})
export class BarreLateraleComponent {
  menus = [
    { label: 'Accueil', route: '/' },
    { label: 'Cartes', route: `/${ROUTE_PATHS.cartes}` },
    { label: 'Gestion des pannes', route: `/${ROUTE_PATHS.gestionPannes}` },
    { label: 'Actions de reparation', route: `/${ROUTE_PATHS.actionsReparation}` },
    { label: 'Maintenance', route: `/${ROUTE_PATHS.maintenance}` },
    { label: 'Pieces de rechange', route: `/${ROUTE_PATHS.piecesRechange}` },
    { label: 'Etalonnage', route: `/${ROUTE_PATHS.etalonnage}` },
    { label: 'Alertes', route: `/${ROUTE_PATHS.alertes}` },
    { label: 'Agent de prediction', route: `/${ROUTE_PATHS.agentPrediction}` },
  ];
}
