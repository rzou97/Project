export const PDR_AFFECTATION_TYPES = ['GENERAL', 'TESTER', 'INSTRUMENT'] as const;
export const PDR_UNITS = ['PIECE'] as const;

export type PdrAffectationType = (typeof PDR_AFFECTATION_TYPES)[number];
export type PdrUnit = (typeof PDR_UNITS)[number];

export interface Pdr {
  id: number;
  part_code: string;
  designation: string;
  manufacturer: string;
  affectation_type: PdrAffectationType | string;
  affectation_value: string;
  unit: PdrUnit | string;
  minimum_stock: number;
  is_active: boolean;
  image_url?: string | null;
  created_at: string;
  updated_at: string;
}

export interface PdrCreatePayload {
  part_code: string;
  designation: string;
  manufacturer?: string;
  affectation_type: PdrAffectationType | string;
  affectation_value?: string;
  unit: PdrUnit | string;
  minimum_stock: number;
  is_active: boolean;
}

export interface PdrStock {
  id: number;
  part: number;
  current_quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  last_inventory_at: string | null;
  created_at: string;
  updated_at: string;
}
