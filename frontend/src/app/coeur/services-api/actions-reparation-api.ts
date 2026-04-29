import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { ActionReparation, TicketReparation } from '../modeles/action-reparation.model';
import {
  ApiListResponse,
  ApiPage,
  buildHttpParams,
  normalizePaginatedResponse,
} from './api-base';

export interface TicketListQuery {
  failure_case?: number;
  serial_number?: string;
  client_reference?: string;
  internal_reference?: string;
  ticket_code?: string;
  ticket_status?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

export interface ActionListQuery {
  repair_ticket?: number;
  serial_number?: string;
  client_reference?: string;
  internal_reference?: string;
  ticket_code?: string;
  defect_type?: string;
  action_progress?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

export interface CreateRepairActionPayload {
  repair_ticket: number;
  defect_type?: string;
  observed_defect?: string;
  detected_cause?: string;
  action_taken: string;
  action_progress: string;
  performed_at: string;
}

export interface UpdateRepairTicketPayload {
  ticket_status: string;
  closed_at?: string | null;
  repair_effectiveness?: number | null;
}

@Injectable({
  providedIn: 'root',
})
export class ActionsReparationApi {
  private readonly http = inject(HttpClient);

  listerTickets(query: TicketListQuery = {}): Observable<ApiPage<TicketReparation>> {
    const page = query.page ?? 1;
    const pageSize = query.page_size ?? 8;

    return this.http
      .get<ApiListResponse<TicketReparation>>(API_ENDPOINTS.ticketsReparation, {
        params: buildHttpParams({
          ...query,
          page,
          page_size: pageSize,
          ordering: query.ordering ?? '-opened_at',
        }),
      })
      .pipe(map((payload) => normalizePaginatedResponse(payload, page, pageSize)));
  }

  obtenirTicket(ticketId: number): Observable<TicketReparation> {
    return this.http.get<TicketReparation>(`${API_ENDPOINTS.ticketsReparation}${ticketId}/`);
  }

  listerActions(query: ActionListQuery = {}): Observable<ApiPage<ActionReparation>> {
    const page = query.page ?? 1;
    const pageSize = query.page_size ?? 8;

    return this.http
      .get<ApiListResponse<ActionReparation>>(API_ENDPOINTS.actionsReparation, {
        params: buildHttpParams({
          ...query,
          page,
          page_size: pageSize,
          ordering: query.ordering ?? '-performed_at',
        }),
      })
      .pipe(map((payload) => normalizePaginatedResponse(payload, page, pageSize)));
  }

  creerAction(payload: CreateRepairActionPayload): Observable<ActionReparation> {
    return this.http.post<ActionReparation>(API_ENDPOINTS.actionsReparation, payload);
  }

  mettreAJourTicket(
    ticketId: number,
    payload: UpdateRepairTicketPayload
  ): Observable<TicketReparation> {
    return this.http.patch<TicketReparation>(`${API_ENDPOINTS.ticketsReparation}${ticketId}/`, payload);
  }
}
