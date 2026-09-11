export interface DirectoryRole {
  id: string
  role_code: string
  role_name: string
  scope: "self" | "team" | "all" | string
  description: string
  report_template_code: string
  status: string
  sort_order?: number
}

export interface RoleMutationPayload {
  role_code: string
  role_name: string
  scope: "self" | "team" | "all"
  description: string
  report_template_code: string
}

export interface DeleteRoleResult {
  id: string
  deleted: true
}

export interface DirectoryGroup {
  id: string
  group_code: string
  group_name: string
  description: string
  parent_group_id: string | null
  status: string
}

export interface DirectoryUser {
  id: string
  username: string
  employee_no: string
  display_name: string
  email: string
  manager_id: string | null
  group_id: string | null
  group_name?: string | null
  avatar_color: string
  status: string
  role_codes: string[]
  role_names: string[]
}
