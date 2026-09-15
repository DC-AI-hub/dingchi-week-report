-- 鼎驰周报本地演示数据（MySQL 8+）
-- 使用方式：先执行本目录的 01_建表DDL.sql，或按项目迁移流程完成建表（二选一），再执行本文件。
-- mysql -uroot -p dingchi_week_report < "docs/数据库脚本/02_初始化DML.sql"
-- 所有 ID 为示例雪花格式的逻辑 ID；密码已使用当前 .keys/public_key.pem 的 RSA-OAEP-SHA256 加密。
-- 若重新生成 RSA 密钥，请重新生成本脚本中的 password_ciphertext。

SET NAMES utf8mb4;
START TRANSACTION;

-- 静态字典：角色数据范围和周报模板由字典表统一维护，页面通过字典接口下拉选择。
INSERT IGNORE INTO `system_dictionary`
    (id, dict_type, dict_code, dict_name, dict_value, description, status, sort_order, created_at, updated_at)
VALUES
    (100000000000000001, 'role_scope', 'self', '仅本人数据', 'self', '只能查看当前用户提交的周报数据。', 'active', 10, NOW(), NOW()),
    (100000000000000002, 'role_scope', 'team', '本人及下属团队', 'team', '可查看当前用户及其逻辑下属的周报数据。', 'active', 20, NOW(), NOW()),
    (100000000000000003, 'role_scope', 'all', '全部数据', 'all', '可查看系统内全部人员的周报数据。', 'active', 30, NOW(), NOW()),
    (100000000000000101, 'report_template', 'recruitment_specialist_v1', '招聘专员周总结计划', 'recruitment_specialist', '招聘专员使用的周报模板。', 'active', 10, NOW(), NOW()),
    (100000000000000102, 'report_template', 'delivery_specialist_v1', '交付专员周总结计划', 'delivery_specialist', '交付专员使用的周报模板。', 'active', 20, NOW(), NOW()),
    (100000000000000103, 'report_template', 'interaction_assistant_v1', '交互助理周总结计划', 'interaction_assistant', '交互助理使用的周报模板。', 'active', 30, NOW(), NOW()),
    (100000000000000104, 'report_template', 'recruitment_manager_v1', '招聘经理周总结计划', 'recruitment_manager', '招聘经理使用的周报模板。', 'active', 40, NOW(), NOW()),
    (100000000000000105, 'report_template', 'delivery_manager_v1', '交付经理周总结计划', 'delivery_manager', '交付经理使用的周报模板。', 'active', 50, NOW(), NOW()),
    (100000000000000106, 'report_template', 'president_v1', '总裁经营周报', 'president', '总裁使用的经营周报模板。', 'active', 60, NOW(), NOW()),
    (100000000000000107, 'report_template', 'system_admin_v1', '系统运营周报', 'system_admin', '系统管理员使用的运营周报模板。', 'active', 70, NOW(), NOW());

-- 周报任务列表字段：dict_type 按角色拆分；dict_value=1 表示默认展示，=0 表示可选但默认隐藏。
-- sort_order 与 Excel 表头顺序一致，序号列由页面固定展示，不在字典中配置。
INSERT IGNORE INTO `system_dictionary`
    (id, dict_type, dict_code, dict_name, dict_value, description, status, sort_order, created_at, updated_at)
VALUES
    (430000000000000001, 'weekly_report_fields_delivery_specialist', 'customer_name', '客户', '1', '任务所属客户。', 'active', 10, NOW(), NOW()),
    (430000000000000002, 'weekly_report_fields_delivery_specialist', 'task_name', '工作任务', '1', '任务名称。', 'active', 20, NOW(), NOW()),
    (430000000000000003, 'weekly_report_fields_delivery_specialist', 'work_content', '主要工作内容', '0', '任务主要工作内容。', 'active', 30, NOW(), NOW()),
    (430000000000000004, 'weekly_report_fields_delivery_specialist', 'output_description', '输出成果', '1', '任务输出成果。', 'active', 40, NOW(), NOW()),
    (430000000000000005, 'weekly_report_fields_delivery_specialist', 'planned_completion_date', '计划完成时间', '1', '任务计划完成日期。', 'active', 50, NOW(), NOW()),
    (430000000000000006, 'weekly_report_fields_delivery_specialist', 'progress_text', '工作进展（截至月日）', '0', '截至统计日期的工作进展。', 'active', 60, NOW(), NOW()),
    (430000000000000007, 'weekly_report_fields_delivery_specialist', 'progress_percent', '完成进度（百分比）', '1', '任务完成进度百分比。', 'active', 70, NOW(), NOW()),
    (430000000000000008, 'weekly_report_fields_delivery_specialist', 'delay_reason', '进度缓慢原因说明', '0', '进度缓慢或延期原因。', 'active', 80, NOW(), NOW()),
    (430000000000000009, 'weekly_report_fields_delivery_specialist', 'on_time_status', '是否在计划时间内完成', '1', '任务按计划完成状态。', 'active', 90, NOW(), NOW()),
    (430000000000000010, 'weekly_report_fields_delivery_specialist', 'actual_completion_date', '实际完成时间', '0', '任务实际完成日期。', 'active', 100, NOW(), NOW()),
    (430000000000000011, 'weekly_report_fields_delivery_specialist', 'owner_name', '责任人', '0', '任务责任人。', 'active', 110, NOW(), NOW()),
    (430000000000000012, 'weekly_report_fields_delivery_specialist', 'collaborator_names', '协作人', '0', '任务协作人。', 'active', 120, NOW(), NOW()),
    (430000000000000013, 'weekly_report_fields_delivery_specialist', 'document_links', '相关文档链接或佐证材料', '0', '任务相关文档链接或佐证材料。', 'active', 130, NOW(), NOW()),
    (430000000000000014, 'weekly_report_fields_interaction_assistant', 'customer_name', '客户', '1', '任务所属客户。', 'active', 10, NOW(), NOW()),
    (430000000000000015, 'weekly_report_fields_interaction_assistant', 'task_name', '工作任务', '1', '任务名称。', 'active', 20, NOW(), NOW()),
    (430000000000000016, 'weekly_report_fields_interaction_assistant', 'work_content', '主要工作内容', '0', '任务主要工作内容。', 'active', 30, NOW(), NOW()),
    (430000000000000017, 'weekly_report_fields_interaction_assistant', 'output_description', '输出成果', '1', '任务输出成果。', 'active', 40, NOW(), NOW()),
    (430000000000000018, 'weekly_report_fields_interaction_assistant', 'planned_completion_date', '计划完成时间', '1', '任务计划完成日期。', 'active', 50, NOW(), NOW()),
    (430000000000000019, 'weekly_report_fields_interaction_assistant', 'progress_text', '工作进展（截至月日）', '0', '截至统计日期的工作进展。', 'active', 60, NOW(), NOW()),
    (430000000000000020, 'weekly_report_fields_interaction_assistant', 'progress_percent', '完成进度（百分比）', '1', '任务完成进度百分比。', 'active', 70, NOW(), NOW()),
    (430000000000000021, 'weekly_report_fields_interaction_assistant', 'delay_reason', '进度缓慢原因说明', '0', '进度缓慢或延期原因。', 'active', 80, NOW(), NOW()),
    (430000000000000022, 'weekly_report_fields_interaction_assistant', 'on_time_status', '是否在计划时间内完成', '1', '任务按计划完成状态。', 'active', 90, NOW(), NOW()),
    (430000000000000023, 'weekly_report_fields_interaction_assistant', 'actual_completion_date', '实际完成时间', '0', '任务实际完成日期。', 'active', 100, NOW(), NOW()),
    (430000000000000024, 'weekly_report_fields_interaction_assistant', 'owner_name', '责任人', '0', '任务责任人。', 'active', 110, NOW(), NOW()),
    (430000000000000025, 'weekly_report_fields_interaction_assistant', 'collaborator_names', '协作人', '0', '任务协作人。', 'active', 120, NOW(), NOW()),
    (430000000000000026, 'weekly_report_fields_interaction_assistant', 'document_links', '相关文档链接或佐证材料', '0', '任务相关文档链接或佐证材料。', 'active', 130, NOW(), NOW());

INSERT IGNORE INTO `organization_group`
    (id, group_code, group_name, description, parent_group_id, status, created_at, updated_at)
VALUES
    (300000000000000001, 'sales', '销售中心', '销售与客户经营团队', NULL, 'active', NOW(), NOW()),
    (300000000000000002, 'delivery', '交付中心', '交付与招聘执行团队', NULL, 'active', NOW(), NOW()),
    (300000000000000003, 'platform', '平台支持', '系统与运营支持团队', NULL, 'active', NOW(), NOW());

INSERT IGNORE INTO `role`
    (id, role_code, role_name, scope, description, report_template_code, status, sort_order, created_at, updated_at)
VALUES
    (200000000000000001, 'recruitment_specialist', '招聘专员', 'self', '填写候选人漏斗和需求推进周报', 'recruitment_specialist_v1', 'active', 10, NOW(), NOW()),
    (200000000000000002, 'delivery_specialist', '交付专员', 'self', '填写客户交付、回款与风险周报', 'delivery_specialist_v1', 'active', 20, NOW(), NOW()),
    (200000000000000003, 'interaction_assistant', '交互助理', 'self', '填写人员构成、客情与薪酬周报', 'interaction_assistant_v1', 'active', 30, NOW(), NOW()),
    (200000000000000004, 'recruitment_manager', '招聘经理', 'team', '查看招聘团队周报', 'recruitment_manager_v1', 'active', 40, NOW(), NOW()),
    (200000000000000005, 'delivery_manager', '交付经理', 'team', '查看交付团队周报', 'delivery_manager_v1', 'active', 50, NOW(), NOW()),
    (200000000000000006, 'president', '总裁', 'all', '查看全公司周报和经营数据', 'president_v1', 'active', 60, NOW(), NOW()),
    (200000000000000007, 'system_admin', '系统管理员', 'all', '维护用户、角色、分组和系统运营周报', 'system_admin_v1', 'active', 70, NOW(), NOW());

-- 演示账号：登录密码分别为 Admin@123、President@123、Manager@123、Worker@123。
INSERT IGNORE INTO `user_account`
    (id, username, employee_no, display_name, email, password_ciphertext, manager_id, group_id,
     avatar_color, status, is_demo, last_login_at, created_at, updated_at)
VALUES
    (900000000000000001, 'admin', 'DC0001', '系统管理员', 'admin@dingchi.local',
     'rsa_oaep_sha256:VOm8hyoa64DStDcehzx2adLyNudHJqaalLRt0_USvEb7eN7fjm7WiFA1RT-px-lyd2JMWSwD8ajgIxIIiQK79geSkRzMEJQA68u1btZeZmVAcIAMKqr1hNRXggYsuADWb3J75UzOrT1WoOZKpWz0KRacYjILLNRorTpaxXIUE7CE8D5dK86rNx-7B7OeX-vzi_e6DeLUYUeovFwU3ASSwTuUfj6ElNCn5cYR6vBk1gP_8vV_B7iv9FMx8eLIgkYDDb28l0z-VyCK3dzwBnIzLBIHqYbOIqHlrVtZU_UQE9-s-vb0uO3npP85Vo0E9v-etamejF9vVzMOdbufd7-g0g==',
     NULL, 300000000000000003, '#315efb', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000002, 'president', 'DC0002', '周总', 'president@dingchi.local',
     'rsa_oaep_sha256:ewSUdcbK7eSy1Odqtdc44R29DyEHzq1bZebg0ldU4OJzj_qXYSK0L3ypByFeiYfRXnQOXTiY1_ZFKhkUR8UVDda8i8vbKb58_kZ0ZyvZxvgpuggVz0O1ustnSDhKO5oJWLB6eVzlRpYuRDA8YS4cK8O4RUwvuj6Snu8mn_FawcsiauQ8Y-t6qFyf5a4QRIl1bywU7ZiwzaWNQneYlwV8OqKK5ubvrVuHxYWJCC4m-Gkfy-JeVfZh3Rs4TDL_FKGSWywDoRQ4iDGFp6WOFnOIqn_QGqhaJU8l16ekA8EWfARZmXw7O9NS8Os11ksHFwWPU2HlueX1XJMjNwE_PKjIUA==',
     NULL, 300000000000000001, '#6c5ce7', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000003, 'delivery.manager', 'DC0003', '交付经理', 'delivery.manager@dingchi.local',
     'rsa_oaep_sha256:aV5xbplwJgNVcFUhPGF2q0kgVRaNN2HD1_ZYK-Cg6OHXugQqav7K0UsTNW8qLHcUpD1wOwdlbSEaXgEQ47q4ZHPeQfAufIfBtWUsitwWIy_nE-pXJUQt4pULaYhhgMq9pZkOQAe4S3lHUHD4guqBwMPqKOQ876bnhmGLeepU2TuenjeoU0kWMQ3RauZclv015nhHbxCdaavgMT8nx9MFvQMcJbRSYoYN1nkSDpy7epLYFDqL1lOtUYJhiLZk9-othg8ctaOPgTNbi8AVb1SV7Kv5CH8AhnrMXIWbcxVTiGFg7pRGjTnQrafUYRUZKxvgJ4U7oSF9JpZYikP1U1wNGw==',
     900000000000000002, 300000000000000002, '#168aad', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000004, 'recruitment.manager', 'DC0004', '招聘经理', 'recruitment.manager@dingchi.local',
     'rsa_oaep_sha256:aV5xbplwJgNVcFUhPGF2q0kgVRaNN2HD1_ZYK-Cg6OHXugQqav7K0UsTNW8qLHcUpD1wOwdlbSEaXgEQ47q4ZHPeQfAufIfBtWUsitwWIy_nE-pXJUQt4pULaYhhgMq9pZkOQAe4S3lHUHD4guqBwMPqKOQ876bnhmGLeepU2TuenjeoU0kWMQ3RauZclv015nhHbxCdaavgMT8nx9MFvQMcJbRSYoYN1nkSDpy7epLYFDqL1lOtUYJhiLZk9-othg8ctaOPgTNbi8AVb1SV7Kv5CH8AhnrMXIWbcxVTiGFg7pRGjTnQrafUYRUZKxvgJ4U7oSF9JpZYikP1U1wNGw==',
     900000000000000002, 300000000000000001, '#8b5cf6', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000005, 'recruiter', 'DC0005', '林晓', 'recruiter@dingchi.local',
     'rsa_oaep_sha256:YKWPYnaExHRunjh5uTRrJgMMsZJrufoALKI9VjgxOm_e8dcAzkQIr_fdyiKW29INbbl9PMireDFV0COjGpeGy_KtakSeB7m-hV_3cV3REk10M090_EiJzKhltzEyYMIQE1at99Awfe1nme4xJkbnqWfABbgBYUjapZpvuM8hAK9GzgKITDyx5KScMtsNLT9fnOvpntoiXta3jwKPS-4at2A9At8KrqMbW-ppnTG25eZqf_kW9p7UCNcirCA3FRYgWt0RxuI1S5JFTFGPIla7PZItgSX_jovsTbigMvkfL6reK1KruSQDCK_aTA61PtSSAU6qX1RTkC2LBC1a1ptbmw==',
     900000000000000004, 300000000000000001, '#14b8a6', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000006, 'delivery.specialist', 'DC0006', '陈默', 'delivery.specialist@dingchi.local',
     'rsa_oaep_sha256:YKWPYnaExHRunjh5uTRrJgMMsZJrufoALKI9VjgxOm_e8dcAzkQIr_fdyiKW29INbbl9PMireDFV0COjGpeGy_KtakSeB7m-hV_3cV3REk10M090_EiJzKhltzEyYMIQE1at99Awfe1nme4xJkbnqWfABbgBYUjapZpvuM8hAK9GzgKITDyx5KScMtsNLT9fnOvpntoiXta3jwKPS-4at2A9At8KrqMbW-ppnTG25eZqf_kW9p7UCNcirCA3FRYgWt0RxuI1S5JFTFGPIla7PZItgSX_jovsTbigMvkfL6reK1KruSQDCK_aTA61PtSSAU6qX1RTkC2LBC1a1ptbmw==',
     900000000000000003, 300000000000000002, '#0ea5e9', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000007, 'interaction.assistant', 'DC0007', '许宁', 'interaction.assistant@dingchi.local',
     'rsa_oaep_sha256:YKWPYnaExHRunjh5uTRrJgMMsZJrufoALKI9VjgxOm_e8dcAzkQIr_fdyiKW29INbbl9PMireDFV0COjGpeGy_KtakSeB7m-hV_3cV3REk10M090_EiJzKhltzEyYMIQE1at99Awfe1nme4xJkbnqWfABbgBYUjapZpvuM8hAK9GzgKITDyx5KScMtsNLT9fnOvpntoiXta3jwKPS-4at2A9At8KrqMbW-ppnTG25eZqf_kW9p7UCNcirCA3FRYgWt0RxuI1S5JFTFGPIla7PZItgSX_jovsTbigMvkfL6reK1KruSQDCK_aTA61PtSSAU6qX1RTkC2LBC1a1ptbmw==',
     900000000000000003, 300000000000000002, '#f59e0b', 'active', 1, NULL, NOW(), NOW());

INSERT IGNORE INTO `user_role` (id, user_id, role_id, is_default, status, created_at, updated_at) VALUES
    (910000000000000001, 900000000000000001, 200000000000000007, 1, 'active', NOW(), NOW()),
    (910000000000000002, 900000000000000002, 200000000000000006, 1, 'active', NOW(), NOW()),
    (910000000000000003, 900000000000000002, 200000000000000007, 0, 'active', NOW(), NOW()),
    (910000000000000004, 900000000000000003, 200000000000000005, 1, 'active', NOW(), NOW()),
    (910000000000000005, 900000000000000003, 200000000000000002, 0, 'active', NOW(), NOW()),
    (910000000000000006, 900000000000000004, 200000000000000004, 1, 'active', NOW(), NOW()),
    (910000000000000007, 900000000000000005, 200000000000000001, 1, 'active', NOW(), NOW()),
    (910000000000000008, 900000000000000006, 200000000000000002, 1, 'active', NOW(), NOW()),
    (910000000000000009, 900000000000000007, 200000000000000003, 1, 'active', NOW(), NOW());

INSERT IGNORE INTO `user_group_membership` (id, user_id, group_id, is_primary, status, created_at, updated_at) VALUES
    (920000000000000001, 900000000000000001, 300000000000000003, 1, 'active', NOW(), NOW()),
    (920000000000000002, 900000000000000002, 300000000000000001, 1, 'active', NOW(), NOW()),
    (920000000000000003, 900000000000000003, 300000000000000002, 1, 'active', NOW(), NOW()),
    (920000000000000004, 900000000000000004, 300000000000000001, 1, 'active', NOW(), NOW()),
    (920000000000000005, 900000000000000005, 300000000000000001, 1, 'active', NOW(), NOW()),
    (920000000000000006, 900000000000000006, 300000000000000002, 1, 'active', NOW(), NOW()),
    (920000000000000007, 900000000000000007, 300000000000000002, 1, 'active', NOW(), NOW());

-- 每个角色一份模板头；模板项采用同一套任务/指标结构，页面按配置渲染。
INSERT IGNORE INTO `report_template`
    (id, template_code, template_version, role_code, template_name, description,
     status, effective_from, effective_to, created_at, updated_at)
VALUES
    (400000000000000001, 'recruitment_specialist_v1', '1.0', 'recruitment_specialist', '招聘专员周总结计划', '围绕候选人漏斗、需求响应和入职结果填写周报', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000002, 'delivery_specialist_v1', '1.0', 'delivery_specialist', '交付专员周总结计划', '围绕客户交付、招聘转化、成本和回款填写周报', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000003, 'interaction_assistant_v1', '1.0', 'interaction_assistant', '交互助理周总结计划', '围绕人员构成、沟通维护、薪酬与客户关系填写周报', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000004, 'recruitment_manager_v1', '1.0', 'recruitment_manager', '招聘经理周总结计划', '汇总招聘团队目标、产能、风险与下周行动', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000005, 'delivery_manager_v1', '1.0', 'delivery_manager', '交付经理周总结计划', '汇总交付团队、客户经营、回款和风险', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000006, 'president_v1', '1.0', 'president', '总裁经营周报', '从全局视角填写经营重点、关键决策和组织风险', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000007, 'system_admin_v1', '1.0', 'system_admin', '系统运营周报', '填写系统运行、数据质量和运营支持事项', 'active', '2026-01-01', NULL, NOW(), NOW());

INSERT IGNORE INTO `report_template_item`
    (id, template_id, section_code, section_name, task_code, label, guidance, item_type, scope_type, value_type, unit, required, validation_rule, sort_order, config_json, created_at, updated_at)
VALUES
    (410000000000000001, 400000000000000001, 'customer', '客户需求', 'candidate_follow_up', '重点候选人跟进', '记录候选人推进、阻塞和下一步。', 'task', 'customer', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000002, 400000000000000001, 'funnel', '招聘漏斗', 'pipeline_cleanup', '招聘漏斗清理', '更新候选人阶段和预计入职时间。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000003, 400000000000000001, 'funnel', '招聘漏斗', 'resume_recommendations', '简历推荐', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '份', 0, '', 3, '{}', NOW(), NOW()),
    (410000000000000004, 400000000000000001, 'funnel', '招聘漏斗', 'interviews', '到面人数', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 4, '{}', NOW(), NOW()),
    (410000000000000005, 400000000000000001, 'funnel', '招聘漏斗', 'onboarded', '有效入职', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 5, '{}', NOW(), NOW()),
    (410000000000000006, 400000000000000002, 'customer', '客户需求和招聘转化', 'customer_progress', '重点客户交付进展', '按客户记录需求、入职与交付成果。', 'task', 'customer', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000007, 400000000000000002, 'risk', '风险控制', 'risk_resolution', '延期/风险项处理', '必须填写原因、下一步和预计完成日期。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000008, 400000000000000002, 'overall', '总体目标', 'net_headcount', '净增人数', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 3, '{}', NOW(), NOW()),
    (410000000000000009, 400000000000000002, 'overall', '总体目标', 'collection_amount', '回款金额', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'amount', '万元', 0, '', 4, '{}', NOW(), NOW()),
    (410000000000000010, 400000000000000003, 'people', '客户人员构成', 'headcount_review', '人员构成复核', '同步存量、增量和试用期人员。', 'task', 'overall', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000011, 400000000000000003, 'risk', '流失与风险', 'attrition_replacement', '流失与替补管控', '记录释放、替补和空岗人日。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000012, 400000000000000003, 'people', '客户人员构成', 'total_headcount', '当月总人数', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 3, '{}', NOW(), NOW()),
    (410000000000000013, 400000000000000003, 'risk', '流失与风险', 'attrition_count', '流失人数', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 4, '{}', NOW(), NOW()),
    (410000000000000014, 400000000000000004, 'team', '团队目标', 'team_review', '团队周度复盘', '汇总下属招聘专员的完成情况。', 'task', 'overall', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000015, 400000000000000004, 'risk', '风险与支持', 'support_request', '资源与风险协调', '记录需要跨团队决策的事项。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000016, 400000000000000004, 'team', '团队目标', 'team_onboarded', '团队有效入职', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 3, '{}', NOW(), NOW()),
    (410000000000000017, 400000000000000005, 'team', '交付团队', 'team_review', '交付团队复盘', '汇总交付专员与交互助理工作。', 'task', 'overall', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000018, 400000000000000005, 'customer', '客户经营', 'customer_review', '重点客户经营', '记录合同、续签、回款及客情。', 'task', 'customer', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000019, 400000000000000005, 'team', '交付团队', 'team_completion_rate', '团队完成率', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'percent', '%', 0, '0-100', 3, '{}', NOW(), NOW()),
    (410000000000000020, 400000000000000006, 'business', '经营概览', 'business_review', '经营重点复盘', '填写跨部门关键进展与结果。', 'task', 'overall', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000021, 400000000000000006, 'decision', '关键决策', 'decision_items', '关键决策事项', '填写需要管理层拍板的事项。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000022, 400000000000000006, 'business', '经营概览', 'overall_completion_rate', '整体完成率', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'percent', '%', 0, '0-100', 3, '{}', NOW(), NOW()),
    (410000000000000023, 400000000000000007, 'operation', '系统运营', 'service_operation', '系统运行维护', '记录发布、告警和问题闭环。', 'task', 'overall', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000024, 400000000000000007, 'data', '数据质量', 'data_quality', '数据质量巡检', '记录用户、角色和周报数据检查。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000025, 400000000000000007, 'operation', '系统运营', 'service_availability', '服务可用率', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'percent', '%', 0, '0-100', 3, '{}', NOW(), NOW());

-- 交付专员 2026-09 月度共用计划。
INSERT IGNORE INTO `monthly_plan`
    (id, role_code, employee_id, group_id, month_key, summary, created_at, updated_at)
VALUES
    (540000000000000001, 'delivery_specialist', 900000000000000006, 300000000000000002,
     '2026-09', '围绕重点客户需求、入职、流失、成本、合同和回款推进月度交付目标。', NOW(), NOW());

-- 当前周演示周报：经理可看到下属，系统管理员/总裁可看到全部。
INSERT IGNORE INTO `weekly_report`
    (id, role_code, template_code, template_version, employee_id, group_id, period_type, month_key,
     period_start, period_end, as_of_date, status, summary, risk_level, risk_blocked, risk_reason,
     next_action, support_needed, expected_resolve_date, created_at, updated_at)
VALUES
    (500000000000000001, 'delivery_specialist', 'delivery_specialist_v1', '1.0', 900000000000000006, 300000000000000002, 'week', '2026-09', '2026-09-07', '2026-09-13', '2026-09-10', 'archived', '完成重点客户需求梳理与简历推荐，合同续签待客户确认。', 'medium', 0, '合同审批节点等待客户反馈。', '周四再次沟通并准备备选报价方案。', '需要交付经理协调商务支持。', '2026-09-11', NOW(), NOW()),
    (500000000000000002, 'interaction_assistant', 'interaction_assistant_v1', '1.0', 900000000000000007, 300000000000000002, 'week', '2026-09', '2026-09-07', '2026-09-13', '2026-09-10', 'archived', '完成客户人员构成盘点和客情拜访，风险人员已建立跟进台账。', 'none', 0, '', '持续跟进高风险人员并同步交付经理。', '', NULL, NOW(), NOW()),
    (500000000000000003, 'recruitment_specialist', 'recruitment_specialist_v1', '1.0', 900000000000000005, 300000000000000001, 'week', '2026-09', '2026-09-07', '2026-09-13', '2026-09-10', 'archived', '本周集中推进中证信息和方正证券候选人。', 'low', 0, '', '完成两名候选人的二面安排。', '', NULL, NOW(), NOW()),
    (500000000000000004, 'delivery_manager', 'delivery_manager_v1', '1.0', 900000000000000003, 300000000000000002, 'week', '2026-09', '2026-09-07', '2026-09-13', '2026-09-10', 'archived', '交付团队整体完成率 83%，重点关注合同续签与回款。', 'medium', 1, '一项合同续签已超过计划日期。', '周五前完成管理层评审并推动客户确认。', '需要总裁关注重点客户决策。', '2026-09-12', NOW(), NOW());

INSERT IGNORE INTO `weekly_report_item`
    (id, report_id, scope_type, customer_id, customer_name_snapshot, section_code, task_code, task_name_snapshot,
     guidance_snapshot, work_content, output_description, planned_completion_date, progress_text, progress_percent, quality_percent,
     completion_rate, on_time_status, actual_completion_date, delay_reason, next_action, expected_completion_date,
     owner_id, owner_name_snapshot, collaborator_names, document_links, item_status, sort_order, created_at, updated_at)
VALUES
    (510000000000000001, 500000000000000001, 'customer', NULL, '中证信息', 'customer', 'customer_progress', '重点客户交付进展', '按客户记录需求、入职与交付成果。', '澄清客户岗位需求并组织候选人推荐。', '完成需求清单与候选人推荐', '2026-09-11', '完成需求澄清、推荐 8 份简历。', 80, 90, 85, 'in_progress', NULL, '', '安排客户面试并确认入职名单。', '2026-09-11', 900000000000000006, '陈默', '招聘专员', 'https://example.local/evidence/customer-demand', 'pending', 1, NOW(), NOW()),
    (510000000000000002, 500000000000000001, 'customer', NULL, '方正证券', 'risk', 'risk_resolution', '延期/风险项处理', '必须填写原因、下一步和预计完成日期。', '跟进客户法务与采购审批节点。', '合同续签方案', '2026-09-09', '客户法务反馈晚于计划。', 60, 85, 72.5, 'overdue', NULL, '法务评审排期延后。', '周四再次沟通并提交备选报价。', '2026-09-11', 900000000000000006, '陈默', '交付经理', 'https://example.local/evidence/renewal', 'pending', 2, NOW(), NOW()),
    (510000000000000003, 500000000000000002, 'overall', NULL, '', 'people', 'headcount_review', '人员构成复核', '同步存量、增量和试用期人员。', '', '客户人员台账', '2026-09-10', '完成 3 个客户人员台账复核。', 100, 90, 95, 'on_time', '2026-09-10', '', '', NULL, 900000000000000007, '许宁', '', '', 'completed', 1, NOW(), NOW()),
    (510000000000000004, 500000000000000002, 'overall', NULL, '', 'risk', 'attrition_replacement', '流失与替补管控', '记录释放、替补和空岗人日。', '', '高风险人员跟进表', '2026-09-12', '已建立跟进台账，待完成一次复盘。', 70, 90, 80, 'in_progress', NULL, '', '周五前完成复盘。', '2026-09-12', 900000000000000007, '许宁', '', '', 'pending', 2, NOW(), NOW()),
    (510000000000000005, 500000000000000003, 'overall', NULL, '', 'customer', 'candidate_follow_up', '重点候选人跟进', '记录候选人推进、阻塞和下一步。', '', '候选人进展表', '2026-09-12', '已完成初筛和一面安排。', 50, 80, 65, 'in_progress', NULL, '', '完成两名候选人的二面安排。', '2026-09-12', 900000000000000005, '林晓', '', '', 'pending', 1, NOW(), NOW()),
    (510000000000000006, 500000000000000004, 'overall', NULL, '', 'team', 'team_review', '交付团队复盘', '汇总交付专员与交互助理工作。', '', '团队复盘纪要', '2026-09-09', '团队完成率 83%，已识别一项续签风险。', 80, 90, 85, 'overdue', NULL, '合同续签超过原计划日期。', '周五前完成管理层评审。', '2026-09-12', 900000000000000003, '交付经理', '', '', 'pending', 1, NOW(), NOW()),
    (510000000000000007, 500000000000000004, 'customer', NULL, '中证信息', 'customer', 'customer_review', '重点客户经营', '记录合同、续签、回款及客情。', '', '续签与回款清单', '2026-09-13', '已完成客户沟通，等待最终确认。', 75, 90, 82.5, 'in_progress', NULL, '', '准备管理层决策材料。', '2026-09-12', 900000000000000003, '交付经理', '', '', 'pending', 2, NOW(), NOW());

INSERT IGNORE INTO `weekly_report_metric`
    (id, report_id, item_id, metric_code, metric_name_snapshot, value_type, target_value_decimal, actual_value_decimal,
     value_text, unit, `precision`, baseline_value_decimal, note, created_at, updated_at)
VALUES
    (520000000000000001, 500000000000000001, NULL, 'net_headcount', '净增人数', 'number', 10, 8, '', '人', 0, 5, '来自本周客户需求清单', NOW(), NOW()),
    (520000000000000002, 500000000000000001, NULL, 'collection_amount', '回款金额', 'amount', 30, 24.5, '', '万元', 2, 18, '', NOW(), NOW()),
    (520000000000000003, 500000000000000002, NULL, 'total_headcount', '当月总人数', 'number', 42, 40, '', '人', 0, 38, '', NOW(), NOW()),
    (520000000000000004, 500000000000000002, NULL, 'customer_visits', '客情拜访数', 'number', 3, 3, '', '次', 0, 2, '', NOW(), NOW()),
    (520000000000000005, 500000000000000003, NULL, 'resume_recommendations', '简历推荐', 'number', 12, 8, '', '份', 0, 5, '', NOW(), NOW()),
    (520000000000000006, 500000000000000003, NULL, 'interviews', '到面人数', 'number', 6, 4, '', '人', 0, 3, '', NOW(), NOW()),
    (520000000000000007, 500000000000000004, NULL, 'team_completion_rate', '团队完成率', 'percent', 90, 83, '', '%', 0, 78, '', NOW(), NOW());

INSERT IGNORE INTO `weekly_report_evidence`
    (id, report_id, item_id, evidence_type, file_url, file_name, description, created_at)
VALUES
    (530000000000000001, 500000000000000001, 510000000000000001, 'link', 'https://example.local/evidence/customer-demand', '客户需求清单', '演示用佐证链接', NOW()),
    (530000000000000002, 500000000000000002, 510000000000000003, 'link', 'https://example.local/evidence/headcount', '人员台账', '演示用人员构成台账', NOW());

COMMIT;
