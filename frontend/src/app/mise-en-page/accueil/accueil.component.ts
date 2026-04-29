import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import { KpiApiService } from '../../coeur/services-api/kpi-api.service';
import {
  TauxPanneActuelKpi,
  TauxPanneActuelReferenceKpi,
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
  topReferencesPannes = computed(() =>
    (this.tauxPannesActuel()?.references ?? []).slice(0, 10)
  );
  maxChartDefectCount = computed(() => {
    const counts = this.topReferencesPannes().map((item) => item.defective_sn);
    return counts.length ? Math.max(...counts, 1) : 1;
  });

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

  chartColumnHeight(item: TauxPanneActuelReferenceKpi): string {
    const maxCount = this.maxChartDefectCount();
    const height = maxCount <= 0 ? 0 : (item.defective_sn / maxCount) * 100;
    return `${Math.max(height, item.defective_sn > 0 ? 12 : 0)}%`;
  }
}
