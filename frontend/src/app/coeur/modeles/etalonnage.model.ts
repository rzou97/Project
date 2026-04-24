export const ETALONNAGE_TYPE_CODES = [
  'CHARGE',
  'DIELECTRIC',
  'GB_TESTER',
  'MESURE',
  'MULTIMETRE',
  'OSCILL',
  'SWITCH',
] as const;

export const ETALONNAGE_STATES = ['GOOD', 'RESTRICTED', 'KO'] as const;
export const ETALONNAGE_CONFORMITY = ['CONFORM', 'NON_CONFORM'] as const;

export type EtalonnageTypeCode = (typeof ETALONNAGE_TYPE_CODES)[number];
export type EtalonnageState = (typeof ETALONNAGE_STATES)[number];
export type EtalonnageConformity = (typeof ETALONNAGE_CONFORMITY)[number];

export interface EtalonnageInstrument {
  id: number;
  instrument_code: string;
  designation: string;
  type_code: EtalonnageTypeCode | string;
  sub_family_code: string;
  serial_number: string;
  brand: string;
  affectation: string;
  calibration_frequency_months: number;
  last_calibration_date: string | null;
  next_calibration_date: string | null;
  calibration_state: EtalonnageState | string;
  conformity_status: EtalonnageConformity | string;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EtalonnageInstrumentCreatePayload {
  instrument_code: string;
  designation: string;
  type_code: EtalonnageTypeCode;
  sub_family_code?: string;
  serial_number?: string;
  brand?: string;
  affectation?: string;
  calibration_frequency_months: number;
  is_active: boolean;
}

export interface EtalonnageRecord {
  id: number;
  instrument: number;
  instrument_code: string;
  provider_name: string;
  calibration_date: string;
  next_due_date: string;
  calibration_state: EtalonnageState | string;
  result: EtalonnageConformity | string;
  comment: string;
  report_file: string | null;
  created_at: string;
  updated_at: string;
}

export interface EtalonnageRecordCreatePayload {
  instrument: number;
  provider_name?: string;
  calibration_date: string;
  next_due_date: string;
  calibration_state: EtalonnageState;
  result: EtalonnageConformity;
  comment?: string;
}
