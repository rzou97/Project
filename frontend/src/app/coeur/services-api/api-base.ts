export interface ApiPaginatedResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
}

export type ApiListResponse<T> = T[] | ApiPaginatedResponse<T>;

export function normalizeListResponse<T>(payload: ApiListResponse<T>): T[] {
  if (Array.isArray(payload)) {
    return payload;
  }

  return Array.isArray(payload.results) ? payload.results : [];
}
