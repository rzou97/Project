import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { Maintenance } from '../modeles/maintenance.model';
import { ApiListResponse, normalizeListResponse } from './api-base';

@Injectable({
  providedIn: 'root',
})
export class MaintenanceApi {
  private readonly http = inject(HttpClient);

  lister(): Observable<Maintenance[]> {
    return this.http
      .get<ApiListResponse<Maintenance>>(API_ENDPOINTS.maintenance)
      .pipe(map(normalizeListResponse));
  }
}
