-- 周报任务列表字段字典增量脚本（MySQL 8+）
-- 用于已经执行 01_建表DDL.sql、02_初始化DML.sql 以前版本的数据库。
-- 本脚本不新增表或字段，只向已有 system_dictionary 表补充列定义。
-- dict_type 按角色拆分；dict_value=1 表示默认展示，=0 表示可选但默认隐藏。
-- sort_order 与 Excel 表头顺序一致，序号列由页面固定展示，不在字典中配置。

SET NAMES utf8mb4;
START TRANSACTION;

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

COMMIT;
