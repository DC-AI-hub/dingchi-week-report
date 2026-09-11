import { encryptPassword } from "@/shared/security/password"

import { request } from "@/shared/api/http"

import type { Role, Session } from "./types"

/**
 * 用户登录：POST /v1/auth/login/（统一客户端拼接 /api）。
 * 请求：username、明文密码（函数内部先通过 RSA-OAEP-SHA256 加密）、可选 role_code。
 * 响应：Session，包含 Bearer 令牌、用户、全部角色和激活角色；错误：INVALID_REQUEST、AUTHENTICATION_FAILED。
 * 安全/追踪：加密失败直接阻止请求，http 层统一附加 X-Trace-ID；兼容：新增会话字段只增不删。
 */
export async function login(username: string, password: string, roleCode?: string): Promise<Session> {
  const encryptedPassword = await encryptPassword(password)
  return request<Session>({
    method: "POST",
    url: "/v1/auth/login/",
    data: { username, password: encryptedPassword, role_code: roleCode },
  })
}

/**
 * 获取当前会话：GET /v1/auth/me/；Bearer 认证、无参数、幂等。
 * 返回用户、角色集合和当前角色；错误：AUTHENTICATION_FAILED；X-Trace-ID 由共享 HTTP 层处理。
 */
export function getMe(): Promise<Pick<Session, "user" | "roles" | "active_role">> {
  return request<Pick<Session, "user" | "roles" | "active_role">>({
    method: "GET",
    url: "/v1/auth/me/",
  })
}

/**
 * 切换角色：POST /v1/auth/switch-role/；Bearer 认证，请求 role_code，返回新的 Session。
 * 仅允许已分配角色；错误：AUTHENTICATION_FAILED、FORBIDDEN；响应带 X-Trace-ID，字段向后兼容。
 */
export function switchRole(roleCode: string): Promise<Session> {
  return request<Session>({
    method: "POST",
    url: "/v1/auth/switch-role/",
    data: { role_code: roleCode },
  })
}

/**
 * 注销：POST /v1/auth/logout/；Bearer 认证，无请求参数，客户端随后清除令牌。
 * 服务端令牌按配置过期；错误：AUTHENTICATION_FAILED；响应带 X-Trace-ID。
 */
export function logout(): Promise<{ logged_out: boolean }> {
  return request<{ logged_out: boolean }>({ method: "POST", url: "/v1/auth/logout/" })
}

export function roleLabel(role: Role | null | undefined): string {
  return role?.role_name || "未选择角色"
}
