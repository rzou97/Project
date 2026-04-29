import { Injectable, inject, signal } from '@angular/core';
import { MouvementTest } from '../../../coeur/modeles/carte.model';
import { GestionPanne } from '../../../coeur/modeles/gestion-panne.model';
import { CartesApi } from '../../../coeur/services-api/cartes-api';
import { ActionsReparationApi } from '../../../coeur/services-api/actions-reparation-api';
import { GestionPannesApi } from '../../../coeur/services-api/gestion-pannes-api';
import { TicketReparation } from '../../../coeur/modeles/action-reparation.model';
import { forkJoin } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GestionPannesStore {
  private readonly gestionPannesApi = inject(GestionPannesApi);
  private readonly actionsReparationApi = inject(ActionsReparationApi);
  private readonly cartesApi = inject(CartesApi);

  readonly panne = signal<GestionPanne | null>(null);
  readonly tickets = signal<TicketReparation[]>([]);
  readonly mouvements = signal<MouvementTest[]>([]);
  readonly chargement = signal(false);
  readonly erreur = signal('');

  charger(failureId: number): void {
    this.chargement.set(true);
    this.erreur.set('');

    this.gestionPannesApi.obtenir(failureId).subscribe({
      next: (panne) => {
        this.panne.set(panne);

        forkJoin({
          tickets: this.actionsReparationApi.listerTickets({
            failure_case: failureId,
            page: 1,
            page_size: 20,
            ordering: '-opened_at',
          }),
          mouvements: this.cartesApi.listerMouvements(panne.serial_number, {
            page: 1,
            page_size: 8,
            ordering: '-tested_at',
          }),
        }).subscribe({
          next: ({ tickets, mouvements }) => {
            this.tickets.set(tickets.items);
            this.mouvements.set(mouvements.items);
            this.chargement.set(false);
          },
          error: () => {
            this.erreur.set(
              "Impossible de charger les tickets ou mouvements de test lies a cette panne."
            );
            this.chargement.set(false);
          },
        });
      },
      error: () => {
        this.erreur.set("Impossible de charger le detail de la panne.");
        this.chargement.set(false);
      },
    });
  }

  vider(): void {
    this.panne.set(null);
    this.tickets.set([]);
    this.mouvements.set([]);
    this.chargement.set(false);
    this.erreur.set('');
  }
}
