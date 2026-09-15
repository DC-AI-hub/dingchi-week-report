import { request } from "@/shared/api/http"

import type {
  DeleteDirectoryResult,
  DeleteRoleResult,
  DirectoryGroup,
  DirectoryRole,
  DirectoryUser,
  DirectoryUserOption,
  GroupMutationPayload,
  RoleMutationPayload,
  UserMutationPayload,
} from "./types"

/**
 * 查询角色管理列表。
 * 方法/路径：GET /v1/roles/；请求参数：无；仅总裁或系统管理员可访问。
 * 响应：items 为未删除角色数组，ID 均为字符串；失败返回认证或权限错误码。
 * 请求由统一客户端携带 Bearer Token 与 X-Trace-ID；新增响应字段保持向后兼容。
 */
export function listRoles(): Promise<{ items: DirectoryRole[] }> {
  return request<{ items: DirectoryRole[] }>({ method: "GET", url: "/v1/roles/" })
}

/**
 * 新增角色并建立周报模板与数据范围映射。
 * 方法/路径：POST /v1/roles/new/；请求体必填 role_code、role_name、scope、
 * report_template_code，description 可为空；scope 和 report_template_code 必须使用字典接口返回的编码。
 * 响应：创建后的角色对象；编码重复返回 ROLE_CONFLICT，参数非法返回 INVALID_REQUEST。
 * 请求由统一客户端携带 Bearer Token 与 X-Trace-ID，角色编码创建后不可修改。
 */
export function createRole(payload: RoleMutationPayload): Promise<DirectoryRole> {
  return request<DirectoryRole>({ method: "POST", url: "/v1/roles/new/", data: payload })
}

/**
 * 修改角色名称、数据范围、说明和周报模板映射。
 * 方法/路径：PATCH /v1/roles/{id}/；路径 id 为 Snowflake 字符串；请求体字段定义同新增，
 * role_code 仅用于前端保持统一表单，后端不会修改该不可变编码。
 * 响应：更新后的角色对象；不存在返回 ROLE_NOT_FOUND，参数非法返回 INVALID_REQUEST。
 * 请求由统一客户端携带 Bearer Token 与 X-Trace-ID，既有字段语义保持兼容。
 */
export function updateRole(id: string, payload: RoleMutationPayload): Promise<DirectoryRole> {
  return request<DirectoryRole>({ method: "PATCH", url: `/v1/roles/${id}/`, data: payload })
}

/**
 * 删除角色配置（后端软删除并停用其用户分配，历史数据保留）。
 * 方法/路径：DELETE /v1/roles/{id}/；路径 id 为 Snowflake 字符串；请求体：无。
 * 响应：id 与 deleted=true；不存在返回 ROLE_NOT_FOUND，受保护或当前角色返回 ROLE_CONFLICT。
 * 请求由统一客户端携带 Bearer Token 与 X-Trace-ID；系统管理员角色禁止删除。
 */
export function deleteRole(id: string): Promise<DeleteRoleResult> {
  return request<DeleteRoleResult>({ method: "DELETE", url: `/v1/roles/${id}/` })
}

/**
 * 查询启用的组织分组，供目录筛选、分组树和用户表单使用。
 * 方法/路径：GET /v1/groups/；请求参数：无；认证：总裁或系统管理员；幂等：是。
 * 响应：items 为平铺分组数组，parent_group_id 用于构建多层级树；ID 均为字符串。
 */
export function listGroups(): Promise<{ items: DirectoryGroup[] }> {
  return request<{ items: DirectoryGroup[] }>({ method: "GET", url: "/v1/groups/" })
}

/**
 * 新增组织分组。
 * 方法/路径：POST /v1/groups/new/；请求体：group_code、group_name 必填，description 可为空，
 * parent_group_id 可为空表示根分组；响应为创建后的分组对象。
 */
export function createGroup(payload: GroupMutationPayload): Promise<DirectoryGroup> {
  return request<DirectoryGroup>({ method: "POST", url: "/v1/groups/new/", data: payload })
}

/**
 * 修改组织分组名称、说明和上级关系。
 * 方法/路径：PATCH /v1/groups/{id}/；请求体为部分 GroupMutationPayload（group_code 不修改）；
 * 响应为更新后的分组；不能移动到自身或下级节点。
 */
export function updateGroup(id: string, payload: Partial<GroupMutationPayload>): Promise<DirectoryGroup> {
  return request<DirectoryGroup>({ method: "PATCH", url: `/v1/groups/${id}/`, data: payload })
}

/**
 * 删除组织分组（后端软删除）。
 * 方法/路径：DELETE /v1/groups/{id}/；请求体：无；分组必须没有下级和在职成员；
 * 响应：id 与 deleted=true，历史周报数据保留。
 */
export function deleteGroup(id: string): Promise<DeleteDirectoryResult> {
  return request<DeleteDirectoryResult>({ method: "DELETE", url: `/v1/groups/${id}/` })
}

/** 查询用户目录：GET /v1/users/；可选 role_code/group_id；响应 data.items 含上下级和角色。 */
export function listUsers(
  filters: { role_code?: string; group_id?: string } = {},
): Promise<{ items: DirectoryUser[] }> {
  return request<{ items: DirectoryUser[] }>({ method: "GET", url: "/v1/users/", params: filters })
}

/**
 * 查询周报责任人和协作人下拉选项。
 * 方法/路径：GET /v1/users/options/；请求参数：无；认证：Bearer；幂等：是。
 * 响应仅返回在职用户的 id、工号、姓名、账号和主分组，不暴露密码等敏感字段。
 */
export function listUserOptions(): Promise<{ items: DirectoryUserOption[] }> {
  return request<{ items: DirectoryUserOption[] }>({ method: "GET", url: "/v1/users/options/" })
}

/**
 * 新增用户并分配角色、分组和直属上级。
 * 方法/路径：POST /v1/users/new/；请求体：username、employee_no、display_name、password、role_codes 必填，
 * email/group_id/manager_id 可为空；password 必须由前端 RSA-OAEP-SHA256 加密；响应不返回密码。
 */
export function createUser(payload: UserMutationPayload & { password: string }): Promise<DirectoryUser> {
  return request<DirectoryUser>({ method: "POST", url: "/v1/users/new/", data: payload })
}

/**
 * 修改用户资料、上下级、分组、状态和角色集合。
 * 方法/路径：PATCH /v1/users/{id}/；请求体为部分 UserMutationPayload，password 可省略表示不修改；
 * 响应为更新后的用户对象，不返回密码。
 */
export function updateUser(id: string, payload: Partial<UserMutationPayload>): Promise<DirectoryUser> {
  return request<DirectoryUser>({ method: "PATCH", url: `/v1/users/${id}/`, data: payload })
}

/**
 * 删除用户（后端软删除并停用其角色、分组成员关系）。
 * 方法/路径：DELETE /v1/users/{id}/；请求体：无；不能删除当前登录用户；响应为 id/deleted=true。
 */
export function deleteUser(id: string): Promise<DeleteDirectoryResult> {
  return request<DeleteDirectoryResult>({ method: "DELETE", url: `/v1/users/${id}/` })
}
