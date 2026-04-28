export interface TesterFpyInstantKpi {
  tester_id: string;
  day_date: string;
  unique_sn_tested: number;
  unique_sn_passed: number;
  fpy_instant: number;
  last_test_at: string | null;
}

export interface TesterCurrentStatusKpi {
  tester_id: string;
  operator_name: string | null;
  internal_reference: string | null;
  last_test_at: string | null;
  current_fail_rate: number;
  current_status: string;
  alert_status: string;
  open_alert_count: number;
}

export interface TauxPanneActuelReferenceKpi {
  internal_reference: string;
  total_sn: number;
  defective_sn: number;
  current_failure_rate: number;
}

export interface TauxPanneActuelKpi {
  total_sn: number;
  total_defective_sn: number;
  current_failure_rate: number;
  references: TauxPanneActuelReferenceKpi[];
}
