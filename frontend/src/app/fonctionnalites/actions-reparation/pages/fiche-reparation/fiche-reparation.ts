import { CommonModule } from '@angular/common';
import { DestroyRef, Component, OnInit, computed, effect, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { SessionService } from '../../../../coeur/auth/session.service';
import { ROUTE_PATHS } from '../../../../coeur/constantes/routes.const';
import { CreateRepairActionPayload } from '../../../../coeur/services-api/actions-reparation-api';
import { ActionsReparationStore } from '../../etat/actions-reparation-store';

@Component({
  selector: 'app-fiche-reparation',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './fiche-reparation.html',
  styleUrl: './fiche-reparation.scss',
})
export class FicheReparation implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);
  private readonly sessionService = inject(SessionService);
  private readonly store = inject(ActionsReparationStore);

  readonly paths = ROUTE_PATHS;
  readonly actionProgressStatuses = ['PENDING', 'IN_PROGRESS', 'DONE', 'WAITING_PARTS', 'WAITING_RETEST'];

  readonly ticket = this.store.ticket;
  readonly actions = this.store.actions;
  readonly chargementTicket = this.store.chargementTicket;
  readonly chargementActions = this.store.chargementActions;
  readonly miseAJourTicket = this.store.miseAJourTicket;
  readonly soumissionAction = this.store.soumissionAction;
  readonly erreur = this.store.erreur;
  readonly erreurAction = this.store.erreurAction;
  readonly succesAction = this.store.succesAction;

  readonly peutSaisirActions = computed(() => {
    const role = this.sessionService.utilisateur()?.role;
    return role === 'ADMIN' || role === 'REPAIR_TECHNICIAN' || role === 'TECHNICIEN';
  });
  readonly peutPrendreEnCharge = computed(() =>
    this.peutSaisirActions() && this.ticket()?.ticket_status === 'OPEN'
  );
  readonly peutAnnulerTicket = computed(() => {
    const status = this.ticket()?.ticket_status;
    return this.peutSaisirActions() && !!status && !['CLOSED', 'CANCELLED'].includes(status);
  });
  readonly actionCount = computed(() => this.actions().length);

  formulaireAction = this.creerFormulaireAction();
  private ticketIdCourant: number | null = null;

  constructor() {
    effect(() => {
      const ticket = this.ticket();
      if (!ticket) {
        return;
      }

      if (this.formulaireAction.repair_ticket !== ticket.id) {
        this.formulaireAction.repair_ticket = ticket.id;
        this.formulaireAction.defect_type = ticket.failure_type ?? '';
      }
    });
  }

  ngOnInit(): void {
    this.route.paramMap
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((params) => {
        const ticketId = Number(params.get('ticketId'));

        if (!Number.isFinite(ticketId) || ticketId <= 0) {
          this.store.vider();
          return;
        }

        this.ticketIdCourant = ticketId;
        this.formulaireAction = this.creerFormulaireAction();
        this.store.reinitialiserFeedbackAction();
        this.store.refresh(ticketId);
      });
  }

  recharger(): void {
    if (this.ticketIdCourant) {
      this.store.refresh(this.ticketIdCourant);
    }
  }

  prendreEnCharge(): void {
    const ticket = this.ticket();
    if (!ticket) {
      return;
    }

    this.store.mettreAJourStatutTicket(
      ticket.id,
      { ticket_status: 'IN_PROGRESS' },
      'Le ticket a ete pris en charge.'
    );
  }

  annulerTicket(): void {
    const ticket = this.ticket();
    if (!ticket) {
      return;
    }

    this.store.mettreAJourStatutTicket(
      ticket.id,
      {
        ticket_status: 'CANCELLED',
        closed_at: new Date().toISOString(),
      },
      'Le ticket a ete annule.'
    );
  }

  soumettreAction(): void {
    const ticket = this.ticket();
    const actionTaken = this.formulaireAction.action_taken.trim();
    const performedAt = this.formulaireAction.performed_at;

    if (!ticket) {
      this.store.reinitialiserFeedbackAction();
      return;
    }

    if (!actionTaken) {
      this.store.erreurAction.set("Renseignez l'action de reparation effectuee.");
      return;
    }

    if (!performedAt) {
      this.store.erreurAction.set("Renseignez la date et l'heure de l'intervention.");
      return;
    }

    const payload: CreateRepairActionPayload = {
      repair_ticket: ticket.id,
      defect_type: this.nettoyer(this.formulaireAction.defect_type),
      observed_defect: this.nettoyer(this.formulaireAction.observed_defect),
      detected_cause: this.nettoyer(this.formulaireAction.detected_cause),
      action_taken: actionTaken,
      action_progress: this.formulaireAction.action_progress,
      performed_at: this.convertirDateLocaleEnIso(performedAt),
    };

    this.store.enregistrerAction(payload, () => {
      this.reinitialiserFormulaireAction();
    });
  }

  reinitialiserFormulaireAction(): void {
    const ticket = this.ticket();
    this.formulaireAction = {
      repair_ticket: ticket?.id ?? null,
      defect_type: ticket?.failure_type ?? '',
      observed_defect: '',
      detected_cause: '',
      action_taken: '',
      action_progress: 'IN_PROGRESS',
      performed_at: this.dateHeureLocaleCourante(),
    };
    this.store.reinitialiserFeedbackAction();
  }

  private nettoyer(value: string): string | undefined {
    const cleaned = value.trim();
    return cleaned ? cleaned : undefined;
  }

  private creerFormulaireAction() {
    return {
      repair_ticket: null as number | null,
      defect_type: '',
      observed_defect: '',
      detected_cause: '',
      action_taken: '',
      action_progress: 'IN_PROGRESS',
      performed_at: this.dateHeureLocaleCourante(),
    };
  }

  private dateHeureLocaleCourante(): string {
    const now = new Date();
    now.setSeconds(0, 0);
    const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
    return localDate.toISOString().slice(0, 16);
  }

  private convertirDateLocaleEnIso(value: string): string {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toISOString();
  }
}
