import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { Alerte } from '../modeles/alerte.model';
import { ApiListResponse, normalizeListResponse } from './api-base';

@Injectable({
  providedIn: 'root',
})
export class AlertesApi {
  private readonly http = inject(HttpClient);

  lister(): Observable<Alerte[]> {
    return this.http
      .get<ApiListResponse<Alerte>>(API_ENDPOINTS.alertes)
      .pipe(map(normalizeListResponse));
  }
}
