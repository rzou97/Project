import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { Carte, MouvementTest } from '../modeles/carte.model';
import {
  ApiListResponse,
  ApiPage,
  buildHttpParams,
  normalizePaginatedResponse,
} from './api-base';

export interface BoardListQuery {
  serial_number?: string;
  internal_reference?: string;
  current_status?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

export interface TestMovementQuery {
  test_phase?: string;
  result?: string;
  tester_id?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

@Injectable({
  providedIn: 'root',
})
export class CartesApi {
  private readonly http = inject(HttpClient);

  lister(query: BoardListQuery = {}): Observable<ApiPage<Carte>> {
    const page = query.page ?? 1;
    const pageSize = query.page_size ?? 12;

    return this.http
      .get<ApiListResponse<Carte>>(API_ENDPOINTS.cartes, {
        params: buildHttpParams({
          ...query,
          page,
          page_size: pageSize,
        }),
      })
      .pipe(map((payload) => normalizePaginatedResponse(payload, page, pageSize)));
  }

  recupererParSerial(serialNumber: string): Observable<Carte | null> {
    return this.lister({
      serial_number: serialNumber,
      page: 1,
      page_size: 1,
      ordering: '-last_seen_at',
    }).pipe(
      map(({ items }) => {
        const normalizedTarget = serialNumber.trim().toUpperCase();
        return (
          items.find((item) => item.serial_number.trim().toUpperCase() === normalizedTarget) ??
          items[0] ??
          null
        );
      })
    );
  }

  listerMouvements(
    serialNumber: string,
    query: TestMovementQuery = {}
  ): Observable<ApiPage<MouvementTest>> {
    const page = query.page ?? 1;
    const pageSize = query.page_size ?? 10;

    return this.http
      .get<ApiListResponse<MouvementTest>>(API_ENDPOINTS.resultatsTest, {
        params: buildHttpParams({
          serial_number: serialNumber,
          ordering: query.ordering ?? '-tested_at',
          page,
          page_size: pageSize,
          test_phase: query.test_phase,
          result: query.result,
          tester_id: query.tester_id,
        }),
      })
      .pipe(map((payload) => normalizePaginatedResponse(payload, page, pageSize)));
  }
}
