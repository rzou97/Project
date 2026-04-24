import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { Carte } from '../modeles/carte.model';
import { ApiListResponse, normalizeListResponse } from './api-base';

@Injectable({
  providedIn: 'root',
})
export class CartesApi {
  private readonly http = inject(HttpClient);

  lister(): Observable<Carte[]> {
    return this.http
      .get<ApiListResponse<Carte>>(API_ENDPOINTS.cartes)
      .pipe(map(normalizeListResponse));
  }
}
