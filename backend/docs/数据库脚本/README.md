# 数据库脚本说明

本目录保存当前周报系统的手工 SQL 脚本，表结构与 `backend/apps/**/models.py` 及 Django 内置组件保持一致。

## 文件

| 文件 | 用途 |
| --- | --- |
| `01_建表DDL.sql` | 创建当前项目已知的业务表和 Django 框架表。所有建表语句均为 `CREATE TABLE IF NOT EXISTS`，已有表不会被覆盖。表名、字段名均使用下划线命名，并为表和每个字段提供中文注释。 |
| `02_初始化DML.sql` | 唯一的完整初始化脚本，包含字典、组织、角色、用户、周报模板及演示周报数据，可重复执行（使用 `INSERT IGNORE`）。 |
| `03_交付专员周报结构变更.sql` | 已有数据库的增量脚本：新增月度计划表，并补充交付专员周任务字段；请在本地手工执行。 |
| `04_周报字段字典DML.sql` | 已完成基础初始化的数据库补充周报任务列表字段字典；按角色配置 Excel 字段顺序和默认展示状态，不新增表或字段。 |
| `05_system_attachment.sql` | 已有数据库的增量脚本：新增系统通用附件表；如检测到旧版周报附件表，则将历史文件记录迁移到通用表，原记录保留。 |
| `99_删除所有表.sql` | 删除本项目当前已知的全部业务表和 Django 框架表。脚本会删除数据，执行前必须确认数据库和备份。 |

## 推荐执行顺序

在已经创建好的 MySQL 数据库中按以下顺序执行：

```text
01_建表DDL.sql
02_初始化DML.sql
```

如果数据库已经执行过旧版初始化脚本，只需额外执行 `03_交付专员周报结构变更.sql`、`04_周报字段字典DML.sql` 和 `05_system_attachment.sql`（按顺序）。项目启动不会自动执行这些 SQL。

项目启动不会自动执行表迁移或初始化脚本。生产环境仍建议使用 Django migration 作为唯一的结构变更来源；手工 DDL 主要用于本地初始化、交付或需要纯 SQL 的环境，不要在同一套空库上重复混用两套建表流程。

## 设计约束

- 业务表主键统一使用应用层雪花算法生成的 `BIGINT`，不会设置 `AUTO_INCREMENT`。
- 日期时间字段统一使用 `DATETIME(6)`；日期周期字段使用 `DATE`。日期时间字段不使用 `BIGINT`，也不使用 `DEFAULT 0`。
- 业务表的用户、角色、分组、模板、周报等关系均使用逻辑 ID/编码，不创建数据库外键；这样与现有跨模块解耦规范一致。
- Django 自带的 `auth`、`contenttypes`、`admin`、`sessions`、`migrations` 表保留框架必需的外键和索引，它们不属于业务关联设计。
- `02_初始化DML.sql` 的演示账号密码是加密密文；实际环境请按项目 `.env` 和密码加密流程重新生成，不要把明文密码写入脚本。

当前业务表包括：`system_dictionary`、`organization_group`、`role`、`user_account`、`user_role`、`user_group_membership`、`report_template`、`report_template_item`、`weekly_report`、`monthly_plan`、`weekly_report_item`、`weekly_report_metric`、`weekly_report_evidence`、`system_attachment`。

`weekly_report_evidence` 保留通用链接/佐证记录；用户上传的实际文件统一写入系统通用附件表 `system_attachment`。附件通过 `attachment_type` 标识业务类型（当前周报接口固定写入 `weekly_report`），通过 `relation_id` 逻辑关联业务主记录（周报 ID），通过可选 `relation_sub_id` 逻辑关联业务子记录（周报任务 ID）。后续其他功能复用此表时，只需定义新的业务类型和对应的关联 ID，不需要再建一张业务专用附件表。文件实际存储根目录由 `.env` 的 `MEDIA_ROOT` 配置：填写相对路径时相对 `backend` 目录，填写 `/opt/dingchi-week-report/data/files` 这类绝对路径时直接使用宿主机目录；`ATTACHMENT_UPLOAD_DIR` 是相对于 `MEDIA_ROOT` 的分类子目录（默认 `weekly-report`）。因此默认文件路径为 `backend/media/weekly-report/{report_id}/...`，配置绝对根目录后则为 `/opt/dingchi-week-report/data/files/weekly-report/{report_id}/...`。表中同时保存 `storage_key`、访问地址、原始文件名、MIME 类型和字节大小。

周报任务列表字段使用 `system_dictionary` 管理：字典类型为 `weekly_report_fields_{role_code}`，`dict_code` 为字段编码，`dict_name` 为页面中文列名，`sort_order` 为展示顺序，`dict_value` 为默认展示标记（`1` 展示、`0` 隐藏）。目前已初始化交付专员和交互助理的 Excel 字段顺序；后续角色可按同一规则新增字典项。

本目录统一管理数据库 SQL（建表 DDL、初始化 DML 和删除脚本）。`backend/scripts/` 仅保留密钥生成、服务探测等可执行 Python 工具，不属于数据库脚本。
