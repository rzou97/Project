import { HttpParams } from '@angular/common/http';

export interface ApiPaginatedResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
}

export type ApiListResponse<T> = T[] | ApiPaginatedResponse<T>;
export type ApiQueryValue = string | number | boolean | null | undefined;

export interface ApiPage<T> {
  items: T[];
  count: number;
  next: string | null;
  previous: string | null;
  page: number;
  pageSize: number;
  totalPages: number;
}

export function normalizeListResponse<T>(payload: ApiListResponse<T>): T[] {
  if (Array.isArray(payload)) {
    return payload;
  }

  return Array.isArray(payload.results) ? payload.results : [];
}

export function normalizePaginatedResponse<T>(
  payload: ApiListResponse<T>,
  page = 1,
  pageSize = 25
): ApiPage<T> {
  const items = normalizeListResponse(payload);

  if (Array.isArray(payload)) {
    const safePageSize = pageSize > 0 ? pageSize : Math.max(items.length, 1);
    return {
      items,
      count: items.length,
      next: null,
      previous: null,
      page,
      pageSize: safePageSize,
      totalPages: items.length === 0 ? 1 : Math.ceil(items.length / safePageSize),
    };
  }

  const safePageSize = pageSize > 0 ? pageSize : Math.max(items.length, 1);
  const count = payload.count ?? items.length;

  return {
    items,
    count,
    next: payload.next ?? null,
    previous: payload.previous ?? null,
    page,
    pageSize: safePageSize,
    totalPages: count === 0 ? 1 : Math.ceil(count / safePageSize),
  };
}

export function buildHttpParams(query: Record<string, ApiQueryValue>): HttpParams {
  let params = new HttpParams();

  Object.entries(query).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') {
      return;
    }

    params = params.set(key, String(value));
  });

  return params;
}
