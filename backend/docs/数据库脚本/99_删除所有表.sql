-- DingChi 周报系统：删除当前项目已知全部表
-- 警告：本脚本会永久删除表结构和表内数据，仅允许在本地开发或已确认的目标数据库执行。
-- 本脚本不会 DROP DATABASE，也不会处理本项目之外的未知表。

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 业务表（明细/记录表先删除）
DROP TABLE IF EXISTS `system_attachment`;
DROP TABLE IF EXISTS `weekly_report_daily_task`;
DROP TABLE IF EXISTS `weekly_report_metric`;
DROP TABLE IF EXISTS `weekly_report_item_progress_history`;
DROP TABLE IF EXISTS `weekly_report_item`;
DROP TABLE IF EXISTS `weekly_report`;
DROP TABLE IF EXISTS `monthly_plan`;
DROP TABLE IF EXISTS `report_template_item`;
DROP TABLE IF EXISTS `report_template`;
DROP TABLE IF EXISTS `user_group_membership`;
DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `user_role`;
DROP TABLE IF EXISTS `user_account`;
DROP TABLE IF EXISTS `role`;
DROP TABLE IF EXISTS `organization_group`;
DROP TABLE IF EXISTS `system_dictionary`;

SET FOREIGN_KEY_CHECKS = 1;
