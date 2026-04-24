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
