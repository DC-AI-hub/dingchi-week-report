<script setup lang="ts">
import { formatDateTime } from "@/utils/date"

interface RiskDraft {
  risk_level: string
  risk_blocked: boolean
  risk_reason: string
  next_action: string
  support_needed: string
  expected_resolve_date: string | null
}

defineProps<{ modelValue: RiskDraft; readonly?: boolean }>()
</script>

<template>
  <div class="risk-panel">
    <div class="risk-levels" role="radiogroup" aria-label="风险等级">
      <label v-for="item in [{ value: 'none', label: '无风险' }, { value: 'low', label: '低风险' }, { value: 'medium', label: '中风险' }, { value: 'high', label: '高风险' } ]" :key="item.value" :class="{ 'risk-option': true, [`risk-option--${item.value}`]: true, 'is-active': modelValue.risk_level === item.value }">
        <input v-if="!readonly" v-model="modelValue.risk_level" type="radio" :value="item.value" />
        <span>{{ item.label }}</span>
      </label>
    </div>
    <div class="risk-form-grid">
      <label>风险 / 阻塞说明<textarea v-if="!readonly" v-model="modelValue.risk_reason" rows="3" placeholder="描述影响、原因与当前状态" /><span v-else>{{ modelValue.risk_reason || '暂无风险说明' }}</span></label>
      <label>下一步行动<textarea v-if="!readonly" v-model="modelValue.next_action" rows="3" placeholder="下一步怎么解决或推进" /><span v-else>{{ modelValue.next_action || '暂无行动说明' }}</span></label>
      <label>需要的支持<textarea v-if="!readonly" v-model="modelValue.support_needed" rows="3" placeholder="需要领导或协作方提供什么支持" /><span v-else>{{ modelValue.support_needed || '暂无支持需求' }}</span></label>
      <label>预计解决日期<input v-if="!readonly" v-model="modelValue.expected_resolve_date" type="date" /><span v-else>{{ formatDateTime(modelValue.expected_resolve_date) }}</span></label>
    </div>
    <label v-if="!readonly" class="blocked-check"><input v-model="modelValue.risk_blocked" type="checkbox" /> 当前存在阻塞，需要协同升级</label>
  </div>
</template>

<style scoped src="./RiskPanel.css"></style>
