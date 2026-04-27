import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { GestionPanne } from '../modeles/gestion-panne.model';
import {
  ApiListResponse,
  ApiPage,
  buildHttpParams,
  normalizePaginatedResponse,
} from './api-base';

export interface FailureListQuery {
  serial_number?: string;
  client_reference?: string;
  internal_reference?: string;
  failure_status?: string;
  detected_on_tester?: string;
  failure_type?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

@Injectable({
  providedIn: 'root',
})
export class GestionPannesApi {
  private readonly http = inject(HttpClient);

  lister(query: FailureListQuery = {}): Observable<ApiPage<GestionPanne>> {
    const page = query.page ?? 1;
    const pageSize = query.page_size ?? 12;

    return this.http
      .get<ApiListResponse<GestionPanne>>(API_ENDPOINTS.gestionPannes, {
        params: buildHttpParams({
          ...query,
          page,
          page_size: pageSize,
          ordering: query.ordering ?? '-opened_at',
        }),
      })
      .pipe(map((payload) => normalizePaginatedResponse(payload, page, pageSize)));
  }
}
