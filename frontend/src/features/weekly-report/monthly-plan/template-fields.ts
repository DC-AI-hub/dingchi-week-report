export function monthlyPlanScopeLabel(templateCode: string): string {
  if (templateCode === "functional_group_v1") return ""
  return templateCode === "recruitment_v1" ? "维度" : "客户"
}

export function usesConfiguredCustomers(templateCode: string): boolean {
  return ["delivery_specialist_v1", "delivery_assistant_v1"].includes(templateCode)
}
