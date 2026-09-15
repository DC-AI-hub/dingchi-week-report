import { request } from "@/shared/api/http"

import type { DictionaryItem } from "./types"

/**
 * 查询启用的静态字典项，供角色配置等页面使用。
 * 方法/路径：GET /v1/dictionaries/{dictType}/（统一客户端拼接 /api）；无请求体。
 * 路径参数：dictType 使用小写下划线编码，例如 role_scope、report_template。
 * 响应：data.items 按 sort_order 排序，包含 dict_code、dict_name、dict_value 等展示和校验字段。
 * 失败：401 表示未登录，400 表示字典类型编码非法；请求自动携带 Bearer Token 与 X-Trace-ID。
 */
export function listDictionaryItems(dictType: string): Promise<{ items: DictionaryItem[] }> {
  return request<{ items: DictionaryItem[] }>({
    method: "GET",
    url: `/v1/dictionaries/${encodeURIComponent(dictType)}/`,
  })
}
