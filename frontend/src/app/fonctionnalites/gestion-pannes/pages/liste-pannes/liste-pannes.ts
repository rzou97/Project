import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { GestionPanne } from '../../../../coeur/modeles/gestion-panne.model';
import { FailureListQuery, GestionPannesApi } from '../../../../coeur/services-api/gestion-pannes-api';

@Component({
  selector: 'app-liste-pannes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './liste-pannes.html',
  styleUrl: './liste-pannes.scss',
})
export class ListePannes implements OnInit {
  private readonly gestionPannesApi = inject(GestionPannesApi);

  readonly statuts = ['IN_DEFECT', 'IN_REPAIR', 'WAITING_RETEST', 'REPAIRED'];
  readonly pageSizeOptions = [10, 25, 50];

  chargement = signal(true);
  erreur = signal('');
  pannes = signal<GestionPanne[]>([]);
  totalPannes = signal(0);
  totalPages = signal(1);

  pageCourante = 1;
  filtres = {
    serial_number: '',
    client_reference: '',
    internal_reference: '',
    failure_status: '',
    detected_on_tester: '',
    failure_type: '',
    page_size: 10,
  };

  ngOnInit(): void {
    this.chargerPannes(1);
  }

  chargerPannes(page = this.pageCourante): void {
    this.chargement.set(true);
    this.erreur.set('');

    const query: FailureListQuery = {
      serial_number: this.nettoyer(this.filtres.serial_number),
      client_reference: this.nettoyer(this.filtres.client_reference),
      internal_reference: this.nettoyer(this.filtres.internal_reference),
      failure_status: this.nettoyer(this.filtres.failure_status),
      detected_on_tester: this.nettoyer(this.filtres.detected_on_tester),
      failure_type: this.nettoyer(this.filtres.failure_type),
      page,
      page_size: this.filtres.page_size,
      ordering: '-opened_at',
    };

    this.gestionPannesApi.lister(query).subscribe({
      next: ({ items, count, totalPages, page: currentPage }) => {
        this.pannes.set(items);
        this.totalPannes.set(count);
        this.totalPages.set(totalPages);
        this.pageCourante = currentPage;
        this.chargement.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les failure cases.');
        this.chargement.set(false);
      },
    });
  }

  appliquerFiltres(): void {
    this.chargerPannes(1);
  }

  reinitialiserFiltres(): void {
    this.filtres = {
      serial_number: '',
      client_reference: '',
      internal_reference: '',
      failure_status: '',
      detected_on_tester: '',
      failure_type: '',
      page_size: 10,
    };
    this.chargerPannes(1);
  }

  changerTaillePage(): void {
    this.chargerPannes(1);
  }

  pagePrecedente(): void {
    if (this.pageCourante > 1) {
      this.chargerPannes(this.pageCourante - 1);
    }
  }

  pageSuivante(): void {
    if (this.pageCourante < this.totalPages()) {
      this.chargerPannes(this.pageCourante + 1);
    }
  }

  debutResultats(): number {
    if (this.totalPannes() === 0) {
      return 0;
    }
    return (this.pageCourante - 1) * this.filtres.page_size + 1;
  }

  finResultats(): number {
    return Math.min(this.pageCourante * this.filtres.page_size, this.totalPannes());
  }

  private nettoyer(value: string): string | undefined {
    const cleaned = value.trim();
    return cleaned ? cleaned : undefined;
  }
}
