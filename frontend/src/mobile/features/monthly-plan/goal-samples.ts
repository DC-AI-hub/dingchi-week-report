import { humanResourcesMonthlyPlanSampleFields } from "@/mobile/features/weekly-report/human-resources/samples"
import { deliveryMonthlyPlanSampleFields } from "@/mobile/features/weekly-report/delivery-specialist/samples"
import { deliveryAssistantMonthlyPlanSampleFields } from "@/mobile/features/weekly-report/delivery-assistant/samples"
import { recruitmentMonthlyPlanSampleFields } from "@/mobile/features/weekly-report/recruitment/samples"
import { itoSalesMonthlyPlanSampleFields } from "@/mobile/features/weekly-report/ito-sales/samples"
import { innovationSalesMonthlyPlanSampleFields } from "@/mobile/features/weekly-report/innovation-sales/samples"
import { functionalMonthlyPlanSampleFields } from "@/mobile/features/weekly-report/functional-group/samples"

type SampleField = { label: string; value?: string; rows?: readonly {label:string;value:string}[] }
// 沿用现有模板样例；当前样例仍由前端常量维护。
const samples: Record<string, readonly SampleField[]> = {
  human_resources_v1: humanResourcesMonthlyPlanSampleFields,
  delivery_specialist_v1: deliveryMonthlyPlanSampleFields,
  delivery_assistant_v1: deliveryAssistantMonthlyPlanSampleFields,
  recruitment_v1: recruitmentMonthlyPlanSampleFields,
  ito_sales_v1: itoSalesMonthlyPlanSampleFields,
  innovation_sales_v1: innovationSalesMonthlyPlanSampleFields,
  functional_group_v1: functionalMonthlyPlanSampleFields,
}

export function monthlyGoalSamples(templateCode: string) {
  return samples[templateCode] || []
}
