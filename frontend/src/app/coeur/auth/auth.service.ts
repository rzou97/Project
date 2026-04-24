import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { SessionService } from './session.service';
import {
  ActivationReponse,
  AuthentificationPayload,
  AuthentificationReponse,
  InscriptionPayload,
  InscriptionReponse,
} from '../modeles/auth.model';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly sessionService = inject(SessionService);

  seConnecter(payload: AuthentificationPayload): Observable<AuthentificationReponse> {
    return this.http.post<AuthentificationReponse>(API_ENDPOINTS.connexion, payload).pipe(
      tap((reponse) => {
        this.sessionService.definirSession(
          reponse.access,
          reponse.refresh,
          reponse.user
        );
      })
    );
  }

  seDeconnecter(): void {
    this.sessionService.viderSession();
  }

  inscrire(payload: InscriptionPayload): Observable<InscriptionReponse> {
    return this.http.post<InscriptionReponse>(API_ENDPOINTS.inscription, payload);
  }

  activerCompte(uidb64: string, token: string): Observable<ActivationReponse> {
    return this.http.get<ActivationReponse>(`${API_ENDPOINTS.activationCompteBase}${uidb64}/${token}/`);
  }
}
