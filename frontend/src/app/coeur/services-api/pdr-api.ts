import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { Pdr, PdrCreatePayload, PdrStock } from '../modeles/pdr.model';
import { ApiListResponse, normalizeListResponse } from './api-base';

@Injectable({
  providedIn: 'root',
})
export class PdrApi {
  private readonly http = inject(HttpClient);

  lister(): Observable<Pdr[]> {
    return this.listerParts();
  }

  listerParts(): Observable<Pdr[]> {
    return this.http
      .get<ApiListResponse<Pdr>>(API_ENDPOINTS.piecesRechangeParts)
      .pipe(map(normalizeListResponse));
  }

  creerPart(payload: PdrCreatePayload): Observable<Pdr> {
    return this.http.post<Pdr>(API_ENDPOINTS.piecesRechangeParts, payload);
  }

  listerStocks(): Observable<PdrStock[]> {
    return this.http
      .get<ApiListResponse<PdrStock>>(API_ENDPOINTS.piecesRechangeStocks)
      .pipe(map(normalizeListResponse));
  }
}
