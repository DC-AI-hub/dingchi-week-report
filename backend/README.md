# Backend

Django 6 + MCP 2 的 ASGI 后端，使用 MySQL 持久化、Redis 缓存，并通过 OpenAI-compatible SDK 调用大模型。

新增或重构后端代码必须遵守 [后端开发约束规范](docs/backend-development-conventions.md)，前后端接口还必须遵守仓库级 [API 对接规范](../docs/frontend-backend-api-conventions.md)。业务模块统一放在 `apps/<domain>/`，模块内部按 MVC、Service、DAO 和 Integration 分层；Django `views` 统一承担 HTTP 控制层职责，并通过 `apps/core/http.py` 返回统一 JSON 响应。

## 结构

```text
config/
├─ settings/            # base、development、production、test
├─ asgi.py              # Django 与 MCP 的统一 ASGI 入口
└─ urls.py              # /api 路由入口
apps/
├─ core/                # 通用响应、追踪中间件、认证和安全工具
├─ accounts/            # 登录、角色、用户、上下级和分组
├─ weekly_report/       # 模板、周报任务、指标、佐证和审核流程
├─ ai_gateway/          # AI 参数校验、服务层、HTTP 接口
└─ mcp_server/          # 统一 MCP Server，工具按 modules/<capability>/ 分层
```

横切能力说明：

- 所有 REST、MCP 和 WebSocket 请求统一生成/复用 `X-Trace-ID`，响应和滚动日志都会带上该值。
- 雪花主键通过 `apps/core/services/id_generator.py` 统一生成，配置项位于 `.env.*`。
- 页面密码使用 RSA-OAEP-SHA256 公钥加密；公钥接口为 `GET /api/v1/security/public-key/`，后端密码字段以 `rsa_oaep_sha256:` 前缀保存。
- 项目启动不会自动生成密钥或执行数据库迁移。首次开发需显式运行：

```powershell
python scripts/generate_crypto_keys.py
```

## 启动

```powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install -e ".[dev]"
python -m uvicorn config.asgi:application --reload --port 8000
```

不要用 `manage.py runserver` 作为完整项目入口，因为它不会承载顶层 Starlette 中的 MCP 生命周期。

项目启动不会自动执行数据库迁移。数据库变更必须单独审核并手动执行：

```powershell
python manage.py makemigrations
python manage.py migrate --plan
python manage.py migrate
```

首次初始化演示数据：

```powershell
mysql -uroot -p dingchi_week_report < scripts/seed_weekly_report.sql
```

## API 响应约定

成功：

```json
{"success": true, "data": {}}
```

失败：

```json
{"success": false, "error": {"code": "ERROR_CODE", "message": "错误说明"}}
```

## 周报与组织接口

- `POST /api/v1/auth/login/`、`GET /api/v1/auth/me/`、`POST /api/v1/auth/switch-role/`：登录、会话和角色切换。
- `GET /api/v1/dashboard/summary/`：按当前角色返回个人、团队或全量驾驶舱数据。
- `GET /api/v1/weekly-report-templates/{role_code}/`：获取角色模板任务和指标。
- `GET/POST /api/v1/weekly-reports/`、`GET/PATCH /api/v1/weekly-reports/{id}/`：查询、创建和编辑周报。
- `POST /api/v1/weekly-reports/{id}/submit/`、`POST /api/v1/weekly-reports/{id}/review/`：提交与审核。
- `GET /api/v1/users/`、`GET /api/v1/roles/`、`GET /api/v1/groups/`：总裁/系统管理员维护组织主数据。

角色范围为 `self`（本人）、`team`（本人及下属树）和 `all`（全量）。所有接口返回统一 JSON，并附带 `X-Trace-ID`；完整中文契约注释放在后端 `views.py` 与前端 feature `api.ts`。

## 环境配置

- 本地直接修改 `.env.development`；公共占位参考 `.env.example`；生产通过 `ENV_FILE` 指向 `.env.production.example` 的实际配置。
- 数据库和 Redis 连接必须使用连接池，连接池大小、超时和健康检查参数均在 `.env.*` 配置。
- MySQL 使用 `django-db-connection-pool` 的 SQLAlchemy `QueuePool` 适配器，池参数为 `MYSQL_POOL_*`；Redis 使用 `django-redis` 内置连接池。
- `.env.*` 中每个配置项均保留中文用途说明；禁止把系统配置、密钥或连接参数硬编码在代码中。

## 运行时烟雾测试

后端启动后执行：

```powershell
python scripts/smoke_test.py
```

脚本会验证 `/api/v1/health/live/`，并通过统一 `/mcp/` 端点列出工具、调用 `service_health`。

AI 接口当前为本地开发示例，生产使用前需补充认证、限流和审计。
