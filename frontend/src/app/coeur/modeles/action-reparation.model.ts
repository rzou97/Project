export interface TicketReparation {
  id: number;
  failure_case: number;
  serial_number: string;
  client_reference: string | null;
  internal_reference: string | null;
  failure_status: string | null;
  detected_in_phase: string | null;
  detected_on_tester: string | null;
  failure_type: string | null;
  failure_message: string | null;
  board_status: string | null;
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
  client_reference?: string | null;
  internal_reference?: string | null;
  failure_status?: string | null;
  failure_message?: string | null;
  ticket_status?: string | null;
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
  failure_case?: number | null;
  repair_ticket?: number | null;
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
  recommended_steps: string[];
  recommended_parts: string[];
  success_rate: number | null;
  version: string;
  generated_at: string;
}

export interface FailureEnrichment {
  id: number;
  failure_case: number;
  serial_number: string;
  client_reference: string | null;
  internal_reference: string | null;
  failure_type: string | null;
  failure_message: string | null;
  failure_status: string | null;
  normalized_family: string | null;
  normalized_signature: string | null;
  probable_root_cause: string | null;
  suggested_action: string | null;
  suggested_checks: string[];
  suspect_components: string[];
  supporting_history_count: number;
  confidence_score: number | null;
  needs_human_review: boolean;
  enrichment_source: string | null;
  model_name: string | null;
  model_version: string | null;
  prompt_version: string | null;
  evidence_json: Record<string, unknown>;
  enriched_at: string;
  created_at: string;
  updated_at: string;
}

export interface RepairPrediction {
  id: number;
  failure_case?: number | null;
  repair_ticket?: number | null;
  prediction_type: string;
  target_serial_number: string;
  predicted_cause: string | null;
  recommended_action: string | null;
  recommended_procedure: number | null;
  recommended_procedure_name?: string | null;
  prediction_source: string | null;
  model_name: string | null;
  model_version: string | null;
  input_signature: string | null;
  explanation_json?: Record<string, unknown> | null;
  confidence_score: number | null;
  predicted_at: string;
  created_at: string;
}
