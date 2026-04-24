import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { ActionReparation, TicketReparation } from '../modeles/action-reparation.model';
import { ApiListResponse, normalizeListResponse } from './api-base';

@Injectable({
  providedIn: 'root',
})
export class ActionsReparationApi {
  private readonly http = inject(HttpClient);

  listerTickets(): Observable<TicketReparation[]> {
    return this.http
      .get<ApiListResponse<TicketReparation>>(API_ENDPOINTS.ticketsReparation)
      .pipe(map(normalizeListResponse));
  }

  listerActions(): Observable<ActionReparation[]> {
    return this.http
      .get<ApiListResponse<ActionReparation>>(API_ENDPOINTS.actionsReparation)
      .pipe(map(normalizeListResponse));
  }
}
