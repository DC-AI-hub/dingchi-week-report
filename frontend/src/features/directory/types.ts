export interface DirectoryRole {
  id: string
  role_code: string
  role_name: string
  scope: "self" | "team" | "all" | string
  description: string
  report_template_code: string
  role_group_code: string
  status: string
  sort_order?: number
}

export interface RoleMutationPayload {
  role_code: string
  role_name: string
  scope: string
  description: string
  report_template_code: string
  role_group_code: string
}

export interface DeleteRoleResult {
  id: string
  deleted: true
}

export interface DeleteDirectoryResult {
  id: string
  deleted: true
}

export interface DirectoryGroup {
  id: string
  group_code: string
  group_name: string
  description: string
  parent_group_id: string | null
  is_system?: boolean
  status: string
}

export interface DirectoryUser {
  id: string
  username: string
  employee_no: string
  display_name: string
  email: string
  phone: string
  manager_id: string | null
  group_id: string | null
  group_name?: string | null
  avatar_color: string
  status: string
  role_codes: string[]
  role_names: string[]
}

/** 周报责任人/协作人下拉所需的最小用户信息。 */
export interface DirectoryUserOption {
  id: string
  employee_no: string
  display_name: string
  username: string
  group_id: string | null
}

export interface GroupMutationPayload {
  group_code: string
  group_name: string
  description: string
  parent_group_id: string | null
}

export interface UserMutationPayload {
  username: string
  employee_no?: string
  display_name: string
  email: string
  phone: string
  password?: string
  group_id: string | null
  manager_id: string | null
  role_codes: string[]
  status?: string
}
