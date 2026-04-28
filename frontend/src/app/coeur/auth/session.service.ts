import { Injectable, signal } from '@angular/core';
import { Utilisateur } from '../modeles/utilisateur.model';

@Injectable({
  providedIn: 'root',
})
export class SessionService {
  private readonly cleAccessToken = 'access_token';
  private readonly cleRefreshToken = 'refresh_token';
  private readonly cleUtilisateur = 'utilisateur_connecte';

  utilisateur = signal<Utilisateur | null>(this.lireUtilisateur());
  estConnecte = signal<boolean>(this.aUneSessionLocale());

  definirSession(access: string, refresh: string, utilisateur: Utilisateur): void {
    localStorage.setItem(this.cleAccessToken, access);
    localStorage.setItem(this.cleRefreshToken, refresh);
    localStorage.setItem(this.cleUtilisateur, JSON.stringify(utilisateur));
    this.utilisateur.set(utilisateur);
    this.estConnecte.set(true);
  }

  mettreAJourTokens(access: string, refresh?: string): void {
    localStorage.setItem(this.cleAccessToken, access);
    if (refresh) {
      localStorage.setItem(this.cleRefreshToken, refresh);
    }
    this.estConnecte.set(this.aUneSessionLocale());
  }

  viderSession(): void {
    localStorage.removeItem(this.cleAccessToken);
    localStorage.removeItem(this.cleRefreshToken);
    localStorage.removeItem(this.cleUtilisateur);
    this.utilisateur.set(null);
    this.estConnecte.set(false);
  }

  obtenirAccessToken(): string | null {
    return localStorage.getItem(this.cleAccessToken);
  }

  obtenirRefreshToken(): string | null {
    return localStorage.getItem(this.cleRefreshToken);
  }

  private lireUtilisateur(): Utilisateur | null {
    const brut = localStorage.getItem(this.cleUtilisateur);
    if (!brut) return null;

    try {
      return JSON.parse(brut);
    } catch {
      return null;
    }
  }

  private aUneSessionLocale(): boolean {
    return !!(localStorage.getItem(this.cleAccessToken) || localStorage.getItem(this.cleRefreshToken));
  }
}
