import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import {
  EtalonnageInstrument,
  EtalonnageInstrumentCreatePayload,
  EtalonnageRecord,
  EtalonnageRecordCreatePayload,
} from '../modeles/etalonnage.model';
import { ApiListResponse, normalizeListResponse } from './api-base';

@Injectable({
  providedIn: 'root',
})
export class EtalonnageApi {
  private readonly http = inject(HttpClient);

  listerInstruments(): Observable<EtalonnageInstrument[]> {
    return this.http
      .get<ApiListResponse<EtalonnageInstrument>>(API_ENDPOINTS.etalonnageInstruments)
      .pipe(map(normalizeListResponse));
  }

  creerInstrument(payload: EtalonnageInstrumentCreatePayload): Observable<EtalonnageInstrument> {
    return this.http.post<EtalonnageInstrument>(API_ENDPOINTS.etalonnageInstruments, payload);
  }

  listerRecords(): Observable<EtalonnageRecord[]> {
    return this.http
      .get<ApiListResponse<EtalonnageRecord>>(API_ENDPOINTS.etalonnageRecords)
      .pipe(map(normalizeListResponse));
  }

  creerRecord(payload: EtalonnageRecordCreatePayload, reportFile?: File | null): Observable<EtalonnageRecord> {
    const formData = new FormData();
    formData.append('instrument', String(payload.instrument));
    formData.append('provider_name', payload.provider_name || '');
    formData.append('calibration_date', payload.calibration_date);
    formData.append('next_due_date', payload.next_due_date);
    formData.append('calibration_state', payload.calibration_state);
    formData.append('result', payload.result);
    formData.append('comment', payload.comment || '');

    if (reportFile) {
      formData.append('report_file', reportFile);
    }

    return this.http.post<EtalonnageRecord>(API_ENDPOINTS.etalonnageRecords, formData);
  }
}
