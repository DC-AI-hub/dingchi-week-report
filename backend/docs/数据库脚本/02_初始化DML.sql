-- 鼎驰周报本地演示数据（MySQL 8+）
-- 使用方式：先执行本目录的 01_建表DDL.sql，或按项目迁移流程完成建表（二选一），再执行本文件。
-- mysql -uroot -p dingchi_week_report < "docs/数据库脚本/02_初始化DML.sql"
-- 所有 ID 为示例雪花格式的逻辑 ID；密码已使用当前 .keys/public_key.pem 的 RSA-OAEP-SHA256 加密。
-- 若重新生成 RSA 密钥，请重新生成本脚本中的 password_ciphertext。

SET NAMES utf8mb4;
START TRANSACTION;

-- 重置系统配置种子：清空本脚本维护的配置表，再重新插入配置数据。
-- 本脚本不初始化也不清理周报、月度计划和附件等业务数据，避免误删用户已填写内容。
-- 本脚本用于本地/测试环境初始化，生产环境请按变更流程执行。
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE `report_template_item`;
TRUNCATE TABLE `report_template`;
TRUNCATE TABLE `user_group_membership`;
TRUNCATE TABLE `user_role`;
TRUNCATE TABLE `user_account`;
TRUNCATE TABLE `role`;
TRUNCATE TABLE `organization_group`;
TRUNCATE TABLE `system_dictionary`;
SET FOREIGN_KEY_CHECKS = 1;

-- 静态字典：角色数据范围和周报模板由字典表统一维护，页面通过字典接口下拉选择。
INSERT INTO `system_dictionary`
    (id, dict_type, dict_code, dict_name, dict_value, description, status, sort_order, created_at, updated_at)
VALUES
    (100000000000000001, 'role_scope', 'self', '仅本人数据', 'self', '只能查看当前用户提交的周报数据。', 'active', 10, NOW(), NOW()),
    (100000000000000002, 'role_scope', 'team', '本人及下属团队', 'team', '可查看当前用户及其逻辑下属的周报数据。', 'active', 20, NOW(), NOW()),
    (100000000000000003, 'role_scope', 'all', '全部数据', 'all', '可查看系统内全部人员的周报数据。', 'active', 30, NOW(), NOW()),
    (100000000000000101, 'report_template', 'recruitment_v1', '招聘周报', 'recruitment', '招聘专员和招聘经理共用的周报模板。', 'active', 10, NOW(), NOW()),
    (100000000000000102, 'report_template', 'delivery_specialist_v1', '交付专员周报', 'delivery_specialist', '交付专员使用的周报模板。', 'active', 20, NOW(), NOW()),
    (100000000000000103, 'report_template', 'delivery_assistant_v1', '交付助理周报', 'delivery_assistant', '交付助理使用的周报模板。', 'active', 30, NOW(), NOW()),
    (100000000000000105, 'report_template', 'delivery_manager_v1', '交付经理周报', 'delivery_manager', '交付经理使用的周报模板。', 'active', 50, NOW(), NOW()),
    (100000000000000106, 'report_template', 'president_v1', '总裁经营周报', 'president', '总裁使用的经营周报模板。', 'active', 60, NOW(), NOW()),
    (100000000000000107, 'report_template', 'system_admin_v1', '系统运营周报', 'system_admin', '系统管理员使用的运营周报模板。', 'active', 70, NOW(), NOW()),
    (100000000000000108, 'report_template', 'ito_sales_v1', 'ITO销售周报', 'ito_sales', 'ITO销售使用的客户拓展、商机推进和回款周报模板。', 'active', 80, NOW(), NOW()),
    (100000000000000109, 'report_template', 'innovation_sales_v1', '创新业务销售周报', 'innovation_sales', '创新业务销售使用的业务机会、方案与签约周报模板。', 'active', 90, NOW(), NOW());

-- 周报任务列表字段：dict_type 按模板版本拆分；dict_value=1 表示默认展示，=0 表示可选但默认隐藏。
-- sort_order 与 Excel 表头顺序一致，序号列由页面固定展示，不在字典中配置。
INSERT INTO `system_dictionary`
    (id, dict_type, dict_code, dict_name, dict_value, description, status, sort_order, created_at, updated_at)
VALUES
    (430000000000000001, 'weekly_report_fields_delivery_specialist_v1', 'customer_name', '客户', '1', '任务所属客户。', 'active', 10, NOW(), NOW()),
    (430000000000000002, 'weekly_report_fields_delivery_specialist_v1', 'task_name', '工作任务', '1', '任务名称。', 'active', 20, NOW(), NOW()),
    (430000000000000003, 'weekly_report_fields_delivery_specialist_v1', 'work_content', '主要工作内容', '0', '任务主要工作内容。', 'active', 30, NOW(), NOW()),
    (430000000000000004, 'weekly_report_fields_delivery_specialist_v1', 'output_description', '输出成果', '1', '任务输出成果。', 'active', 40, NOW(), NOW()),
    (430000000000000005, 'weekly_report_fields_delivery_specialist_v1', 'planned_completion_date', '计划完成时间', '1', '任务计划完成日期。', 'active', 50, NOW(), NOW()),
    (430000000000000006, 'weekly_report_fields_delivery_specialist_v1', 'progress_text', '工作进展（截至月日）', '0', '截至统计日期的工作进展。', 'active', 60, NOW(), NOW()),
    (430000000000000007, 'weekly_report_fields_delivery_specialist_v1', 'progress_percent', '完成进度（百分比）', '1', '任务完成进度百分比。', 'active', 70, NOW(), NOW()),
    (430000000000000008, 'weekly_report_fields_delivery_specialist_v1', 'delay_reason', '进度缓慢原因说明', '0', '进度缓慢或延期原因。', 'active', 80, NOW(), NOW()),
    (430000000000000009, 'weekly_report_fields_delivery_specialist_v1', 'on_time_status', '是否在计划时间内完成', '1', '任务按计划完成状态。', 'active', 90, NOW(), NOW()),
    (430000000000000010, 'weekly_report_fields_delivery_specialist_v1', 'actual_completion_date', '实际完成时间', '0', '任务实际完成日期。', 'active', 100, NOW(), NOW()),
    (430000000000000011, 'weekly_report_fields_delivery_specialist_v1', 'owner_name', '责任人', '0', '任务责任人。', 'active', 110, NOW(), NOW()),
    (430000000000000012, 'weekly_report_fields_delivery_specialist_v1', 'collaborator_names', '协作人', '0', '任务协作人。', 'active', 120, NOW(), NOW()),
    (430000000000000013, 'weekly_report_fields_delivery_specialist_v1', 'document_links', '相关文档链接或佐证材料', '0', '任务相关文档链接或佐证材料。', 'active', 130, NOW(), NOW()),
    (430000000000000014, 'weekly_report_fields_delivery_assistant_v1', 'customer_name', '客户', '1', '任务所属客户。', 'active', 10, NOW(), NOW()),
    (430000000000000015, 'weekly_report_fields_delivery_assistant_v1', 'task_name', '工作任务', '1', '任务名称。', 'active', 20, NOW(), NOW()),
    (430000000000000016, 'weekly_report_fields_delivery_assistant_v1', 'work_content', '主要工作内容', '0', '任务主要工作内容。', 'active', 30, NOW(), NOW()),
    (430000000000000017, 'weekly_report_fields_delivery_assistant_v1', 'output_description', '输出成果', '1', '任务输出成果。', 'active', 40, NOW(), NOW()),
    (430000000000000018, 'weekly_report_fields_delivery_assistant_v1', 'planned_completion_date', '计划完成时间', '1', '任务计划完成日期。', 'active', 50, NOW(), NOW()),
    (430000000000000019, 'weekly_report_fields_delivery_assistant_v1', 'progress_text', '工作进展（截至月日）', '0', '截至统计日期的工作进展。', 'active', 60, NOW(), NOW()),
    (430000000000000020, 'weekly_report_fields_delivery_assistant_v1', 'progress_percent', '完成进度（百分比）', '1', '任务完成进度百分比。', 'active', 70, NOW(), NOW()),
    (430000000000000027, 'weekly_report_fields_delivery_assistant_v1', 'quality_percent', '完成质量（百分比）', '1', '任务完成质量百分比。', 'active', 80, NOW(), NOW()),
    (430000000000000028, 'weekly_report_fields_delivery_assistant_v1', 'completion_rate', '月度工作完成率（完成进度*50%+完成质量*50%）', '1', '根据完成进度和完成质量自动计算。', 'active', 90, NOW(), NOW()),
    (430000000000000021, 'weekly_report_fields_delivery_assistant_v1', 'delay_reason', '进度缓慢原因说明', '0', '进度缓慢或延期原因。', 'active', 100, NOW(), NOW()),
    (430000000000000022, 'weekly_report_fields_delivery_assistant_v1', 'on_time_status', '是否在计划时间内完成', '1', '任务按计划完成状态。', 'active', 110, NOW(), NOW()),
    (430000000000000023, 'weekly_report_fields_delivery_assistant_v1', 'actual_completion_date', '实际完成时间', '0', '任务实际完成日期。', 'active', 120, NOW(), NOW()),
    (430000000000000024, 'weekly_report_fields_delivery_assistant_v1', 'owner_name', '责任人', '0', '任务责任人。', 'active', 130, NOW(), NOW()),
    (430000000000000025, 'weekly_report_fields_delivery_assistant_v1', 'collaborator_names', '协作人', '0', '任务协作人。', 'active', 140, NOW(), NOW()),
    (430000000000000026, 'weekly_report_fields_delivery_assistant_v1', 'document_links', '相关文档链接或佐证材料', '0', '任务相关文档链接或佐证材料。', 'active', 150, NOW(), NOW()),
    (430000000000000029, 'weekly_report_fields_recruitment_v1', 'dimension', '维度', '1', '招聘任务所属维度。', 'active', 10, NOW(), NOW()),
    (430000000000000030, 'weekly_report_fields_recruitment_v1', 'task_name', '工作任务', '1', '招聘工作任务名称。', 'active', 20, NOW(), NOW()),
    (430000000000000031, 'weekly_report_fields_recruitment_v1', 'work_content', '主要工作内容', '0', '招聘任务主要工作内容。', 'active', 30, NOW(), NOW()),
    (430000000000000032, 'weekly_report_fields_recruitment_v1', 'output_description', '输出成果', '1', '招聘任务输出成果。', 'active', 40, NOW(), NOW()),
    (430000000000000033, 'weekly_report_fields_recruitment_v1', 'planned_completion_date', '计划完成时间', '1', '招聘任务计划完成日期。', 'active', 50, NOW(), NOW()),
    (430000000000000034, 'weekly_report_fields_recruitment_v1', 'progress_text', '工作进展（截至月日）', '0', '截至统计日期的招聘工作进展。', 'active', 60, NOW(), NOW()),
    (430000000000000035, 'weekly_report_fields_recruitment_v1', 'progress_percent', '完成进度（百分比）', '1', '招聘任务完成进度百分比。', 'active', 70, NOW(), NOW()),
    (430000000000000036, 'weekly_report_fields_recruitment_v1', 'quality_percent', '完成质量（百分比）', '1', '招聘任务完成质量百分比。', 'active', 80, NOW(), NOW()),
    (430000000000000037, 'weekly_report_fields_recruitment_v1', 'completion_rate', '月度工作完成率（完成进度*50%+完成质量*50%）', '1', '根据完成进度和完成质量自动计算。', 'active', 90, NOW(), NOW()),
    (430000000000000038, 'weekly_report_fields_recruitment_v1', 'delay_reason', '进度缓慢原因说明', '0', '招聘任务进度缓慢或延期原因。', 'active', 100, NOW(), NOW()),
    (430000000000000039, 'weekly_report_fields_recruitment_v1', 'on_time_status', '是否在计划时间内完成', '1', '招聘任务按计划完成状态。', 'active', 110, NOW(), NOW()),
    (430000000000000040, 'weekly_report_fields_recruitment_v1', 'actual_completion_date', '实际完成时间', '0', '招聘任务实际完成日期。', 'active', 120, NOW(), NOW()),
    (430000000000000041, 'weekly_report_fields_recruitment_v1', 'owner_name', '责任人', '0', '招聘任务责任人。', 'active', 130, NOW(), NOW()),
    (430000000000000042, 'weekly_report_fields_recruitment_v1', 'collaborator_names', '协作人', '0', '招聘任务协作人。', 'active', 140, NOW(), NOW()),
    (430000000000000043, 'weekly_report_fields_recruitment_v1', 'document_links', '相关文档链接或佐证材料', '0', '招聘任务相关文档链接或佐证材料。', 'active', 150, NOW(), NOW()),
    (430000000000000044, 'weekly_report_fields_ito_sales_v1', 'customer_name', '客户', '1', '任务所属客户。', 'active', 10, NOW(), NOW()),
    (430000000000000045, 'weekly_report_fields_ito_sales_v1', 'task_name', '工作任务', '1', '销售工作任务名称。', 'active', 20, NOW(), NOW()),
    (430000000000000046, 'weekly_report_fields_ito_sales_v1', 'work_content', '主要工作指引', '0', '任务主要工作指引。', 'active', 30, NOW(), NOW()),
    (430000000000000047, 'weekly_report_fields_ito_sales_v1', 'output_description', '输出成果', '1', '任务输出成果。', 'active', 40, NOW(), NOW()),
    (430000000000000048, 'weekly_report_fields_ito_sales_v1', 'planned_completion_date', '计划完成时间', '1', '任务计划完成日期。', 'active', 50, NOW(), NOW()),
    (430000000000000049, 'weekly_report_fields_ito_sales_v1', 'progress_text', '工作进展（截至月日）', '0', '截至统计日期的销售工作进展。', 'active', 60, NOW(), NOW()),
    (430000000000000050, 'weekly_report_fields_ito_sales_v1', 'progress_percent', '完成进度（百分比）', '1', '任务完成进度百分比。', 'active', 70, NOW(), NOW()),
    (430000000000000051, 'weekly_report_fields_ito_sales_v1', 'quality_percent', '完成质量（百分比）', '1', '任务完成质量百分比。', 'active', 80, NOW(), NOW()),
    (430000000000000052, 'weekly_report_fields_ito_sales_v1', 'completion_rate', '月度工作完成率（完成进度*50%+完成质量*50%）', '1', '根据完成进度和完成质量自动计算。', 'active', 90, NOW(), NOW()),
    (430000000000000053, 'weekly_report_fields_ito_sales_v1', 'delay_reason', '进度缓慢原因说明', '0', '任务进度缓慢或延期原因。', 'active', 100, NOW(), NOW()),
    (430000000000000054, 'weekly_report_fields_ito_sales_v1', 'on_time_status', '是否在计划时间内完成', '1', '任务按计划完成状态。', 'active', 110, NOW(), NOW()),
    (430000000000000055, 'weekly_report_fields_ito_sales_v1', 'actual_completion_date', '实际完成时间', '0', '任务实际完成日期。', 'active', 120, NOW(), NOW()),
    (430000000000000056, 'weekly_report_fields_ito_sales_v1', 'owner_name', '责任人', '0', '任务责任人。', 'active', 130, NOW(), NOW()),
    (430000000000000057, 'weekly_report_fields_ito_sales_v1', 'collaborator_names', '协作人', '0', '任务协作人。', 'active', 140, NOW(), NOW()),
    (430000000000000058, 'weekly_report_fields_ito_sales_v1', 'document_links', '相关文档链接或佐证材料', '0', '任务相关文档链接或佐证材料。', 'active', 150, NOW(), NOW()),
    (430000000000000059, 'weekly_report_fields_innovation_sales_v1', 'customer_name', '客户', '1', '任务所属客户。', 'active', 10, NOW(), NOW()),
    (430000000000000060, 'weekly_report_fields_innovation_sales_v1', 'task_name', '工作任务', '1', '创新业务销售任务名称。', 'active', 20, NOW(), NOW()),
    (430000000000000061, 'weekly_report_fields_innovation_sales_v1', 'work_content', '主要工作内容', '0', '创新业务任务主要工作内容。', 'active', 30, NOW(), NOW()),
    (430000000000000062, 'weekly_report_fields_innovation_sales_v1', 'output_description', '输出成果', '1', '任务输出成果。', 'active', 40, NOW(), NOW()),
    (430000000000000063, 'weekly_report_fields_innovation_sales_v1', 'planned_completion_date', '计划完成时间', '1', '任务计划完成日期。', 'active', 50, NOW(), NOW()),
    (430000000000000064, 'weekly_report_fields_innovation_sales_v1', 'progress_text', '工作进展（截至月日）', '0', '截至统计日期的创新业务销售工作进展。', 'active', 60, NOW(), NOW()),
    (430000000000000065, 'weekly_report_fields_innovation_sales_v1', 'progress_percent', '完成进度（百分比）', '1', '任务完成进度百分比。', 'active', 70, NOW(), NOW()),
    (430000000000000066, 'weekly_report_fields_innovation_sales_v1', 'quality_percent', '完成质量（百分比）', '1', '任务完成质量百分比。', 'active', 80, NOW(), NOW()),
    (430000000000000067, 'weekly_report_fields_innovation_sales_v1', 'completion_rate', '月度工作完成率（完成进度*50%+完成质量*50%）', '1', '根据完成进度和完成质量自动计算。', 'active', 90, NOW(), NOW()),
    (430000000000000068, 'weekly_report_fields_innovation_sales_v1', 'delay_reason', '进度缓慢原因说明', '0', '任务进度缓慢或延期原因。', 'active', 100, NOW(), NOW()),
    (430000000000000069, 'weekly_report_fields_innovation_sales_v1', 'on_time_status', '是否在计划时间内完成', '1', '任务按计划完成状态。', 'active', 110, NOW(), NOW()),
    (430000000000000070, 'weekly_report_fields_innovation_sales_v1', 'actual_completion_date', '实际完成时间', '0', '任务实际完成日期。', 'active', 120, NOW(), NOW()),
    (430000000000000071, 'weekly_report_fields_innovation_sales_v1', 'owner_name', '责任人', '0', '任务责任人。', 'active', 130, NOW(), NOW()),
    (430000000000000072, 'weekly_report_fields_innovation_sales_v1', 'collaborator_names', '协作人', '0', '任务协作人。', 'active', 140, NOW(), NOW()),
    (430000000000000073, 'weekly_report_fields_innovation_sales_v1', 'document_links', '相关文档链接或佐证材料', '0', '任务相关文档链接或佐证材料。', 'active', 150, NOW(), NOW());

INSERT INTO `system_dictionary`
    (id, dict_type, dict_code, dict_name, dict_value, description, status, sort_order, created_at, updated_at)
VALUES
    (100000000000000110, 'report_template', 'functional_group_v1', '职能组周报', 'functional_group', '职能组使用的职能事项周报模板。', 'active', 100, NOW(), NOW()),
    (430000000000000074, 'weekly_report_fields_functional_group_v1', 'task_name', '工作任务', '1', '职能事项工作任务名称。', 'active', 10, NOW(), NOW()),
    (430000000000000075, 'weekly_report_fields_functional_group_v1', 'work_content', '主要工作内容', '0', '职能事项主要工作内容。', 'active', 20, NOW(), NOW()),
    (430000000000000076, 'weekly_report_fields_functional_group_v1', 'output_description', '输出成果', '1', '职能事项输出成果。', 'active', 30, NOW(), NOW()),
    (430000000000000077, 'weekly_report_fields_functional_group_v1', 'planned_completion_date', '计划完成时间', '1', '职能事项计划完成日期。', 'active', 40, NOW(), NOW()),
    (430000000000000078, 'weekly_report_fields_functional_group_v1', 'progress_text', '工作进展（截至月日）', '0', '职能事项截至统计日期的工作进展。', 'active', 50, NOW(), NOW()),
    (430000000000000079, 'weekly_report_fields_functional_group_v1', 'progress_percent', '完成进度（百分比）', '1', '职能事项完成进度百分比。', 'active', 60, NOW(), NOW()),
    (430000000000000080, 'weekly_report_fields_functional_group_v1', 'delay_reason', '进度缓慢原因说明', '0', '职能事项进度缓慢原因。', 'active', 70, NOW(), NOW()),
    (430000000000000081, 'weekly_report_fields_functional_group_v1', 'on_time_status', '是否在计划时间内完成', '1', '职能事项按计划完成状态。', 'active', 80, NOW(), NOW()),
    (430000000000000082, 'weekly_report_fields_functional_group_v1', 'actual_completion_date', '实际完成时间', '0', '职能事项实际完成日期。', 'active', 90, NOW(), NOW()),
    (430000000000000083, 'weekly_report_fields_functional_group_v1', 'owner_name', '责任人', '0', '职能事项责任人。', 'active', 100, NOW(), NOW()),
    (430000000000000084, 'weekly_report_fields_functional_group_v1', 'collaborator_names', '协作人', '0', '职能事项协作人。', 'active', 110, NOW(), NOW()),
    (430000000000000085, 'weekly_report_fields_functional_group_v1', 'document_links', '相关文档链接或佐证材料', '0', '职能事项相关文档链接或佐证材料。', 'active', 120, NOW(), NOW());

INSERT INTO `organization_group`
    (id, group_code, group_name, description, parent_group_id, is_system, status, created_at, updated_at)
VALUES
    (300000000000000006, 'president', '总裁', '公司组织架构最高管理层。', NULL, 1, 'active', NOW(), NOW()),
    (300000000000000004, 'president_office', '总裁办', '总裁经营管理与决策支持分组。', 300000000000000006, 1, 'active', NOW(), NOW()),
    (300000000000000007, 'functional', '职能组', '公司职能支持组织。', 300000000000000006, 1, 'active', NOW(), NOW()),
    (300000000000000008, 'business', '业务组', '公司业务执行组织。', 300000000000000006, 1, 'active', NOW(), NOW()),
    (300000000000000005, 'operations', '运维组', '系统管理员和平台运维角色组。', 300000000000000007, 1, 'active', NOW(), NOW()),
    (300000000000000001, 'delivery', '交付组', '交付专员、交付助理和交付经理角色组。', 300000000000000008, 1, 'active', NOW(), NOW()),
    (300000000000000002, 'recruitment', '招聘组', '招聘专员和招聘经理角色组。', 300000000000000008, 1, 'active', NOW(), NOW()),
    (300000000000000003, 'sales', '销售组', 'ITO销售与创新业务销售角色组。', 300000000000000008, 1, 'active', NOW(), NOW());

INSERT INTO `role`
    (id, role_code, role_name, scope, description, report_template_code, role_group_code, status, sort_order, created_at, updated_at)
VALUES
    (200000000000000001, 'recruitment_specialist', '招聘专员', 'self', '填写招聘目标、需求管理和招聘成果周报', 'recruitment_v1', 'recruitment', 'active', 10, NOW(), NOW()),
    (200000000000000002, 'delivery_specialist', '交付专员', 'self', '填写客户交付、回款与风险周报', 'delivery_specialist_v1', 'delivery', 'active', 20, NOW(), NOW()),
    (200000000000000003, 'delivery_assistant', '交付助理', 'self', '填写人员流失、交付风险、成本和客户维护周报', 'delivery_assistant_v1', 'delivery', 'active', 30, NOW(), NOW()),
    (200000000000000004, 'recruitment_manager', '招聘经理', 'team', '查看招聘团队周报', 'recruitment_v1', 'recruitment', 'active', 40, NOW(), NOW()),
    (200000000000000005, 'delivery_manager', '交付经理', 'team', '查看交付团队周报', 'delivery_manager_v1', 'delivery', 'active', 50, NOW(), NOW()),
    (200000000000000006, 'president', '总裁', 'all', '查看全公司周报和经营数据', 'president_v1', 'president', 'active', 60, NOW(), NOW()),
    (200000000000000007, 'system_admin', '系统管理员', 'all', '维护用户、角色、分组和系统运营周报', 'system_admin_v1', 'operations', 'active', 70, NOW(), NOW()),
    (200000000000000008, 'ito_sales', 'ITO销售', 'self', '填写ITO客户拓展、商机推进、报价和回款周报', 'ito_sales_v1', 'sales', 'active', 80, NOW(), NOW()),
    (200000000000000009, 'innovation_sales', '创新业务销售', 'self', '填写创新业务机会、方案、签约和回款周报', 'innovation_sales_v1', 'sales', 'active', 90, NOW(), NOW());

-- 演示账号：所有账号的初始登录密码均为 aa123456。
INSERT INTO `role`
    (id, role_code, role_name, scope, description, report_template_code, role_group_code, status, sort_order, created_at, updated_at)
VALUES
    (200000000000000010, 'functional_group', '职能组', 'self', '填写职能事项、成果、进度和协作周报', 'functional_group_v1', 'functional', 'active', 100, NOW(), NOW());

INSERT INTO `user_account`
    (id, username, employee_no, display_name, email, password_ciphertext, manager_id, group_id,
     avatar_color, status, is_super, last_login_at, created_at, updated_at)
VALUES
    (900000000000000001, 'admin', 'DC000001', '系统管理员', 'admin@dingchi.local',
     'rsa_oaep_sha256:Bz-noyQfgCd7QmVkrUOH9-Q6gjH2QzpGx5C5NHPMCEQ62LSi5CZTrgGfzpscjW1Fu4OLtp-Zzw7tR55xHTYF8bo57WCorWugHgzgLRkJmNGjn5nRm5cZ4WgDapv4zC3rBJ6BqW_HE7_H-AthmMoBCEY3d4I6fWYo_j4iOmQe8ldERIWeRT79g0NcRI9n3jSubY-at1SnMduZH6-u7FkgrQoidhIZ7wI1cCEkdjPK88TfgEhit9mc4uw6_Q_FbUp6wWUL9LtN5VwHaogWsZN8liFfQipFNJpESkvMj6eeMoNbJyjnpZ_-0OLYGr7Y0r8QgxsNDG6cwptiwlEai6gkbw==',
     NULL, 300000000000000005, '#315efb', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000002, 'president', 'DC000002', '周总', 'president@dingchi.local',
     'rsa_oaep_sha256:Bz-noyQfgCd7QmVkrUOH9-Q6gjH2QzpGx5C5NHPMCEQ62LSi5CZTrgGfzpscjW1Fu4OLtp-Zzw7tR55xHTYF8bo57WCorWugHgzgLRkJmNGjn5nRm5cZ4WgDapv4zC3rBJ6BqW_HE7_H-AthmMoBCEY3d4I6fWYo_j4iOmQe8ldERIWeRT79g0NcRI9n3jSubY-at1SnMduZH6-u7FkgrQoidhIZ7wI1cCEkdjPK88TfgEhit9mc4uw6_Q_FbUp6wWUL9LtN5VwHaogWsZN8liFfQipFNJpESkvMj6eeMoNbJyjnpZ_-0OLYGr7Y0r8QgxsNDG6cwptiwlEai6gkbw==',
     NULL, 300000000000000006, '#6c5ce7', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000003, 'delivery.manager', 'DC000003', '张三', 'delivery.manager@dingchi.local',
     'rsa_oaep_sha256:Bz-noyQfgCd7QmVkrUOH9-Q6gjH2QzpGx5C5NHPMCEQ62LSi5CZTrgGfzpscjW1Fu4OLtp-Zzw7tR55xHTYF8bo57WCorWugHgzgLRkJmNGjn5nRm5cZ4WgDapv4zC3rBJ6BqW_HE7_H-AthmMoBCEY3d4I6fWYo_j4iOmQe8ldERIWeRT79g0NcRI9n3jSubY-at1SnMduZH6-u7FkgrQoidhIZ7wI1cCEkdjPK88TfgEhit9mc4uw6_Q_FbUp6wWUL9LtN5VwHaogWsZN8liFfQipFNJpESkvMj6eeMoNbJyjnpZ_-0OLYGr7Y0r8QgxsNDG6cwptiwlEai6gkbw==',
     900000000000000002, 300000000000000001, '#168aad', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000004, 'recruitment.manager', 'DC000004', '李四', 'recruitment.manager@dingchi.local',
     'rsa_oaep_sha256:Bz-noyQfgCd7QmVkrUOH9-Q6gjH2QzpGx5C5NHPMCEQ62LSi5CZTrgGfzpscjW1Fu4OLtp-Zzw7tR55xHTYF8bo57WCorWugHgzgLRkJmNGjn5nRm5cZ4WgDapv4zC3rBJ6BqW_HE7_H-AthmMoBCEY3d4I6fWYo_j4iOmQe8ldERIWeRT79g0NcRI9n3jSubY-at1SnMduZH6-u7FkgrQoidhIZ7wI1cCEkdjPK88TfgEhit9mc4uw6_Q_FbUp6wWUL9LtN5VwHaogWsZN8liFfQipFNJpESkvMj6eeMoNbJyjnpZ_-0OLYGr7Y0r8QgxsNDG6cwptiwlEai6gkbw==',
     900000000000000002, 300000000000000002, '#8b5cf6', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000005, 'recruiter', 'DC000005', '林晓', 'recruiter@dingchi.local',
     'rsa_oaep_sha256:Bz-noyQfgCd7QmVkrUOH9-Q6gjH2QzpGx5C5NHPMCEQ62LSi5CZTrgGfzpscjW1Fu4OLtp-Zzw7tR55xHTYF8bo57WCorWugHgzgLRkJmNGjn5nRm5cZ4WgDapv4zC3rBJ6BqW_HE7_H-AthmMoBCEY3d4I6fWYo_j4iOmQe8ldERIWeRT79g0NcRI9n3jSubY-at1SnMduZH6-u7FkgrQoidhIZ7wI1cCEkdjPK88TfgEhit9mc4uw6_Q_FbUp6wWUL9LtN5VwHaogWsZN8liFfQipFNJpESkvMj6eeMoNbJyjnpZ_-0OLYGr7Y0r8QgxsNDG6cwptiwlEai6gkbw==',
     900000000000000004, 300000000000000002, '#14b8a6', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000006, 'delivery.specialist', 'DC000006', '陈默', 'delivery.specialist@dingchi.local',
     'rsa_oaep_sha256:Bz-noyQfgCd7QmVkrUOH9-Q6gjH2QzpGx5C5NHPMCEQ62LSi5CZTrgGfzpscjW1Fu4OLtp-Zzw7tR55xHTYF8bo57WCorWugHgzgLRkJmNGjn5nRm5cZ4WgDapv4zC3rBJ6BqW_HE7_H-AthmMoBCEY3d4I6fWYo_j4iOmQe8ldERIWeRT79g0NcRI9n3jSubY-at1SnMduZH6-u7FkgrQoidhIZ7wI1cCEkdjPK88TfgEhit9mc4uw6_Q_FbUp6wWUL9LtN5VwHaogWsZN8liFfQipFNJpESkvMj6eeMoNbJyjnpZ_-0OLYGr7Y0r8QgxsNDG6cwptiwlEai6gkbw==',
     900000000000000003, 300000000000000001, '#0ea5e9', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000007, 'delivery.assistant', 'DC000007', '王助理', 'delivery.assistant@dingchi.local',
     'rsa_oaep_sha256:Bz-noyQfgCd7QmVkrUOH9-Q6gjH2QzpGx5C5NHPMCEQ62LSi5CZTrgGfzpscjW1Fu4OLtp-Zzw7tR55xHTYF8bo57WCorWugHgzgLRkJmNGjn5nRm5cZ4WgDapv4zC3rBJ6BqW_HE7_H-AthmMoBCEY3d4I6fWYo_j4iOmQe8ldERIWeRT79g0NcRI9n3jSubY-at1SnMduZH6-u7FkgrQoidhIZ7wI1cCEkdjPK88TfgEhit9mc4uw6_Q_FbUp6wWUL9LtN5VwHaogWsZN8liFfQipFNJpESkvMj6eeMoNbJyjnpZ_-0OLYGr7Y0r8QgxsNDG6cwptiwlEai6gkbw==',
     900000000000000003, 300000000000000001, '#f59e0b', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000008, 'ito.sales', 'DC000008', '张销售', 'ito.sales@dingchi.local',
     'rsa_oaep_sha256:Bz-noyQfgCd7QmVkrUOH9-Q6gjH2QzpGx5C5NHPMCEQ62LSi5CZTrgGfzpscjW1Fu4OLtp-Zzw7tR55xHTYF8bo57WCorWugHgzgLRkJmNGjn5nRm5cZ4WgDapv4zC3rBJ6BqW_HE7_H-AthmMoBCEY3d4I6fWYo_j4iOmQe8ldERIWeRT79g0NcRI9n3jSubY-at1SnMduZH6-u7FkgrQoidhIZ7wI1cCEkdjPK88TfgEhit9mc4uw6_Q_FbUp6wWUL9LtN5VwHaogWsZN8liFfQipFNJpESkvMj6eeMoNbJyjnpZ_-0OLYGr7Y0r8QgxsNDG6cwptiwlEai6gkbw==',
     900000000000000002, 300000000000000003, '#f97316', 'active', 1, NULL, NOW(), NOW()),
    (900000000000000009, 'innovation.sales', 'DC000009', '李销售', 'innovation.sales@dingchi.local',
     'rsa_oaep_sha256:Bz-noyQfgCd7QmVkrUOH9-Q6gjH2QzpGx5C5NHPMCEQ62LSi5CZTrgGfzpscjW1Fu4OLtp-Zzw7tR55xHTYF8bo57WCorWugHgzgLRkJmNGjn5nRm5cZ4WgDapv4zC3rBJ6BqW_HE7_H-AthmMoBCEY3d4I6fWYo_j4iOmQe8ldERIWeRT79g0NcRI9n3jSubY-at1SnMduZH6-u7FkgrQoidhIZ7wI1cCEkdjPK88TfgEhit9mc4uw6_Q_FbUp6wWUL9LtN5VwHaogWsZN8liFfQipFNJpESkvMj6eeMoNbJyjnpZ_-0OLYGr7Y0r8QgxsNDG6cwptiwlEai6gkbw==',
     900000000000000002, 300000000000000003, '#ec4899', 'active', 1, NULL, NOW(), NOW());

INSERT INTO `user_account`
    (id, username, employee_no, display_name, email, password_ciphertext, manager_id, group_id,
     avatar_color, status, is_super, last_login_at, created_at, updated_at)
VALUES
    (900000000000000010, 'functional.group', 'DC000010', '职能组用户', 'functional.group@dingchi.local',
     'rsa_oaep_sha256:Bz-noyQfgCd7QmVkrUOH9-Q6gjH2QzpGx5C5NHPMCEQ62LSi5CZTrgGfzpscjW1Fu4OLtp-Zzw7tR55xHTYF8bo57WCorWugHgzgLRkJmNGjn5nRm5cZ4WgDapv4zC3rBJ6BqW_HE7_H-AthmMoBCEY3d4I6fWYo_j4iOmQe8ldERIWeRT79g0NcRI9n3jSubY-at1SnMduZH6-u7FkgrQoidhIZ7wI1cCEkdjPK88TfgEhit9mc4uw6_Q_FbUp6wWUL9LtN5VwHaogWsZN8liFfQipFNJpESkvMj6eeMoNbJyjnpZ_-0OLYGr7Y0r8QgxsNDG6cwptiwlEai6gkbw==',
     900000000000000002, 300000000000000007, '#22c55e', 'active', 1, NULL, NOW(), NOW());

INSERT INTO `user_role` (id, user_id, role_id, is_default, status, created_at, updated_at) VALUES
    (910000000000000001, 900000000000000001, 200000000000000007, 1, 'active', NOW(), NOW()),
    (910000000000000002, 900000000000000002, 200000000000000006, 1, 'active', NOW(), NOW()),
    (910000000000000003, 900000000000000002, 200000000000000007, 0, 'active', NOW(), NOW()),
    (910000000000000004, 900000000000000003, 200000000000000005, 1, 'active', NOW(), NOW()),
    (910000000000000005, 900000000000000003, 200000000000000002, 0, 'active', NOW(), NOW()),
    (910000000000000006, 900000000000000004, 200000000000000004, 1, 'active', NOW(), NOW()),
    (910000000000000007, 900000000000000005, 200000000000000001, 1, 'active', NOW(), NOW()),
    (910000000000000008, 900000000000000006, 200000000000000002, 1, 'active', NOW(), NOW()),
    (910000000000000009, 900000000000000007, 200000000000000003, 1, 'active', NOW(), NOW()),
    (910000000000000010, 900000000000000008, 200000000000000008, 1, 'active', NOW(), NOW()),
    (910000000000000011, 900000000000000009, 200000000000000009, 1, 'active', NOW(), NOW());

INSERT INTO `user_group_membership` (id, user_id, group_id, is_primary, status, created_at, updated_at) VALUES
    (920000000000000001, 900000000000000001, 300000000000000005, 1, 'active', NOW(), NOW()),
    (920000000000000002, 900000000000000002, 300000000000000006, 1, 'active', NOW(), NOW()),
    (920000000000000003, 900000000000000003, 300000000000000001, 1, 'active', NOW(), NOW()),
    (920000000000000004, 900000000000000004, 300000000000000002, 1, 'active', NOW(), NOW()),
    (920000000000000005, 900000000000000005, 300000000000000002, 1, 'active', NOW(), NOW()),
    (920000000000000006, 900000000000000006, 300000000000000001, 1, 'active', NOW(), NOW()),
    (920000000000000007, 900000000000000007, 300000000000000001, 1, 'active', NOW(), NOW()),
    (920000000000000008, 900000000000000008, 300000000000000003, 1, 'active', NOW(), NOW()),
    (920000000000000009, 900000000000000009, 300000000000000003, 1, 'active', NOW(), NOW());

-- 仅 admin 为超级管理员；超级管理员不属于任何组织分组，账号只能通过数据库维护。
UPDATE `user_account`
SET `is_super` = CASE WHEN `username` = 'admin' THEN 1 ELSE 0 END;

UPDATE `user_account`
SET `group_id` = NULL,
    `manager_id` = NULL
WHERE `username` = 'admin';

DELETE FROM `user_group_membership`
WHERE `user_id` = (SELECT `id` FROM `user_account` WHERE `username` = 'admin');

-- 每个模板一份模板头；招聘专员和招聘经理共用 recruitment_v1，页面按配置渲染。
INSERT INTO `user_role` (id, user_id, role_id, is_default, status, created_at, updated_at) VALUES
    (910000000000000012, 900000000000000010, 200000000000000010, 1, 'active', NOW(), NOW());

INSERT INTO `user_group_membership` (id, user_id, group_id, is_primary, status, created_at, updated_at) VALUES
    (920000000000000010, 900000000000000010, 300000000000000007, 1, 'active', NOW(), NOW());

INSERT INTO `report_template`
    (id, template_code, template_name, description,
     status, effective_from, effective_to, created_at, updated_at)
VALUES
    (400000000000000001, 'recruitment_v1', '招聘周报', '按月计划、需求管理和招聘成果填写招聘周报', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000002, 'delivery_specialist_v1', '交付专员周报', '围绕客户交付、招聘转化、成本和回款填写周报', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000003, 'delivery_assistant_v1', '交付助理周报', '围绕人员构成、流失替补、风险成本与客户维护填写周报', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000005, 'delivery_manager_v1', '交付经理周报', '汇总交付团队、客户经营、回款和风险', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000006, 'president_v1', '总裁经营周报', '从全局视角填写经营重点、关键决策和组织风险', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000007, 'system_admin_v1', '系统运营周报', '填写系统运行、数据质量和运营支持事项', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000008, 'ito_sales_v1', 'ITO销售周报', '围绕客户拓展、商机推进、报价和回款填写周报', 'active', '2026-01-01', NULL, NOW(), NOW()),
    (400000000000000009, 'innovation_sales_v1', '创新业务销售周报', '围绕创新业务机会、方案、签约和回款填写周报', 'active', '2026-01-01', NULL, NOW(), NOW());

INSERT INTO `report_template`
    (id, template_code, template_name, description,
     status, effective_from, effective_to, created_at, updated_at)
VALUES
    (400000000000000010, 'functional_group_v1', '职能组周报', '参考交付周报模板记录职能事项、工作成果、进度和协作信息。', 'active', '2026-01-01', NULL, NOW(), NOW());

INSERT INTO `report_template_item`
    (id, template_id, section_code, section_name, task_code, label, guidance, item_type, scope_type, value_type, unit, required, validation_rule, sort_order, config_json, created_at, updated_at)
VALUES
    (410000000000000001, 400000000000000001, 'overall', '总体目标', 'recruitment_goal', '招聘目标推进', '记录月度招聘目标、客户入职目标和招聘成果。', 'task', 'overall', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000002, 400000000000000001, 'demand', '需求管理', 'demand_response', '识别重点需求与响应', '记录重点客户需求确认、岗位优先级和招聘协同目标。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000003, 400000000000000001, 'other', '其他', 'other_work', '其他工作', '填写不属于以上模块的招聘工作。', 'task', 'overall', 'text', '', 0, '', 3, '{}', NOW(), NOW()),
    (410000000000000004, 400000000000000001, 'overall', '总体目标', 'resume_recommendations', '简历推荐', '填写本周简历推荐目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '份', 0, '', 4, '{}', NOW(), NOW()),
    (410000000000000005, 400000000000000001, 'overall', '总体目标', 'interviews', '到面人数', '填写本周到面目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 5, '{}', NOW(), NOW()),
    (410000000000000006, 400000000000000002, 'customer', '客户需求和招聘转化', 'customer_progress', '重点客户交付进展', '按客户记录需求、入职与交付成果。', 'task', 'customer', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000007, 400000000000000002, 'risk', '风险控制', 'risk_resolution', '延期/风险项处理', '必须填写原因、下一步和预计完成日期。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000008, 400000000000000002, 'overall', '总体目标', 'net_headcount', '净增人数', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 3, '{}', NOW(), NOW()),
    (410000000000000009, 400000000000000002, 'overall', '总体目标', 'collection_amount', '回款金额', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'amount', '万元', 0, '', 4, '{}', NOW(), NOW()),
    (410000000000000010, 400000000000000003, 'customer', '客户交付与人员管控', 'headcount_and_attrition', '人员流失与替补目标', '记录客户人员构成、流失控制、离职替补和空岗人日目标。', 'task', 'customer', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000011, 400000000000000003, 'risk', '风险与成本控制', 'release_and_risk_control', '释放、风险与成本控制', '记录客户释放、风险人员、假期、成本和报价调薪管控措施。', 'task', 'customer', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000012, 400000000000000003, 'customer', '客户交付与人员管控', 'customer_relationship', '客情与员工沟通', '记录客情维护、员工沟通和客户拜访安排。', 'task', 'customer', 'text', '', 0, '', 3, '{}', NOW(), NOW()),
    (410000000000000013, 400000000000000003, 'other', '其他工作', 'other_work_arrangement', '其他工作安排', '记录外派员工入职培训、礼品发放、体检安排等事项。', 'task', 'overall', 'text', '', 0, '', 4, '{}', NOW(), NOW()),
    (410000000000000026, 400000000000000003, 'overall', '总体目标', 'attrition_count', '流失控制人数', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 1, '{}', NOW(), NOW()),
    (410000000000000027, 400000000000000003, 'overall', '总体目标', 'replacement_count', '离职替补人数', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 2, '{}', NOW(), NOW()),
    (410000000000000028, 400000000000000003, 'customer', '客户交付与人员管控', 'total_headcount', '当月总人数', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 3, '{}', NOW(), NOW()),
    (410000000000000029, 400000000000000003, 'risk', '风险与成本控制', 'high_risk_items', '中高风险人数', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 4, '{}', NOW(), NOW()),
    (410000000000000014, 400000000000000001, 'overall', '总体目标', 'onboarded', '有效入职', '填写本周有效入职目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'number', '人', 0, '', 6, '{}', NOW(), NOW()),
    (410000000000000015, 400000000000000001, 'demand', '需求管理', 'demand_response_rate', '需求响应率', '填写本周需求响应率，范围为 0-100%。', 'metric', 'overall', 'percent', '%', 0, '0-100', 7, '{}', NOW(), NOW()),
    (410000000000000017, 400000000000000005, 'team', '交付团队', 'team_review', '交付团队复盘', '汇总交付专员与交付助理工作。', 'task', 'overall', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000018, 400000000000000005, 'customer', '客户经营', 'customer_review', '重点客户经营', '记录合同、续签、回款及客情。', 'task', 'customer', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000019, 400000000000000005, 'team', '交付团队', 'team_completion_rate', '团队完成率', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'percent', '%', 0, '0-100', 3, '{}', NOW(), NOW()),
    (410000000000000020, 400000000000000006, 'business', '经营概览', 'business_review', '经营重点复盘', '填写跨部门关键进展与结果。', 'task', 'overall', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000021, 400000000000000006, 'decision', '关键决策', 'decision_items', '关键决策事项', '填写需要管理层拍板的事项。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000022, 400000000000000006, 'business', '经营概览', 'overall_completion_rate', '整体完成率', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'percent', '%', 0, '0-100', 3, '{}', NOW(), NOW()),
    (410000000000000023, 400000000000000007, 'operation', '系统运营', 'service_operation', '系统运行维护', '记录发布、告警和问题闭环。', 'task', 'overall', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000024, 400000000000000007, 'data', '数据质量', 'data_quality', '数据质量巡检', '记录用户、角色和周报数据检查。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000025, 400000000000000007, 'operation', '系统运营', 'service_availability', '服务可用率', '填写本周目标与实际值，单位清晰可追溯。', 'metric', 'overall', 'percent', '%', 0, '0-100', 3, '{}', NOW(), NOW()),
    (410000000000000040, 400000000000000008, 'overall', '月度目标', 'monthly_goal', '月度目标', '记录目标客户签约、新增机会、中标率、合同收入和客户关系目标。', 'task', 'customer', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000041, 400000000000000008, 'market', '市场开拓', 'market_development', '市场开拓', '记录老客户和新客户机会盘点、机会策略及招投标协同。', 'task', 'customer', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000042, 400000000000000008, 'relationship', '客户关系管理', 'customer_relationship', '客户关系管理', '按目标客户记录教练、内线、决策链、客户画像和拜访计划。', 'task', 'customer', 'text', '', 1, '', 3, '{}', NOW(), NOW()),
    (410000000000000043, 400000000000000008, 'contract', '新签合同销售收入', 'new_contract_revenue_task', '新签合同销售收入', '记录新增需求、客户关系维护和合同收入推进。', 'task', 'customer', 'text', '', 1, '', 4, '{}', NOW(), NOW()),
    (410000000000000044, 400000000000000008, 'other', '其他', 'other_work', '其他', '填写其他销售专项工作。', 'task', 'customer', 'text', '', 0, '', 5, '{}', NOW(), NOW()),
    (410000000000000045, 400000000000000008, 'overall', '月度目标', 'target_signings', '目标客户签约数', '填写月度目标客户签约数量。', 'metric', 'overall', 'number', '家', 0, '', 6, '{}', NOW(), NOW()),
    (410000000000000046, 400000000000000008, 'overall', '月度目标', 'new_opportunities', '新增机会', '填写月度新增机会数量。', 'metric', 'overall', 'number', '家', 0, '', 7, '{}', NOW(), NOW()),
    (410000000000000047, 400000000000000008, 'overall', '月度目标', 'win_rate', '中标率', '填写月度目标中标率，范围为 0-100%。', 'metric', 'overall', 'percent', '%', 0, '0-100', 8, '{}', NOW(), NOW()),
    (410000000000000048, 400000000000000008, 'overall', '月度目标', 'signed_contracts', '合同签订数', '填写月度合同签订数量。', 'metric', 'overall', 'number', '家', 0, '', 9, '{}', NOW(), NOW()),
    (410000000000000049, 400000000000000008, 'overall', '月度目标', 'new_contract_revenue', '新签合同销售收入', '填写月度新签合同销售收入。', 'metric', 'overall', 'amount', '万元', 0, '', 10, '{}', NOW(), NOW()),
    (410000000000000050, 400000000000000008, 'overall', '月度目标', 'new_contract_demands', '新签合同需求数', '填写月度新签合同需求数量。', 'metric', 'overall', 'number', '个', 0, '', 11, '{}', NOW(), NOW()),
    (410000000000000051, 400000000000000008, 'overall', '月度目标', 'effective_onboarded', '有效入职人数', '填写月度有效入职人数。', 'metric', 'overall', 'number', '个', 0, '', 12, '{}', NOW(), NOW()),
    (410000000000000052, 400000000000000009, 'market', '市场开拓', 'market_development', '市场开拓', '记录目标客户签约、新增机会、营业收入、存量项目管理、新项目机会管理和招投标管理。', 'task', 'customer', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000053, 400000000000000009, 'relationship', '客户关系管理', 'customer_relationship', '客户关系管理', '记录新客户中高层关系推进、客户分级管理、拜访和客户画像。', 'task', 'customer', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000054, 400000000000000009, 'receivable', '应收款管理', 'receivables_management', '应收款管理', '记录应收款回款率和超期应收款处理策略。', 'task', 'customer', 'text', '', 1, '', 3, '{}', NOW(), NOW()),
    (410000000000000055, 400000000000000009, 'market', '市场开拓', 'target_signings', '目标客户签约数', '填写目标客户签约数量，单位为家。', 'metric', 'overall', 'number', '家', 0, '', 4, '{}', NOW(), NOW()),
    (410000000000000056, 400000000000000009, 'market', '市场开拓', 'new_opportunities', '新增机会点', '填写新增机会点数量，单位为家。', 'metric', 'overall', 'number', '家', 0, '', 5, '{}', NOW(), NOW()),
    (410000000000000057, 400000000000000009, 'market', '市场开拓', 'new_opportunity_amount', '新增机会额', '填写新增机会金额，单位为万元。', 'metric', 'overall', 'amount', '万元', 0, '', 6, '{}', NOW(), NOW()),
    (410000000000000058, 400000000000000009, 'market', '市场开拓', 'win_rate', '中标率', '填写中标率，范围为 0-100%。', 'metric', 'overall', 'percent', '%', 0, '0-100', 7, '{}', NOW(), NOW()),
    (410000000000000059, 400000000000000009, 'market', '市场开拓', 'existing_project_revenue', '存量项目营业收入', '填写存量项目营业收入，单位为万元。', 'metric', 'overall', 'amount', '万元', 0, '', 8, '{}', NOW(), NOW()),
    (410000000000000060, 400000000000000009, 'market', '市场开拓', 'new_project_revenue', '新增项目营业收入', '填写新增项目营业收入，单位为万元。', 'metric', 'overall', 'amount', '万元', 0, '', 9, '{}', NOW(), NOW()),
    (410000000000000061, 400000000000000009, 'relationship', '客户关系管理', 'customer_coaches', '客户教练', '填写客户教练数量，单位为名。', 'metric', 'overall', 'number', '名', 0, '', 10, '{}', NOW(), NOW()),
    (410000000000000062, 400000000000000009, 'relationship', '客户关系管理', 'customer_insiders', '客户内线', '填写客户内线数量，单位为名。', 'metric', 'overall', 'number', '名', 0, '', 11, '{}', NOW(), NOW()),
    (410000000000000063, 400000000000000009, 'receivable', '应收款管理', 'receivable_recovery_rate', '应收款回款率', '填写应收款回款率，范围为 0-100%。', 'metric', 'overall', 'percent', '%', 0, '0-100', 12, '{}', NOW(), NOW());

-- 业务数据（周报、月度计划、任务明细、指标和附件）不在初始化种子中，由页面/API运行时产生。

INSERT INTO `report_template_item`
    (id, template_id, section_code, section_name, task_code, label, guidance, item_type, scope_type, value_type, unit, required, validation_rule, sort_order, config_json, created_at, updated_at)
VALUES
    (410000000000000064, 400000000000000010, 'work', '重点工作', 'functional_work_progress', '重点工作进展', '记录职能事项的工作进展和输出成果。', 'task', 'overall', 'text', '', 1, '', 1, '{}', NOW(), NOW()),
    (410000000000000065, 400000000000000010, 'risk', '风险控制', 'risk_resolution', '延期/风险项处理', '记录延期原因、风险影响和后续处理措施。', 'task', 'overall', 'text', '', 1, '', 2, '{}', NOW(), NOW()),
    (410000000000000066, 400000000000000010, 'other', '其他工作', 'other_work', '其他工作', '记录本周其他职能工作事项。', 'task', 'overall', 'text', '', 0, '', 3, '{}', NOW(), NOW()),
    (410000000000000067, 400000000000000010, 'overall', '总体目标', 'net_headcount', '净增人数', '填写本月职能组净增人数目标。', 'metric', 'overall', 'number', '人', 0, '', 4, '{}', NOW(), NOW()),
    (410000000000000068, 400000000000000010, 'work', '重点工作', 'new_demands', '新增事项数', '填写本月新增职能事项数量。', 'metric', 'overall', 'number', '项', 0, '', 5, '{}', NOW(), NOW()),
    (410000000000000069, 400000000000000010, 'work', '重点工作', 'incremental_onboarded', '完成事项数', '填写本月已完成职能事项数量。', 'metric', 'overall', 'number', '项', 0, '', 6, '{}', NOW(), NOW()),
    (410000000000000070, 400000000000000010, 'overall', '总体目标', 'collection_amount', '预算/回款金额', '填写本月预算或回款目标金额。', 'metric', 'overall', 'amount', '万元', 0, '', 7, '{}', NOW(), NOW()),
    (410000000000000071, 400000000000000010, 'risk', '风险控制', 'high_risk_items', '高风险事项', '填写本月需重点关注的高风险事项数量。', 'metric', 'overall', 'number', '项', 0, '', 8, '{}', NOW(), NOW());

COMMIT;
