-- DingChi 周报系统：系统通用附件表增量脚本
-- 用途：为所有业务提供统一附件存储；业务通过 attachment_type + relation_id 逻辑关联。
-- 当前周报接口使用 attachment_type = 'weekly_report'，relation_id = weekly_report.id，
-- 可选 relation_sub_id = weekly_report_item.id。脚本可重复执行，不会覆盖已有数据。

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS `system_attachment` (
    `id` BIGINT NOT NULL COMMENT '雪花算法主键ID',
    `attachment_type` VARCHAR(64) NOT NULL COMMENT '业务类型，例如 weekly_report；不是文件格式',
    `relation_id` BIGINT NOT NULL COMMENT '业务主记录ID，按 attachment_type 解释',
    `relation_sub_id` BIGINT NULL COMMENT '业务子记录ID，预留逻辑关联，不绑定具体模块',
    `storage_key` VARCHAR(512) NOT NULL COMMENT '文件存储键，相对 MEDIA_ROOT 的路径',
    `file_url` LONGTEXT NOT NULL COMMENT '附件访问地址',
    `file_name` VARCHAR(255) NOT NULL COMMENT '用户上传的原始文件名',
    `mime_type` VARCHAR(128) NOT NULL COMMENT '文件 MIME 类型',
    `file_size` BIGINT NOT NULL DEFAULT 0 COMMENT '文件大小，单位字节',
    `description` VARCHAR(500) NOT NULL COMMENT '附件说明',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间',
    `updated_at` DATETIME(6) NOT NULL COMMENT '最后更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_system_attachment_relation` (`attachment_type`, `relation_id`, `relation_sub_id`),
    KEY `idx_system_attachment_type` (`attachment_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统通用附件表';

-- 兼容已经创建过 weekly_report_attachment 的本地数据库。
-- 使用动态 SQL 避免旧表不存在时整段脚本失败；INSERT IGNORE 保证可重复执行。
SET @legacy_attachment_table_exists := (
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_schema = DATABASE()
      AND table_name = 'weekly_report_attachment'
);

SET @migrate_legacy_attachment_sql := IF(
    @legacy_attachment_table_exists > 0,
    'INSERT IGNORE INTO `system_attachment`
        (`id`, `attachment_type`, `relation_id`, `relation_sub_id`, `storage_key`,
         `file_url`, `file_name`, `mime_type`, `file_size`, `description`,
         `created_at`, `updated_at`)
     SELECT `id`, ''weekly_report'', `report_id`, `item_id`, `storage_key`,
            `file_url`, `file_name`, `mime_type`, `file_size`, `description`,
            `created_at`, `updated_at`
     FROM `weekly_report_attachment`',
    'SELECT 1'
);

PREPARE migrate_legacy_attachment_stmt FROM @migrate_legacy_attachment_sql;
EXECUTE migrate_legacy_attachment_stmt;
DEALLOCATE PREPARE migrate_legacy_attachment_stmt;

