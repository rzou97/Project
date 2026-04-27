export interface Carte {
  id: number;
  serial_number: string;
  client_reference: string | null;
  internal_reference: string | null;
  current_status: string;
  first_seen_at: string | null;
  last_seen_at: string | null;
}

export interface MouvementTest {
  id: number;
  board: number | null;
  serial_number: string;
  client_reference: string | null;
  internal_reference: string | null;
  operator_name: string | null;
  tester_id: string | null;
  test_phase: string | null;
  result: string;
  failure_type: string | null;
  failure_message: string | null;
  tested_at: string;
  source_event_key: string;
  raw_ingested_ts: string | null;
}
