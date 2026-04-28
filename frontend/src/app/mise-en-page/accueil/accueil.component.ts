import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import { KpiApiService } from '../../coeur/services-api/kpi-api.service';
import {
  TauxPanneActuelKpi,
  TesterCurrentStatusKpi,
  TesterFpyInstantKpi,
} from '../../coeur/modeles/kpi.model';

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
  tauxPannesActuel = signal<TauxPanneActuelKpi | null>(null);

  ngOnInit(): void {
    this.chargerDonnees();
  }

  chargerDonnees(): void {
    this.chargement.set(true);
    this.erreur.set('');

    forkJoin({
      fpy: this.kpiApiService.obtenirFpyInstantTesteurs(),
      statuts: this.kpiApiService.obtenirStatutActuelTesteurs(),
      tauxPannes: this.kpiApiService.obtenirTauxPannesActuel(),
    }).subscribe({
      next: ({ fpy, statuts, tauxPannes }) => {
        this.fpyTesteurs.set(fpy);
        this.statutsTesteurs.set(statuts);
        this.tauxPannesActuel.set(tauxPannes);
        this.chargement.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les KPI de production.');
        this.chargement.set(false);
      },
    });
  }

  libelleStatut(statut: string): string {
    switch (statut) {
      case 'ACTIVE':
        return 'Actif';
      case 'DEGRADED':
        return 'Degrade';
      case 'STOPPED':
        return 'En arret';
      case 'IN_REPAIR':
        return 'En reparation';
      default:
        return statut;
    }
  }

  referenceLabel(reference: string): string {
    const cleaned = (reference || '').trim();
    return cleaned || '-';
  }
}
