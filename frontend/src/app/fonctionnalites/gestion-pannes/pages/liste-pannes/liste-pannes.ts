import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { GestionPanne } from '../../../../coeur/modeles/gestion-panne.model';
import { GestionPannesApi } from '../../../../coeur/services-api/gestion-pannes-api';

@Component({
  selector: 'app-liste-pannes',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './liste-pannes.html',
  styleUrl: './liste-pannes.scss',
})
export class ListePannes implements OnInit {
  private readonly gestionPannesApi = inject(GestionPannesApi);

  chargement = signal(true);
  erreur = signal('');
  pannes = signal<GestionPanne[]>([]);

  ngOnInit(): void {
    this.chargerPannes();
  }

  chargerPannes(): void {
    this.chargement.set(true);
    this.erreur.set('');

    this.gestionPannesApi.lister().subscribe({
      next: (pannes) => {
        this.pannes.set(pannes);
        this.chargement.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les failure cases.');
        this.chargement.set(false);
      },
    });
  }
}
