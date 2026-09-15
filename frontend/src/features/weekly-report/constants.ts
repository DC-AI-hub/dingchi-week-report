export const REPORT_ROLE_NAMES: Record<string, string> = {
  recruitment_specialist: "招聘专员",
  delivery_specialist: "交付专员",
  interaction_assistant: "交互助理",
  recruitment_manager: "招聘经理",
  delivery_manager: "交付经理",
  president: "总裁",
  system_admin: "系统管理员",
}

export function getReportRoleName(roleCode: string, roleName?: string | null): string {
  return roleName || REPORT_ROLE_NAMES[roleCode] || roleCode
}
