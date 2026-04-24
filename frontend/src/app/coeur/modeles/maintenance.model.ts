export interface Maintenance {
  id: number;
  plan_name?: string;
  maintenance_type?: string;
  due_date?: string | null;
  status?: string;
}
