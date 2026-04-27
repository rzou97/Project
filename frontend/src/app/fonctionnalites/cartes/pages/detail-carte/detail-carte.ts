import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Carte, MouvementTest } from '../../../../coeur/modeles/carte.model';
import { CartesApi, TestMovementQuery } from '../../../../coeur/services-api/cartes-api';

@Component({
  selector: 'app-detail-carte',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './detail-carte.html',
  styleUrl: './detail-carte.scss',
})
export class DetailCarte implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly cartesApi = inject(CartesApi);

  readonly phases = ['BOARD_TEST', 'LEAK_TEST', 'BURN_IN_TEST', 'NORMATIVE_TEST', 'FINAL_TEST'];
  readonly resultats = ['PASSED', 'FAILED', 'ERROR', 'TERMINATED'];
  readonly pageSizeOptions = [10, 25, 50];

  readonly carte = signal<Carte | null>(null);
  readonly mouvements = signal<MouvementTest[]>([]);
  readonly chargementCarte = signal(true);
  readonly chargementMouvements = signal(true);
  readonly erreur = signal('');
  readonly totalMouvements = signal(0);
  readonly totalPages = signal(1);

  serialNumber = '';
  pageCourante = 1;
  filtres = {
    test_phase: '',
    result: '',
    tester_id: '',
    page_size: 10,
  };

  ngOnInit(): void {
    this.serialNumber = this.route.snapshot.paramMap.get('serialNumber') ?? '';

    if (!this.serialNumber) {
      this.erreur.set('Aucun serial number n a ete fourni.');
      this.chargementCarte.set(false);
      this.chargementMouvements.set(false);
      return;
    }

    this.chargerCarte();
    this.chargerMouvements(1);
  }

  chargerCarte(): void {
    this.chargementCarte.set(true);

    this.cartesApi.recupererParSerial(this.serialNumber).subscribe({
      next: (carte) => {
        this.carte.set(carte);
        if (!carte) {
          this.erreur.set('Carte introuvable pour ce serial number.');
        }
        this.chargementCarte.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger la fiche carte.');
        this.chargementCarte.set(false);
      },
    });
  }

  chargerMouvements(page = this.pageCourante): void {
    this.chargementMouvements.set(true);
    this.erreur.set('');

    const query: TestMovementQuery = {
      test_phase: this.nettoyer(this.filtres.test_phase),
      result: this.nettoyer(this.filtres.result),
      tester_id: this.nettoyer(this.filtres.tester_id),
      page,
      page_size: this.filtres.page_size,
      ordering: '-tested_at',
    };

    this.cartesApi.listerMouvements(this.serialNumber, query).subscribe({
      next: ({ items, count, totalPages, page: currentPage }) => {
        this.mouvements.set(items);
        this.totalMouvements.set(count);
        this.totalPages.set(totalPages);
        this.pageCourante = currentPage;
        this.chargementMouvements.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les mouvements de test de cette carte.');
        this.chargementMouvements.set(false);
      },
    });
  }

  appliquerFiltres(): void {
    this.chargerMouvements(1);
  }

  reinitialiserFiltres(): void {
    this.filtres = {
      test_phase: '',
      result: '',
      tester_id: '',
      page_size: 10,
    };
    this.chargerMouvements(1);
  }

  changerTaillePage(): void {
    this.chargerMouvements(1);
  }

  pagePrecedente(): void {
    if (this.pageCourante > 1) {
      this.chargerMouvements(this.pageCourante - 1);
    }
  }

  pageSuivante(): void {
    if (this.pageCourante < this.totalPages()) {
      this.chargerMouvements(this.pageCourante + 1);
    }
  }

  debutResultats(): number {
    if (this.totalMouvements() === 0) {
      return 0;
    }
    return (this.pageCourante - 1) * this.filtres.page_size + 1;
  }

  finResultats(): number {
    return Math.min(this.pageCourante * this.filtres.page_size, this.totalMouvements());
  }

  private nettoyer(value: string): string | undefined {
    const cleaned = value.trim();
    return cleaned ? cleaned : undefined;
  }
}
