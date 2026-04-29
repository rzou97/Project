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
  maxChartRate = computed(() => {
    const rates = this.topReferencesPannes().map((item) =>
      this.toNumericRate(item.current_failure_rate)
    );
    return rates.length ? Math.max(...rates, 1) : 1;
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

  chartBarWidth(item: TauxPanneActuelReferenceKpi): string {
    const maxRate = this.maxChartRate();
    const rate = this.toNumericRate(item.current_failure_rate);
    const width = maxRate <= 0 ? 0 : (rate / maxRate) * 100;
    return `${Math.max(width, 4)}%`;
  }

  chartRateLabel(item: TauxPanneActuelReferenceKpi): string {
    return `${this.toNumericRate(item.current_failure_rate).toFixed(2)} %`;
  }

  private toNumericRate(value: number | string): number {
    const numeric = typeof value === 'number' ? value : Number(value);
    return Number.isFinite(numeric) ? numeric : 0;
  }
}
