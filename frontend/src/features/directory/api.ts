import { request } from "@/shared/api/http"

import type {
  DeleteRoleResult,
  DirectoryGroup,
  DirectoryRole,
  DirectoryUser,
  RoleMutationPayload,
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
 * report_template_code，description 可为空；scope 取 self/team/all。
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

/** 查询组织分组：GET /v1/groups/；Bearer 认证；响应 data.items。 */
export function listGroups(): Promise<{ items: DirectoryGroup[] }> { return request<{ items: DirectoryGroup[] }>({ method: "GET", url: "/v1/groups/" }) }

/** 新增组织分组：POST /v1/groups/new/；请求 group_code、group_name、parent_group_id。 */
export function createGroup(payload: Partial<DirectoryGroup>): Promise<DirectoryGroup> { return request<DirectoryGroup>({ method: "POST", url: "/v1/groups/new/", data: payload }) }

/** 修改组织分组：PATCH /v1/groups/{id}/；响应更新后的分组。 */
export function updateGroup(id: string, payload: Partial<DirectoryGroup>): Promise<DirectoryGroup> { return request<DirectoryGroup>({ method: "PATCH", url: `/v1/groups/${id}/`, data: payload }) }

/** 查询用户目录：GET /v1/users/；可选 role_code/group_id；响应 data.items 含上下级和角色。 */
export function listUsers(filters: { role_code?: string; group_id?: string } = {}): Promise<{ items: DirectoryUser[] }> { return request<{ items: DirectoryUser[] }>({ method: "GET", url: "/v1/users/", params: filters }) }

/** 新增用户：POST /v1/users/new/；password 必须由前端 RSA-OAEP-SHA256 加密。 */
export function createUser(payload: Record<string, unknown>): Promise<DirectoryUser> { return request<DirectoryUser>({ method: "POST", url: "/v1/users/new/", data: payload }) }

/** 修改用户：PATCH /v1/users/{id}/；支持资料、上下级、分组、状态和角色集合。 */
export function updateUser(id: string, payload: Record<string, unknown>): Promise<DirectoryUser> { return request<DirectoryUser>({ method: "PATCH", url: `/v1/users/${id}/`, data: payload }) }
