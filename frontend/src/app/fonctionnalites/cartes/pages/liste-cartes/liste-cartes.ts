import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { Carte } from '../../../../coeur/modeles/carte.model';
import { CartesApi } from '../../../../coeur/services-api/cartes-api';

@Component({
  selector: 'app-liste-cartes',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './liste-cartes.html',
  styleUrl: './liste-cartes.scss',
})
export class ListeCartes implements OnInit {
  private readonly cartesApi = inject(CartesApi);

  chargement = signal(true);
  erreur = signal('');
  cartes = signal<Carte[]>([]);

  ngOnInit(): void {
    this.chargerCartes();
  }

  chargerCartes(): void {
    this.chargement.set(true);
    this.erreur.set('');

    this.cartesApi.lister().subscribe({
      next: (cartes) => {
        this.cartes.set(cartes);
        this.chargement.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les cartes.');
        this.chargement.set(false);
      },
    });
  }
}
