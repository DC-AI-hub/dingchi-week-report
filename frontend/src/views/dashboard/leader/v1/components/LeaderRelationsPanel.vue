<script setup lang="ts">
import { Link2, UsersRound } from "lucide-vue-next"

import type { LeaderRelation } from "../types"

const props = defineProps<{ relations: LeaderRelation[] }>()
</script>

<template>
  <article class="leader-relations-panel">
    <div class="leader-bottom-heading"><div class="leader-bottom-title"><span class="leader-bottom-icon leader-bottom-icon--green"><UsersRound :size="17" /></span><h2>协同关系</h2></div><Link2 :size="18" class="leader-relations-link" /></div>
    <div v-if="!props.relations.length" class="leader-bottom-empty">暂无协同记录</div>
    <div v-else class="leader-relation-list">
      <div v-for="relation in props.relations" :key="relation.id" class="leader-relation-item"><span class="leader-relation-avatar">{{ relation.name.slice(0, 1) }}</span><span class="leader-relation-name">{{ relation.name }}</span><span class="leader-relation-line" /><b>{{ relation.count }} 项协作</b></div>
    </div>
  </article>
</template>

<style scoped src="./LeaderRelationsPanel.css"></style>
