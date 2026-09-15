-- DingChi 周报系统：交付专员周报增量结构脚本
-- 用途：已有数据库已执行旧版 01/02 脚本时，手工执行本文件补充新表和新字段。
-- 本脚本不会删除数据，不会执行 Django 迁移，也不会由项目启动自动执行。

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS `monthly_plan` (
    `id` BIGINT NOT NULL COMMENT '雪花算法主键ID',
    `role_code` VARCHAR(64) NOT NULL COMMENT '月度计划所属角色编码',
    `employee_id` BIGINT NOT NULL COMMENT '员工ID，逻辑关联 user_account.id',
    `group_id` BIGINT NULL COMMENT '组织分组ID，逻辑关联 organization_group.id',
    `month_key` VARCHAR(7) NOT NULL COMMENT '计划月份，格式 YYYY-MM',
    `summary` LONGTEXT NOT NULL COMMENT '月度计划内容',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间',
    `updated_at` DATETIME(6) NOT NULL COMMENT '最后更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_monthly_plan_employee_role_month` (`employee_id`, `role_code`, `month_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='员工角色月度计划表';

DELIMITER $$

DROP PROCEDURE IF EXISTS `add_weekly_report_item_column_if_missing`$$
CREATE PROCEDURE `add_weekly_report_item_column_if_missing`(
    IN column_name_arg VARCHAR(64),
    IN column_definition_arg VARCHAR(500)
)
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = 'weekly_report_item'
          AND column_name = column_name_arg
    ) THEN
        SET @alter_sql = CONCAT(
            'ALTER TABLE `weekly_report_item` ADD COLUMN `',
            column_name_arg,
            '` ',
            column_definition_arg
        );
        PREPARE alter_statement FROM @alter_sql;
        EXECUTE alter_statement;
        DEALLOCATE PREPARE alter_statement;
    END IF;
END$$

CALL `add_weekly_report_item_column_if_missing`(
    'work_content',
    'LONGTEXT NOT NULL COMMENT ''主要工作内容'''
)$$
CALL `add_weekly_report_item_column_if_missing`(
    'owner_name_snapshot',
    'VARCHAR(128) NOT NULL DEFAULT '''' COMMENT ''责任人姓名快照'''
)$$
CALL `add_weekly_report_item_column_if_missing`(
    'collaborator_names',
    'VARCHAR(500) NOT NULL DEFAULT '''' COMMENT ''协作人姓名，多个以逗号分隔'''
)$$
CALL `add_weekly_report_item_column_if_missing`(
    'document_links',
    'LONGTEXT NOT NULL COMMENT ''相关文档链接或佐证材料'''
)$$

DROP PROCEDURE `add_weekly_report_item_column_if_missing`$$

DELIMITER ;

-- 可选：给现有交付专员月度计划写入一条空白记录时，请使用应用生成的雪花 ID，
-- 不要在此脚本中使用自增或固定业务主键。
