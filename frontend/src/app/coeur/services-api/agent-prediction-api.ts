import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import {
  RepairHistory,
  RepairPrediction,
  RepairProcedureTemplate,
} from '../modeles/action-reparation.model';
import { ApiListResponse, normalizeListResponse } from './api-base';

@Injectable({
  providedIn: 'root',
})
export class AgentPredictionApi {
  private readonly http = inject(HttpClient);

  listerHistorique(): Observable<RepairHistory[]> {
    return this.http
      .get<ApiListResponse<RepairHistory>>(API_ENDPOINTS.historiqueReparation)
      .pipe(map(normalizeListResponse));
  }

  listerProcedures(): Observable<RepairProcedureTemplate[]> {
    return this.http
      .get<ApiListResponse<RepairProcedureTemplate>>(API_ENDPOINTS.proceduresReparation)
      .pipe(map(normalizeListResponse));
  }

  listerPredictions(): Observable<RepairPrediction[]> {
    return this.http
      .get<ApiListResponse<RepairPrediction>>(API_ENDPOINTS.predictionsReparation)
      .pipe(map(normalizeListResponse));
  }
}
