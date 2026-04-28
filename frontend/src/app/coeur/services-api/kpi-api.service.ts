import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import {
  TauxPanneActuelKpi,
  TesterCurrentStatusKpi,
  TesterFpyInstantKpi,
} from '../modeles/kpi.model';
import { ApiListResponse, normalizeListResponse } from './api-base';

@Injectable({
  providedIn: 'root',
})
export class KpiApiService {
  private readonly http = inject(HttpClient);

  obtenirFpyInstantTesteurs(): Observable<TesterFpyInstantKpi[]> {
    return this.http
      .get<ApiListResponse<TesterFpyInstantKpi>>(API_ENDPOINTS.kpiTesteursFpyInstant)
      .pipe(map(normalizeListResponse));
  }

  obtenirStatutActuelTesteurs(): Observable<TesterCurrentStatusKpi[]> {
    return this.http
      .get<ApiListResponse<TesterCurrentStatusKpi>>(API_ENDPOINTS.kpiStatutTesteurs)
      .pipe(map(normalizeListResponse));
  }

  obtenirTauxPannesActuel(): Observable<TauxPanneActuelKpi> {
    return this.http.get<TauxPanneActuelKpi>(API_ENDPOINTS.kpiTauxPannesActuel);
  }
}
