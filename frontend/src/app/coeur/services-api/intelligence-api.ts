import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import {
  FailureEnrichment,
  RepairHistory,
  RepairPrediction,
} from '../modeles/action-reparation.model';
import {
  ApiListResponse,
  ApiPage,
  buildHttpParams,
  normalizePaginatedResponse,
} from './api-base';

export interface FailureEnrichmentQuery {
  failure_case?: number;
  serial_number?: string;
  client_reference?: string;
  internal_reference?: string;
  failure_status?: string;
  normalized_family?: string;
  enrichment_source?: string;
  needs_human_review?: boolean;
  page?: number;
  page_size?: number;
  ordering?: string;
}

export interface RepairPredictionQuery {
  failure_case?: number;
  repair_ticket?: number;
  prediction_type?: string;
  prediction_source?: string;
  target_serial_number?: string;
  input_signature?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

export interface RepairHistoryQuery {
  serial_number?: string;
  client_reference?: string;
  internal_reference?: string;
  failure_type?: string;
  detected_in_phase?: string;
  detected_on_tester?: string;
  technician_matricule?: string;
  final_outcome?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

export interface AnalyzeFailurePayload {
  failure_case: number;
  repair_ticket?: number | null;
}

export interface AnalyzeFailureResponse {
  enrichment: FailureEnrichment;
  prediction: RepairPrediction;
}

@Injectable({
  providedIn: 'root',
})
export class IntelligenceApi {
  private readonly http = inject(HttpClient);

  listerEnrichissements(query: FailureEnrichmentQuery = {}): Observable<ApiPage<FailureEnrichment>> {
    const page = query.page ?? 1;
    const pageSize = query.page_size ?? 10;

    return this.http
      .get<ApiListResponse<FailureEnrichment>>(API_ENDPOINTS.enrichissementsPanne, {
        params: buildHttpParams({
          ...query,
          page,
          page_size: pageSize,
          ordering: query.ordering ?? '-enriched_at',
        }),
      })
      .pipe(map((payload) => normalizePaginatedResponse(payload, page, pageSize)));
  }

  listerPredictions(query: RepairPredictionQuery = {}): Observable<ApiPage<RepairPrediction>> {
    const page = query.page ?? 1;
    const pageSize = query.page_size ?? 10;

    return this.http
      .get<ApiListResponse<RepairPrediction>>(API_ENDPOINTS.predictionsReparation, {
        params: buildHttpParams({
          ...query,
          page,
          page_size: pageSize,
          ordering: query.ordering ?? '-predicted_at',
        }),
      })
      .pipe(map((payload) => normalizePaginatedResponse(payload, page, pageSize)));
  }

  listerHistorique(query: RepairHistoryQuery = {}): Observable<ApiPage<RepairHistory>> {
    const page = query.page ?? 1;
    const pageSize = query.page_size ?? 10;

    return this.http
      .get<ApiListResponse<RepairHistory>>(API_ENDPOINTS.historiqueReparation, {
        params: buildHttpParams({
          ...query,
          page,
          page_size: pageSize,
          ordering: query.ordering ?? '-created_at',
        }),
      })
      .pipe(map((payload) => normalizePaginatedResponse(payload, page, pageSize)));
  }

  analyserPanne(payload: AnalyzeFailurePayload): Observable<AnalyzeFailureResponse> {
    return this.http.post<AnalyzeFailureResponse>(API_ENDPOINTS.analysePanneIntelligence, payload);
  }
}
