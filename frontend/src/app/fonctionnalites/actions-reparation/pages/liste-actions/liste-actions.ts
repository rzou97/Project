import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import {
  ActionReparation,
  TicketReparation,
} from '../../../../coeur/modeles/action-reparation.model';
import { ActionsReparationApi } from '../../../../coeur/services-api/actions-reparation-api';

@Component({
  selector: 'app-liste-actions',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './liste-actions.html',
  styleUrl: './liste-actions.scss',
})
export class ListeActions implements OnInit {
  private readonly actionsReparationApi = inject(ActionsReparationApi);

  chargement = signal(true);
  erreur = signal('');
  tickets = signal<TicketReparation[]>([]);
  actions = signal<ActionReparation[]>([]);

  ngOnInit(): void {
    this.chargerDonnees();
  }

  chargerDonnees(): void {
    this.chargement.set(true);
    this.erreur.set('');

    forkJoin({
      tickets: this.actionsReparationApi.listerTickets(),
      actions: this.actionsReparationApi.listerActions(),
    }).subscribe({
      next: ({ tickets, actions }) => {
        this.tickets.set(tickets);
        this.actions.set(actions);
        this.chargement.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les tickets et actions de reparation.');
        this.chargement.set(false);
      },
    });
  }
}
