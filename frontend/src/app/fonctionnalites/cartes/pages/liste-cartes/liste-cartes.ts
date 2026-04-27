import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Carte } from '../../../../coeur/modeles/carte.model';
import { BoardListQuery, CartesApi } from '../../../../coeur/services-api/cartes-api';

@Component({
  selector: 'app-liste-cartes',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './liste-cartes.html',
  styleUrl: './liste-cartes.scss',
})
export class ListeCartes implements OnInit {
  private readonly cartesApi = inject(CartesApi);

  readonly statuts = ['HEALTHY', 'IN_DEFECT', 'IN_REPAIR', 'WAITING_RETEST', 'REPAIRED'];
  readonly pageSizeOptions = [10, 25, 50];

  chargement = signal(true);
  erreur = signal('');
  cartes = signal<Carte[]>([]);
  totalCartes = signal(0);
  totalPages = signal(1);

  pageCourante = 1;
  filtres = {
    serial_number: '',
    internal_reference: '',
    current_status: '',
    page_size: 10,
  };

  ngOnInit(): void {
    this.chargerCartes(1);
  }

  chargerCartes(page = this.pageCourante): void {
    this.chargement.set(true);
    this.erreur.set('');

    const query: BoardListQuery = {
      serial_number: this.nettoyer(this.filtres.serial_number),
      internal_reference: this.nettoyer(this.filtres.internal_reference),
      current_status: this.nettoyer(this.filtres.current_status),
      page,
      page_size: this.filtres.page_size,
      ordering: '-last_seen_at',
    };

    this.cartesApi.lister(query).subscribe({
      next: ({ items, count, totalPages, page: currentPage }) => {
        this.cartes.set(items);
        this.totalCartes.set(count);
        this.totalPages.set(totalPages);
        this.pageCourante = currentPage;
        this.chargement.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les cartes.');
        this.chargement.set(false);
      },
    });
  }

  appliquerFiltres(): void {
    this.chargerCartes(1);
  }

  reinitialiserFiltres(): void {
    this.filtres = {
      serial_number: '',
      internal_reference: '',
      current_status: '',
      page_size: 10,
    };
    this.chargerCartes(1);
  }

  changerTaillePage(): void {
    this.chargerCartes(1);
  }

  pagePrecedente(): void {
    if (this.pageCourante > 1) {
      this.chargerCartes(this.pageCourante - 1);
    }
  }

  pageSuivante(): void {
    if (this.pageCourante < this.totalPages()) {
      this.chargerCartes(this.pageCourante + 1);
    }
  }

  debutResultats(): number {
    if (this.totalCartes() === 0) {
      return 0;
    }
    return (this.pageCourante - 1) * this.filtres.page_size + 1;
  }

  finResultats(): number {
    return Math.min(this.pageCourante * this.filtres.page_size, this.totalCartes());
  }

  private nettoyer(value: string): string | undefined {
    const cleaned = value.trim();
    return cleaned ? cleaned : undefined;
  }
}
