export interface GestionPanne {
  id: number;
  serial_number: string;
  client_reference: string | null;
  internal_reference: string | null;
  failure_status: string;
  detected_in_phase: string | null;
  detected_on_tester: string | null;
  failure_type: string | null;
  failure_message: string | null;
  opened_at: string;
  closed_at: string | null;
}
