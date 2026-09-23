import { defineAsyncComponent, type Component } from "vue"

/**
 * 周报模板页面注册表。
 *
 * key 必须使用完整 template_code（包含版本号）。角色只负责绑定模板，
 * 因此这里不能按 role_code 分流；新增模板版本时新增独立目录和注册项。
 */
const templateEditors: Record<string, Component> = {
  delivery_specialist_v1: defineAsyncComponent(
    () => import("@/views/weekly-report/templates/delivery-specialist/v1/EditView.vue"),
  ),
  delivery_assistant_v1: defineAsyncComponent(
    () => import("@/views/weekly-report/templates/delivery-assistant/v1/EditView.vue"),
  ),
  recruitment_v1: defineAsyncComponent(
    () => import("@/views/weekly-report/templates/recruitment/v1/EditView.vue"),
  ),
  ito_sales_v1: defineAsyncComponent(
    () => import("@/views/weekly-report/templates/ito-sales/v1/EditView.vue"),
  ),
  innovation_sales_v1: defineAsyncComponent(
    () => import("@/views/weekly-report/templates/innovation-sales/v1/EditView.vue"),
  ),
  functional_group_v1: defineAsyncComponent(
    () => import("@/views/weekly-report/templates/functional-group/v1/EditView.vue"),
  ),
}

export function resolveTemplateEditor(templateCode: string): Component | null {
  // 模板编码必须精确匹配已注册的版本页面；未知编码不能回退到默认页面。
  return templateEditors[templateCode] || null
}
