import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../coeur/auth/auth.service';
import { SessionService } from '../../coeur/auth/session.service';
import { ROUTE_PATHS } from '../../coeur/constantes/routes.const';

interface RaccourciRecherche {
  label: string;
  route: string;
}

@Component({
  selector: 'app-en-tete',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './en-tete.component.html',
  styleUrl: './en-tete.component.scss',
})
export class EnTeteComponent {
  readonly sessionService = inject(SessionService);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  readonly query = signal('');
  readonly afficherSuggestions = signal(false);

  readonly raccourcis: RaccourciRecherche[] = [
    { label: 'Accueil', route: '/' },
    { label: 'Cartes', route: `/${ROUTE_PATHS.cartes}` },
    { label: 'Gestion des pannes', route: `/${ROUTE_PATHS.gestionPannes}` },
    { label: 'Actions de reparation', route: `/${ROUTE_PATHS.actionsReparation}` },
    { label: 'Maintenance', route: `/${ROUTE_PATHS.maintenance}` },
    { label: 'Pieces de rechange', route: `/${ROUTE_PATHS.piecesRechange}` },
    { label: 'Etalonnage', route: `/${ROUTE_PATHS.etalonnage}` },
    { label: 'Alertes', route: `/${ROUTE_PATHS.alertes}` },
    { label: 'Agent de prediction', route: `/${ROUTE_PATHS.agentPrediction}` },
  ];

  readonly resultatsRecherche = computed(() => {
    const term = this.query().trim().toLowerCase();
    if (!term) {
      return [];
    }

    return this.raccourcis
      .filter((item) => item.label.toLowerCase().includes(term))
      .slice(0, 6);
  });

  onQueryChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value || '';
    this.query.set(value);
    this.afficherSuggestions.set(value.trim().length > 0);
  }

  onQueryFocus(): void {
    if (this.query().trim()) {
      this.afficherSuggestions.set(true);
    }
  }

  onQueryBlur(): void {
    setTimeout(() => this.afficherSuggestions.set(false), 120);
  }

  onQueryEnter(event: KeyboardEvent): void {
    if (event.key !== 'Enter') {
      return;
    }

    const first = this.resultatsRecherche()[0];
    if (!first) {
      return;
    }

    event.preventDefault();
    this.allerVers(first.route);
  }

  allerVers(route: string): void {
    this.query.set('');
    this.afficherSuggestions.set(false);
    this.router.navigateByUrl(route);
  }

  displayName(user: { full_name?: string; email?: string; first_name?: string; last_name?: string }): string {
    const fullName = user.full_name?.trim();
    if (fullName) {
      return fullName;
    }

    const composed = `${user.first_name || ''} ${user.last_name || ''}`.trim();
    if (composed) {
      return composed;
    }

    return user.email || 'Utilisateur';
  }

  initials(name: string): string {
    const cleaned = name.trim();
    if (!cleaned) {
      return 'U';
    }

    const parts = cleaned.split(/\s+/).filter(Boolean);
    if (parts.length === 1) {
      return parts[0].slice(0, 2).toUpperCase();
    }

    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }

  seDeconnecter(): void {
    this.authService.seDeconnecter();
    this.router.navigateByUrl('/connexion');
  }
}
