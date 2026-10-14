# 数据库脚本说明

本目录保存当前周报系统的手工 SQL 脚本，表结构与 `backend/apps/**/models.py` 及 Django 内置组件保持一致。

## 文件

| 文件 | 用途 |
| --- | --- |
| `01_建表DDL.sql` | 创建当前项目已知的业务表和 Django 框架表。所有建表语句均为 `CREATE TABLE IF NOT EXISTS`，已有表不会被覆盖。表名、字段名均使用下划线命名，并为表和每个字段提供中文注释。 |
| `02_初始化DML.sql` | 唯一的系统配置初始化脚本，包含字典、组织、角色、用户、周报模板及模板字段；执行时先清空配置表，再重新插入，可重复执行，不初始化或清理周报、月度计划等业务数据。 |
| `03_查询所有表.sql` | 只读查询脚本：先查询当前数据库的表名、表注释和估算行数，再逐表查询业务表及 Django 框架表数据。 |
| `04_统一周报任务状态.sql` | 已初始化数据库的增量脚本：移除废弃的 `weekly_report_item.item_status` 字段，任务状态统一使用 `on_time_status`。 |
| `05_新增用户手机号字段.sql` | 已初始化数据库的增量脚本，为 `user_account` 增加手机号字段；新库的 `01_建表DDL.sql` 已直接包含该字段。 |
| `06_新增每日工作任务表.sql` | 已初始化数据库的增量脚本，新增周报日报表；按周报 ID 和日期唯一约束，一个周报每天只能填写一条日报。 |
| `99_删除所有表.sql` | 删除本项目当前已知的全部业务表和 Django 框架表。脚本会删除数据，执行前必须确认数据库和备份。 |

## 推荐执行顺序

在已经创建好的 MySQL 数据库中按以下顺序执行：

```text
01_建表DDL.sql
02_初始化DML.sql
```

如果数据库已经按当前 DDL 创建，请额外执行 `06_新增每日工作任务表.sql`；如果手机号字段尚未存在，再执行 `05_新增用户手机号字段.sql`。项目启动不会自动执行这些结构变更。

项目启动不会自动执行表迁移或初始化脚本。生产环境仍建议使用 Django migration 作为唯一的结构变更来源；手工 DDL 主要用于本地初始化、交付或需要纯 SQL 的环境，不要在同一套空库上重复混用两套建表流程。

新库使用完整 DDL；已有库使用对应增量脚本，避免重复执行增列语句。

## 设计约束

- 业务表主键统一使用应用层雪花算法生成的 `BIGINT`，不会设置 `AUTO_INCREMENT`。
- 日期时间字段统一使用 `DATETIME(6)`；日期周期字段使用 `DATE`。日期时间字段不使用 `BIGINT`，也不使用 `DEFAULT 0`。
- 业务表的用户、角色、分组、模板、周报等关系均使用逻辑 ID/编码，不创建数据库外键；这样与现有跨模块解耦规范一致。
- Django 自带的 `auth`、`contenttypes`、`admin`、`sessions`、`migrations` 表保留框架必需的外键和索引，它们不属于业务关联设计。
- `02_初始化DML.sql` 的演示账号密码是加密密文；实际环境请按项目 `.env` 和密码加密流程重新生成，不要把明文密码写入脚本。

当前业务表包括：`system_dictionary`、`organization_group`、`role`、`user_account`、`user_role`、`user_group_membership`、`report_template`、`report_template_item`、`weekly_report`、`monthly_plan`、`monthly_plan_task`、`weekly_report_item`、`weekly_report_metric`、`system_attachment`、`weekly_report_daily_task`。

文档链接保存在周报任务的 `document_links` 字段；用户上传的实际文件统一写入系统通用附件表 `system_attachment`。附件通过 `attachment_type` 标识业务类型（当前周报接口固定写入 `weekly_report`），通过 `relation_id` 逻辑关联业务主记录（周报 ID），通过可选 `relation_sub_id` 逻辑关联业务子记录（周报任务 ID）。后续其他功能复用此表时，只需定义新的业务类型和对应的关联 ID，不需要再建一张业务专用附件表。文件实际存储根目录由 `.env` 的 `MEDIA_ROOT` 配置：填写相对路径时相对 `backend` 目录，填写 `/opt/dingchi-week-report/data/files` 这类绝对路径时直接使用宿主机目录；`ATTACHMENT_UPLOAD_DIR` 是相对于 `MEDIA_ROOT` 的分类子目录（默认 `weekly-report`）。因此默认文件路径为 `backend/media/weekly-report/{report_id}/...`，配置绝对根目录后则为 `/opt/dingchi-week-report/data/files/weekly-report/{report_id}/...`。表中同时保存 `storage_key`、访问地址、原始文件名、MIME 类型和字节大小。

周报任务列表字段使用 `system_dictionary` 管理：字典类型为 `weekly_report_fields_{template_code}`（模板编码含版本号），`dict_code` 为字段编码，`dict_name` 为页面中文列名，`sort_order` 为展示顺序，`dict_value` 为默认展示标记（`1` 展示、`0` 隐藏）。目前已初始化交付专员、交付助理、招聘、ITO 销售和创新业务销售模板的 Excel 字段顺序；后续模板版本可按同一规则新增独立字典项。

周报任务明细只保留 `on_time_status` 一个状态字段，允许值为 `pending`（待完成）、`in_progress`（进行中）、`on_time`（按时完成）、`late`（延期完成）、`overdue`（逾期未完成）、`not_applicable`（不适用）和 `completed`（已完成）。`item_status` 已废弃，后端查询、保存、统计和前端展示均不再读取或写入该字段。

本目录统一管理数据库 SQL（建表 DDL、初始化 DML 和删除脚本）。`backend/scripts/` 仅保留密钥生成、服务探测等可执行 Python 工具，不属于数据库脚本。
### 每日工作任务

`06_新增每日工作任务表.sql` 新增周报日报表 `weekly_report_daily_task`。该表使用 `report_id` 与周报逻辑关联，按 `report_id + work_date` 唯一约束保证一个周报每天只能有一条日报；执行现有建表脚本后再执行本文件即可。

### 月度计划任务

`07_新增月度计划任务表.sql` 仅新增独立的 `monthly_plan_task` 明细表。
同一员工、角色、月份共用列表，填写客户与工作任务，与月度目标和周任务分别存储。
接口及保存规则见 `../monthly-plan-tasks-api.md`。

`08_月度计划新增客户.sql` 用于已建表环境增加客户名称字段，历史记录保留，客户默认空。
新建环境的完整 DDL 和 `07_新增月度计划任务表.sql` 已包含该字段，不要重复执行增列脚本。

`09_月度计划新增维度.sql` 用于已建表环境增加招聘计划维度字段，客户与维度独立存储。

`10_月度计划客户维度允许为空.sql` 调整客户与维度列允许 NULL，模板必填规则由代码校验。

`11_月度计划合并客户维度.sql` 将历史客户／维度两列合并为唯一可空字段 `scope_name`。
新建环境直接执行最新完整 DDL 或 07 脚本，不执行历史 08–11 增量脚本。

### 月度计划管理及审批

`12_月度计划审批管理.sql` 为已执行11的数据库增加直属上级顺序表、通用审批单、
审批节点和月度计划变更历史，并给计划主表增加状态、模板、版本和驳回原因。
保留现有计划为草稿，旧直属上级迁入排序0；不会把已有计划自动设为审批通过。
完整DDL、查询及删除脚本已同步，API见 `../monthly-plan-management-api.md`。
所有关联为逻辑关联；客户／维度仍共用一个可空字段 `scope_name`。

13_月度计划变更子流程.sql：增加独立变更申请表。存量升级需执行 Django 0010/0011 迁移，0011 恢复最后已通过的主流程并保留未完成申请及审批记录。不要同时重复执行建表脚本与建表迁移。

`14_通用待办提醒.sql` 增加通用待办表；已读时间与业务完成时间独立，按接收人+业务键去重。完整 DDL、查询、删除脚本同步；接口和提醒生成规则见 `../todos-api.md`。Django 部署显式执行 todos.0001_initial，不与 SQL 建表重复执行。

`15_待办及审批角色隔离.sql`：旧版14环境增加待办所属角色、审批节点处理角色，并调整去重键和索引。同步回填参见 approvals.0003/todos.0003；保留已读标记。新建环境直接用最新完整DDL。
