import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { KpiApiService } from '../../coeur/services-api/kpi-api.service';
import { TesterCurrentStatusKpi, TesterFpyInstantKpi } from '../../coeur/modeles/kpi.model';

@Component({
  selector: 'app-accueil',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './accueil.component.html',
  styleUrl: './accueil.component.scss',
})
export class AccueilComponent implements OnInit {
  private readonly kpiApiService = inject(KpiApiService);

  chargement = signal(true);
  erreur = signal('');

  fpyTesteurs = signal<TesterFpyInstantKpi[]>([]);
  statutsTesteurs = signal<TesterCurrentStatusKpi[]>([]);

  ngOnInit(): void {
    this.chargerDonnees();
  }

  chargerDonnees(): void {
    this.chargement.set(true);
    this.erreur.set('');

    this.kpiApiService.obtenirFpyInstantTesteurs().subscribe({
      next: (data) => this.fpyTesteurs.set(data),
      error: () => this.erreur.set('Impossible de charger le FPY instantané.'),
    });

    this.kpiApiService.obtenirStatutActuelTesteurs().subscribe({
      next: (data) => {
        this.statutsTesteurs.set(data);
        this.chargement.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger le statut des testeurs.');
        this.chargement.set(false);
      },
    });
  }

  libelleStatut(statut: string): string {
    switch (statut) {
      case 'ACTIVE':
        return 'Actif';
      case 'DEGRADED':
        return 'Dégradé';
      case 'STOPPED':
        return 'En arrêt';
      case 'IN_REPAIR':
        return 'En réparation';
      default:
        return statut;
    }
  }
}
