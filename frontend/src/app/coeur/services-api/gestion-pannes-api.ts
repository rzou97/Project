import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { GestionPanne } from '../modeles/gestion-panne.model';
import { ApiListResponse, normalizeListResponse } from './api-base';

@Injectable({
  providedIn: 'root',
})
export class GestionPannesApi {
  private readonly http = inject(HttpClient);

  lister(): Observable<GestionPanne[]> {
    return this.http
      .get<ApiListResponse<GestionPanne>>(API_ENDPOINTS.gestionPannes)
      .pipe(map(normalizeListResponse));
  }
}
