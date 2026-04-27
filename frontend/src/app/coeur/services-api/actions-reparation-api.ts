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
  serial_number?: string;
  internal_reference?: string;
  ticket_code?: string;
  ticket_status?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

export interface ActionListQuery {
  serial_number?: string;
  ticket_code?: string;
  defect_type?: string;
  action_progress?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
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
}
