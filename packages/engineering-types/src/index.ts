export type Role =
  | "ADMIN"
  | "ENGINEERING_DIRECTOR"
  | "ENGINEER"
  | "TECHNICIAN"
  | "AUDITOR"
  | "VIEWER";

export interface Asset {
  id: string;
  site_id: string;
  tag: string;
  name: string;
  asset_type: string;
  status: string;
  specs?: Record<string, unknown>;
  is_demo: boolean;
}

export interface CalcEnvelope {
  discipline: string;
  calc_type: string;
  name: string;
  inputs: Record<string, unknown>;
  formula: string;
  units: Record<string, string>;
  assumptions: string[];
  result: Record<string, unknown>;
  check_status: "PASS" | "FAIL" | "WARN" | string;
  check_notes: string;
  source: string;
  version: string;
}
