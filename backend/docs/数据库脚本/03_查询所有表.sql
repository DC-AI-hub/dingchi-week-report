-- DingChi 周报系统 MySQL 全表查询脚本
-- 用途：查询当前数据库中的项目业务表和 Django 框架表。
-- 说明：本脚本只读，不新增、修改或删除任何数据；请在目标数据库中执行。

SET NAMES utf8mb4;

-- =========================
-- 一、查询当前数据库的表名及数据库表注释
-- =========================
SELECT
    TABLE_NAME AS `表名`,
    TABLE_COMMENT AS `表注释`,
    TABLE_ROWS AS `估算行数`
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME;

-- =========================
-- 二、查询业务表
-- =========================

-- 系统静态字典表：管理角色范围、周报模板、列表字段等静态配置。
SELECT * FROM `system_dictionary`;

-- 组织分组表：保存多层级组织分组及系统预设分组。
SELECT * FROM `organization_group`;

-- 系统角色表：保存角色编码、中文名称、数据范围和周报模板配置。
SELECT * FROM `role`;

-- 用户账号表：保存员工账号、上下级关系、主分组和登录信息。
SELECT * FROM `user_account`;

-- 用户角色关联表：保存用户可切换的角色及默认角色。
SELECT * FROM `user_role`;

-- 用户组织分组关联表：保存用户与组织分组的多对多关系。
SELECT * FROM `user_group_membership`;

-- 周报模板主表：保存各角色使用的周报模板版本。
SELECT * FROM `report_template`;

-- 周报模板项目明细表：保存模板分区、任务项、指标项及其顺序。
SELECT * FROM `report_template_item`;

-- 周报主表：保存周报周期、所属月度、填报人和报告状态。
SELECT * FROM `weekly_report`;

-- 角色月度共用计划主表：保存同一员工、角色和月份共用的月度计划。
SELECT * FROM `monthly_plan`;

-- 周报任务明细表：保存周报中的客户任务、进度、负责人和文档链接。
SELECT * FROM `weekly_report_item`;

-- 周报任务进度历史快照表
SELECT * FROM `weekly_report_item_progress_history`;

-- 周报指标明细表：保存周报任务或周报总体指标数据。
SELECT * FROM `weekly_report_metric`;

-- 系统通用附件表：按业务类型和逻辑关联 ID 保存各业务上传的附件。
SELECT * FROM `system_attachment`;

-- =========================
-- 三、查询 Django 框架表
-- =========================

-- Django 迁移记录表：保存已执行的迁移名称和时间。
SELECT * FROM `django_migrations`;

-- Django 内容类型表：保存应用模型的内容类型元数据。
SELECT * FROM `django_content_type`;

-- Django 权限表：保存后台模型权限定义。
SELECT * FROM `auth_permission`;

-- Django 权限组表：保存后台权限组名称。
SELECT * FROM `auth_group`;

-- Django 权限组关系表：保存权限组与权限的关联。
SELECT * FROM `auth_group_permissions`;

-- Django 后台用户表：保存 Django Admin 用户账号。
SELECT * FROM `auth_user`;

-- Django 用户权限组关系表：保存后台用户与权限组的关联。
SELECT * FROM `auth_user_groups`;

-- Django 用户权限关系表：保存后台用户与直接权限的关联。
SELECT * FROM `auth_user_user_permissions`;

-- Django 管理后台操作日志表：保存 Admin 操作记录。
SELECT * FROM `django_admin_log`;

-- Django 会话表：保存服务端会话数据和过期时间。
SELECT * FROM `django_session`;
