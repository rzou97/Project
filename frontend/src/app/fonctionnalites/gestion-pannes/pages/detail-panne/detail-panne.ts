import { CommonModule } from '@angular/common';
import { DestroyRef, Component, OnInit, computed, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ROUTE_PATHS } from '../../../../coeur/constantes/routes.const';
import { GestionPannesStore } from '../../etat/gestion-pannes-store';

@Component({
  selector: 'app-detail-panne',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './detail-panne.html',
  styleUrl: './detail-panne.scss',
})
export class DetailPanne implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);
  private readonly store = inject(GestionPannesStore);

  readonly paths = ROUTE_PATHS;
  readonly panne = this.store.panne;
  readonly tickets = this.store.tickets;
  readonly mouvements = this.store.mouvements;
  readonly chargement = this.store.chargement;
  readonly erreur = this.store.erreur;

  readonly ticketActif = computed(() =>
    this.tickets().find((ticket) => !['CLOSED', 'CANCELLED'].includes(ticket.ticket_status)) ?? null
  );
  readonly dernierMouvement = computed(() => this.mouvements()[0] ?? null);

  ngOnInit(): void {
    this.route.paramMap
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((params) => {
        const failureId = Number(params.get('failureId'));

        if (!Number.isFinite(failureId) || failureId <= 0) {
          this.store.vider();
          return;
        }

        this.store.charger(failureId);
      });
  }
}
