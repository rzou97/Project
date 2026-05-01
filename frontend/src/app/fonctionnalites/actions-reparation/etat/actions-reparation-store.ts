import { Injectable, inject, signal } from '@angular/core';
import { catchError, forkJoin, of } from 'rxjs';
import {
  ActionReparation,
  FailureEnrichment,
  RepairHistory,
  RepairPrediction,
  TicketReparation,
} from '../../../coeur/modeles/action-reparation.model';
import {
  ActionsReparationApi,
  CreateRepairActionPayload,
  UpdateRepairTicketPayload,
} from '../../../coeur/services-api/actions-reparation-api';
import {
  AnalyzeFailurePayload,
  IntelligenceApi,
} from '../../../coeur/services-api/intelligence-api';

@Injectable({
  providedIn: 'root',
})
export class ActionsReparationStore {
  private readonly actionsReparationApi = inject(ActionsReparationApi);
  private readonly intelligenceApi = inject(IntelligenceApi);

  readonly ticket = signal<TicketReparation | null>(null);
  readonly actions = signal<ActionReparation[]>([]);
  readonly enrichment = signal<FailureEnrichment | null>(null);
  readonly prediction = signal<RepairPrediction | null>(null);
  readonly similarHistories = signal<RepairHistory[]>([]);
  readonly chargementTicket = signal(false);
  readonly chargementActions = signal(false);
  readonly chargementIntelligence = signal(false);
  readonly analyseIntelligence = signal(false);
  readonly miseAJourTicket = signal(false);
  readonly soumissionAction = signal(false);
  readonly erreur = signal('');
  readonly erreurAction = signal('');
  readonly erreurIntelligence = signal('');
  readonly succesAction = signal('');
  readonly succesIntelligence = signal('');

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
        this.chargerIntelligence(ticket);
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

  chargerIntelligence(ticket: TicketReparation): void {
    this.chargementIntelligence.set(true);
    this.erreurIntelligence.set('');
    this.succesIntelligence.set('');

    forkJoin({
      enrichments: this.intelligenceApi
        .listerEnrichissements({
          failure_case: ticket.failure_case,
          page: 1,
          page_size: 1,
          ordering: '-enriched_at',
        })
        .pipe(catchError(() => of(null))),
      predictions: this.intelligenceApi
        .listerPredictions({
          failure_case: ticket.failure_case,
          repair_ticket: ticket.id,
          page: 1,
          page_size: 1,
          ordering: '-predicted_at',
        })
        .pipe(catchError(() => of(null))),
      histories: this.intelligenceApi
        .listerHistorique({
          internal_reference: ticket.internal_reference ?? undefined,
          failure_type: ticket.failure_type ?? undefined,
          page: 1,
          page_size: 5,
          ordering: '-created_at',
        })
        .pipe(catchError(() => of(null))),
    }).subscribe({
      next: ({ enrichments, predictions, histories }) => {
        this.enrichment.set(enrichments?.items[0] ?? null);
        this.prediction.set(predictions?.items[0] ?? null);
        this.similarHistories.set(
          (histories?.items ?? []).filter((history) => history.failure_case !== ticket.failure_case)
        );

        if (!enrichments || !predictions || !histories) {
          this.erreurIntelligence.set(
            "Une partie des donnees d'intelligence n'a pas pu etre chargee."
          );
        }

        this.chargementIntelligence.set(false);
      },
      error: () => {
        this.enrichment.set(null);
        this.prediction.set(null);
        this.similarHistories.set([]);
        this.erreurIntelligence.set("Impossible de charger le bloc d'intelligence.");
        this.chargementIntelligence.set(false);
      },
    });
  }

  analyserTicketIntelligence(payload: AnalyzeFailurePayload): void {
    this.analyseIntelligence.set(true);
    this.erreurIntelligence.set('');
    this.succesIntelligence.set('');

    this.intelligenceApi.analyserPanne(payload).subscribe({
      next: ({ enrichment, prediction }) => {
        this.enrichment.set(enrichment);
        this.prediction.set(prediction);
        this.analyseIntelligence.set(false);
        this.succesIntelligence.set("L'analyse intelligente a ete actualisee.");

        const ticket = this.ticket();
        if (ticket) {
          this.intelligenceApi
            .listerHistorique({
              internal_reference: ticket.internal_reference ?? undefined,
              failure_type: ticket.failure_type ?? undefined,
              page: 1,
              page_size: 5,
              ordering: '-created_at',
            })
            .subscribe({
              next: ({ items }) => {
                this.similarHistories.set(
                  items.filter((history) => history.failure_case !== ticket.failure_case)
                );
              },
              error: () => {
                this.similarHistories.set([]);
              },
            });
        }
      },
      error: (err) => {
        this.analyseIntelligence.set(false);
        this.erreurIntelligence.set(
          this.extraireErreur(err, "Impossible de lancer l'analyse intelligente.")
        );
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
    this.erreurIntelligence.set('');
    this.succesIntelligence.set('');
  }

  vider(): void {
    this.ticket.set(null);
    this.actions.set([]);
    this.enrichment.set(null);
    this.prediction.set(null);
    this.similarHistories.set([]);
    this.chargementTicket.set(false);
    this.chargementActions.set(false);
    this.chargementIntelligence.set(false);
    this.analyseIntelligence.set(false);
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
