import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import {
  ActionReparation,
  TicketReparation,
} from '../../../../coeur/modeles/action-reparation.model';
import { ROUTE_PATHS } from '../../../../coeur/constantes/routes.const';
import {
  ActionListQuery,
  ActionsReparationApi,
  TicketListQuery,
} from '../../../../coeur/services-api/actions-reparation-api';

@Component({
  selector: 'app-liste-actions',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './liste-actions.html',
  styleUrl: './liste-actions.scss',
})
export class ListeActions implements OnInit {
  private readonly actionsReparationApi = inject(ActionsReparationApi);

  readonly paths = ROUTE_PATHS;
  readonly ticketStatuses = ['OPEN', 'IN_PROGRESS', 'WAITING_RETEST', 'CLOSED', 'CANCELLED'];
  readonly actionProgressStatuses = ['PENDING', 'IN_PROGRESS', 'DONE', 'WAITING_PARTS', 'WAITING_RETEST'];
  readonly pageSizeOptions = [5, 10, 25];

  readonly ticketsActifs = computed(() =>
    this.tickets().filter((ticket) => ['OPEN', 'IN_PROGRESS'].includes(ticket.ticket_status)).length
  );
  readonly ticketsEnRetest = computed(() =>
    this.tickets().filter((ticket) => ticket.ticket_status === 'WAITING_RETEST').length
  );
  readonly ticketsClosOuAnnules = computed(() =>
    this.tickets().filter((ticket) => ['CLOSED', 'CANCELLED'].includes(ticket.ticket_status)).length
  );
  readonly actionsEnCours = computed(() =>
    this.actions().filter((action) =>
      ['PENDING', 'IN_PROGRESS', 'WAITING_PARTS'].includes(action.action_progress ?? '')
    ).length
  );

  chargementTickets = signal(true);
  chargementActions = signal(true);
  erreur = signal('');
  tickets = signal<TicketReparation[]>([]);
  actions = signal<ActionReparation[]>([]);
  totalTickets = signal(0);
  totalActions = signal(0);
  totalPagesTickets = signal(1);
  totalPagesActions = signal(1);

  pageTickets = 1;
  pageActions = 1;

  filtresTickets = {
    serial_number: '',
    internal_reference: '',
    ticket_code: '',
    ticket_status: '',
    page_size: 5,
  };

  filtresActions = {
    serial_number: '',
    ticket_code: '',
    defect_type: '',
    action_progress: '',
    page_size: 5,
  };

  ngOnInit(): void {
    this.chargerDonnees();
  }

  chargerDonnees(): void {
    this.erreur.set('');
    this.chargerTickets(this.pageTickets);
    this.chargerActions(this.pageActions);
  }

  chargerTickets(page = this.pageTickets): void {
    this.chargementTickets.set(true);

    const query: TicketListQuery = {
      serial_number: this.nettoyer(this.filtresTickets.serial_number),
      internal_reference: this.nettoyer(this.filtresTickets.internal_reference),
      ticket_code: this.nettoyer(this.filtresTickets.ticket_code),
      ticket_status: this.nettoyer(this.filtresTickets.ticket_status),
      page,
      page_size: this.filtresTickets.page_size,
      ordering: '-opened_at',
    };

    this.actionsReparationApi.listerTickets(query).subscribe({
      next: ({ items, count, totalPages, page: currentPage }) => {
        this.tickets.set(items);
        this.totalTickets.set(count);
        this.totalPagesTickets.set(totalPages);
        this.pageTickets = currentPage;
        this.chargementTickets.set(false);
      },
      error: () => {
        this.erreur.set('Impossible de charger les tickets de reparation.');
        this.chargementTickets.set(false);
      },
    });
  }

  chargerActions(page = this.pageActions): void {
    this.chargementActions.set(true);

    const query: ActionListQuery = {
      serial_number: this.nettoyer(this.filtresActions.serial_number),
      ticket_code: this.nettoyer(this.filtresActions.ticket_code),
      defect_type: this.nettoyer(this.filtresActions.defect_type),
      action_progress: this.nettoyer(this.filtresActions.action_progress),
      page,
      page_size: this.filtresActions.page_size,
      ordering: '-performed_at',
    };

    this.actionsReparationApi.listerActions(query).subscribe({
      next: ({ items, count, totalPages, page: currentPage }) => {
        this.actions.set(items);
        this.totalActions.set(count);
        this.totalPagesActions.set(totalPages);
        this.pageActions = currentPage;
        this.chargementActions.set(false);
      },
      error: () => {
        this.erreur.set("Impossible de charger l'historique des actions.");
        this.chargementActions.set(false);
      },
    });
  }

  appliquerFiltresTickets(): void {
    this.chargerTickets(1);
  }

  appliquerFiltresActions(): void {
    this.chargerActions(1);
  }

  reinitialiserFiltresTickets(): void {
    this.filtresTickets = {
      serial_number: '',
      internal_reference: '',
      ticket_code: '',
      ticket_status: '',
      page_size: 5,
    };
    this.chargerTickets(1);
  }

  reinitialiserFiltresActions(): void {
    this.filtresActions = {
      serial_number: '',
      ticket_code: '',
      defect_type: '',
      action_progress: '',
      page_size: 5,
    };
    this.chargerActions(1);
  }

  pagePrecedenteTickets(): void {
    if (this.pageTickets > 1) {
      this.chargerTickets(this.pageTickets - 1);
    }
  }

  pageSuivanteTickets(): void {
    if (this.pageTickets < this.totalPagesTickets()) {
      this.chargerTickets(this.pageTickets + 1);
    }
  }

  pagePrecedenteActions(): void {
    if (this.pageActions > 1) {
      this.chargerActions(this.pageActions - 1);
    }
  }

  pageSuivanteActions(): void {
    if (this.pageActions < this.totalPagesActions()) {
      this.chargerActions(this.pageActions + 1);
    }
  }

  debutTickets(): number {
    if (this.totalTickets() === 0) {
      return 0;
    }
    return (this.pageTickets - 1) * this.filtresTickets.page_size + 1;
  }

  finTickets(): number {
    return Math.min(this.pageTickets * this.filtresTickets.page_size, this.totalTickets());
  }

  debutActions(): number {
    if (this.totalActions() === 0) {
      return 0;
    }
    return (this.pageActions - 1) * this.filtresActions.page_size + 1;
  }

  finActions(): number {
    return Math.min(this.pageActions * this.filtresActions.page_size, this.totalActions());
  }

  private nettoyer(value: string): string | undefined {
    const cleaned = value.trim();
    return cleaned ? cleaned : undefined;
  }
}
