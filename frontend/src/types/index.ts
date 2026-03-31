export type UserRole = "admin" | "manager" | "rep" | "viewer";
export type TenantStatus = "active" | "deactivated";
export type UserStatus = "active" | "deactivated";
export type DealStage =
  | "qualification"
  | "proposal"
  | "negotiation"
  | "closed_won"
  | "closed_lost";
export type TaskPriority = "low" | "medium" | "high";
export type TaskStatus = "to_do" | "in_progress" | "done";

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  tenant_id: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  status: TenantStatus;
}

export interface Contact {
  id: string;
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string | null;
  notes: string | null;
  company_id: string | null;
  tenant_id: string;
  archived: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: string;
  name: string;
  industry: string | null;
  website: string | null;
  notes: string | null;
  tenant_id: string;
  archived: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Deal {
  id: string;
  name: string;
  value: number;
  expected_close_date: string | null;
  stage: DealStage;
  close_date: string | null;
  loss_reason: string | null;
  owner_id: string;
  company_id: string;
  primary_contact_id: string;
  tenant_id: string;
  archived: boolean;
  created_by: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  due_date: string;
  priority: TaskPriority;
  status: TaskStatus;
  assignee_id: string;
  contact_id: string | null;
  deal_id: string | null;
  tenant_id: string;
  archived: boolean;
  completed_at: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  status: number;
}
