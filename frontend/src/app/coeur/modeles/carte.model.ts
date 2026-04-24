export interface Carte {
  id: number;
  serial_number: string;
  client_reference: string | null;
  internal_reference: string | null;
  current_status: string;
  first_seen_at: string | null;
  last_seen_at: string | null;
}
