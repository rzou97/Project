export interface TicketReparation {
  id: number;
  serial_number: string;
  client_reference: string | null;
  internal_reference: string | null;
  ticket_code: string;
  ticket_status: string;
  cycle_number: number;
  opened_at: string;
  closed_at: string | null;
  repair_effectiveness: number | null;
}

export interface ActionReparation {
  id: number;
  ticket_code?: string | null;
  serial_number?: string | null;
  defect_type: string | null;
  observed_defect: string | null;
  detected_cause: string | null;
  action_taken: string | null;
  action_progress: string | null;
  performed_at: string | null;
  repair_ticket?: number;
  technician_matricule?: string | null;
}

export interface RepairHistory {
  id: number;
  serial_number: string;
  client_reference: string | null;
  internal_reference: string | null;
  detected_in_phase: string | null;
  detected_on_tester: string | null;
  failure_type: string | null;
  failure_message: string | null;
  technician_matricule: string | null;
  detected_cause: string | null;
  action_taken: string | null;
  retest_result: string | null;
  final_outcome: string | null;
  repair_cycle_count: number;
  created_at: string;
}

export interface RepairProcedureTemplate {
  id: number;
  procedure_name: string;
  failure_type: string;
  failure_signature: string;
  recommended_steps: string;
  recommended_parts: string;
  success_rate: number | null;
  version: string;
  generated_at: string;
}

export interface RepairPrediction {
  id: number;
  prediction_type: string;
  target_serial_number: string;
  predicted_cause: string | null;
  recommended_action: string | null;
  recommended_procedure: string | null;
  confidence_score: number | null;
  predicted_at: string;
}
