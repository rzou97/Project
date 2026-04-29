import { Injectable, inject, signal } from '@angular/core';
import {
  ActionReparation,
  TicketReparation,
} from '../../../coeur/modeles/action-reparation.model';
import {
  ActionsReparationApi,
  CreateRepairActionPayload,
  UpdateRepairTicketPayload,
} from '../../../coeur/services-api/actions-reparation-api';

@Injectable({
  providedIn: 'root',
})
export class ActionsReparationStore {
  private readonly actionsReparationApi = inject(ActionsReparationApi);

  readonly ticket = signal<TicketReparation | null>(null);
  readonly actions = signal<ActionReparation[]>([]);
  readonly chargementTicket = signal(false);
  readonly chargementActions = signal(false);
  readonly miseAJourTicket = signal(false);
  readonly soumissionAction = signal(false);
  readonly erreur = signal('');
  readonly erreurAction = signal('');
  readonly succesAction = signal('');

  refresh(ticketId: number): void {
    this.erreur.set('');
    this.chargerTicket(ticketId);
    this.chargerActions(ticketId);
  }

  chargerTicket(ticketId: number): void {
    this.chargementTicket.set(true);

    this.actionsReparationApi.obtenirTicket(ticketId).subscribe({
      next: (ticket) => {
        this.ticket.set(ticket);
        this.chargementTicket.set(false);
      },
      error: () => {
        this.erreur.set("Impossible de charger le detail du ticket de reparation.");
        this.chargementTicket.set(false);
      },
    });
  }

  chargerActions(ticketId: number): void {
    this.chargementActions.set(true);

    this.actionsReparationApi
      .listerActions({
        repair_ticket: ticketId,
        page: 1,
        page_size: 50,
        ordering: '-performed_at',
      })
      .subscribe({
        next: ({ items }) => {
          this.actions.set(items);
          this.chargementActions.set(false);
        },
        error: () => {
          this.erreur.set("Impossible de charger l'historique des actions de reparation.");
          this.chargementActions.set(false);
        },
      });
  }

  enregistrerAction(payload: CreateRepairActionPayload, onSuccess?: () => void): void {
    this.soumissionAction.set(true);
    this.erreurAction.set('');
    this.succesAction.set('');

    this.actionsReparationApi.creerAction(payload).subscribe({
      next: () => {
        this.soumissionAction.set(false);
        this.succesAction.set("L'action technicien a bien ete enregistree.");
        this.refresh(payload.repair_ticket);
        onSuccess?.();
      },
      error: (err) => {
        this.soumissionAction.set(false);
        this.erreurAction.set(
          this.extraireErreur(err, "Impossible d'enregistrer l'action de reparation.")
        );
      },
    });
  }

  mettreAJourStatutTicket(
    ticketId: number,
    payload: UpdateRepairTicketPayload,
    successMessage: string
  ): void {
    this.miseAJourTicket.set(true);
    this.erreurAction.set('');
    this.succesAction.set('');

    this.actionsReparationApi.mettreAJourTicket(ticketId, payload).subscribe({
      next: () => {
        this.miseAJourTicket.set(false);
        this.succesAction.set(successMessage);
        this.refresh(ticketId);
      },
      error: (err) => {
        this.miseAJourTicket.set(false);
        this.erreurAction.set(
          this.extraireErreur(err, "Impossible de mettre a jour le ticket de reparation.")
        );
      },
    });
  }

  reinitialiserFeedbackAction(): void {
    this.erreurAction.set('');
    this.succesAction.set('');
  }

  vider(): void {
    this.ticket.set(null);
    this.actions.set([]);
    this.chargementTicket.set(false);
    this.chargementActions.set(false);
    this.miseAJourTicket.set(false);
    this.soumissionAction.set(false);
    this.erreur.set('');
    this.reinitialiserFeedbackAction();
  }

  private extraireErreur(err: unknown, fallback: string): string {
    const payload = (err as { error?: unknown })?.error;

    if (!payload) {
      return fallback;
    }

    if (typeof payload === 'string') {
      return payload;
    }

    if (typeof payload !== 'object') {
      return fallback;
    }

    const detail = (payload as { detail?: string }).detail;
    if (detail) {
      return detail;
    }

    return Object.entries(payload as Record<string, unknown>)
      .map(([key, value]) => {
        if (Array.isArray(value)) {
          return `${key}: ${value.join(', ')}`;
        }

        return `${key}: ${String(value)}`;
      })
      .join(' | ');
  }
}
