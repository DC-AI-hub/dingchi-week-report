# 后端开发约束规范

状态：强制执行  
适用范围：`backend/` 下所有新增、重构的后端代码  
技术栈：Python 3.12+、Django 6、ASGI、MCP 2、MySQL、Redis、OpenAI-compatible SDK

本文中的“必须”“禁止”为强制规则；“建议”为默认做法。用户明确要求与本文冲突时，
以用户要求为准，并在交付说明中记录偏离项。

## 1. 核心目标

1. 业务按模块组织，每个模块内部高内聚，模块之间低耦合。
2. 每个业务模块按 MVC 职责分层，并通过 Service、DAO、Integration 补充分层边界。
3. HTTP、MCP、任务脚本等入口复用同一业务服务，不重复实现业务规则。
4. 中间件、拦截器、认证、权限、路由、配置和公共工具具有唯一、明确的归属。
5. MySQL、Redis、AI 服务等基础设施通过适配层访问，不泄漏到 Django View。
6. 所有依赖保持单向，禁止循环引用和跨模块访问内部实现。

## 2. 标准目录结构

~~~text
backend/
├─ config/                              # Django/ASGI 装配与环境配置
│  ├─ settings/
│  │  ├─ base.py
│  │  ├─ development.py
│  │  ├─ production.py
│  │  └─ test.py
│  ├─ urls.py                           # REST 根路由，只挂载模块路由
│  ├─ asgi.py                           # Django、MCP、中间件和生命周期装配
│  └─ wsgi.py
├─ apps/
│  ├─ core/                             # 无业务语义的 Django/协议公共基础设施
│  │  ├─ authentication/                # 认证后端、凭证解析、身份上下文
│  │  ├─ permissions/                   # 跨模块通用权限原语
│  │  ├─ middleware/                    # 全局 Django/ASGI 中间件
│  │  ├─ security/                      # RSA 密码传输、解密与加密字段
│  │  ├─ interceptors/                  # 接口级装饰器、前后置拦截器
│  │  ├─ http.py                        # 统一 JSON 响应、异常和状态码映射
│  │  └─ services/                      # 健康检查等平台服务
│  ├─ mcp_server/                       # 统一 MCP Server、注册器及所有 MCP 工具
│  │  ├─ server.py                      # Server 实例与生命周期适配
│  │  ├─ registry.py                    # 功能模块工具统一注册
│  │  ├─ modules/                       # 按 MCP 功能模块拆分工具
│  │  │  └─ <capability>/
│  │  │     └─ tools.py                 # 当前功能的协议适配与工具定义
│  │  └─ tests/                         # MCP 工具测试
│  │     └─ <capability>/
│  │        └─ test_tools.py
│  └─ <domain>/                         # 一个业务边界，例如 weekly_report
│     ├─ apps.py
│     ├─ urls.py                        # 当前模块 REST 路由
│     ├─ public.py                      # 跨模块调用的稳定公开入口（按需）
│     ├─ models/                        # M：实体、值对象、约束
│     │  ├─ __init__.py
│     │  └─ <aggregate>.py
│     ├─ views/                         # Django HTTP 控制层
│     │  ├─ __init__.py
│     │  └─ <resource>.py
│     ├─ services/                      # 用例编排、事务和业务流程
│     │  └─ <use_case>.py
│     ├─ dao/                            # 数据访问对象：ORM 查询和持久化封装（按需）
│     │  ├─ <aggregate>.py
│     │  └─ sql/                         # 多表关联查询 SQL 脚本（按需）
│     │     └─ <query_name>.sql
│     ├─ integrations/                  # AI、外部 HTTP、消息等适配器（按需）
│     ├─ policies/                      # 当前业务模块的权限/业务策略（按需）
│     ├─ migrations/
│     ├─ management/commands/           # 需要 Django 上下文的运维命令（按需）
│     └─ tests/
│        ├─ models/
│        ├─ views/
│        ├─ services/
│        ├─ dao/
│        └─ integrations/
├─ utils/                               # 全局无业务语义的纯工具函数
│  └─ snowflake.py                      # 统一雪花主键生成算法
├─ scripts/                             # 本地开发、部署辅助和烟雾测试脚本
├─ docs/                                # 后端架构、接口和运维文档
├─ manage.py
└─ pyproject.toml
~~~

禁止为了结构完整创建空目录；只有出现对应职责的代码时才创建可选目录。

例如，当前功能可按以下方式归档：`modules/system/tools.py` 放置健康检查类工具，
`modules/ai/tools.py` 放置 AI 类工具；后续新增功能只在 `modules/<capability>/` 下扩展，
不把不同功能重新堆回 `server.py`。

### 2.1 项目启动与数据库迁移

- 项目启动入口（包括 ASGI、WSGI、本地启动脚本和容器入口）只能加载配置、装配应用和启动服务，
  **禁止自动执行** `makemigrations`、`migrate` 或任何建表/改表操作。
- 数据库迁移必须作为独立、显式、可审计的运维步骤执行，不得隐藏在启动命令、健康检查或应用导入中。
- 需要迁移时由开发者或部署流程明确执行并审核，例如：

~~~powershell
python manage.py makemigrations
python manage.py migrate --plan
python manage.py migrate
~~~

- 启动验证只执行 Django system check、测试或健康检查，不以自动迁移修复数据库结构。

## 3. Django 项目中的 MVC 映射

Django 的 View 函数或类本身就是 HTTP 请求控制入口，因此本项目不再额外建立
`controllers/`。在纯 JSON API 场景中统一采用以下映射：

| 职责 | 目录 | 说明 |
| --- | --- | --- |
| Model | `models/` | 数据实体、字段、关系、数据库约束和单实体不变量 |
| Controller | `views/` 或简单模块的 `views.py` | 接收 HTTP 请求、认证授权、调用 Service、返回 JSON |
| View representation | Django View + `apps/core/http.py` | 在控制层完成必要输入校验和输出映射，并生成统一 JSON Response |

前端页面是最终可视 View；后端不使用 Django Template 时，JSON 就是后端输出的 View
representation。简单请求参数、响应字段和序列化逻辑就近放在对应的 Django View 文件中，
不得为了几行字段定义创建固定的 `schemas/` 层；只有跨多个入口复用且明显变复杂时才单独
抽取类型模块。

Service、DAO、Integration 是 MVC 的辅助层：

- `services/` 承载业务用例和事务边界。
- `dao/` 封装 ORM 查询、数据库读写和持久化组合。
- `integrations/` 隔离 AI、第三方 HTTP、消息系统等外部服务 SDK。

小型模块允许使用单个 `views.py`；当接口按资源可独立命名、文件超过拆分阈值或存在多个
业务流程时，必须拆为 `views/<resource>.py`。无论文件还是目录形式，Django View 都只
承担控制层职责。

## 4. 依赖方向

模块内部依赖方向：

~~~text
urls
  ↓
views ──→ apps/core/http.py
  ↓
services ──→ policies
  ├─→ dao ──→ models
  └─→ integrations

mcp_server/modules/<capability>/tools ──→ apps/<domain>/public.py（公开 Service）

所有层均可按约束依赖 utils；上层禁止被下层反向依赖。
~~~

强制规则：

- Django View 可以依赖 Service、认证、权限和 `apps/core/http.py`；复杂类型应就近定义。
- Service 可以依赖当前模块的 Model、DAO、Integration、Policy 和领域类型。
- DAO 只能依赖当前模块的 Model、数据库能力和无业务工具。
- Integration 负责外部系统适配，禁止反向调用 Django View 或 MCP Tool。
- Model 禁止依赖 View、Service、DAO、Integration 或其他协议层。
- `apps/mcp_server/` 是 MCP 协议适配和工具实现的唯一归属；MCP Tool 只能依赖业务模块的
  `public.py` 或明确声明的公开 Service 接口，禁止导入业务模块的 View、DAO、Model、
  Integration 等内部实现。
- `mcp_server/server.py` 只负责 Server 实例和生命周期适配，`registry.py` 负责集中注册；
  功能模块不得各自创建 MCP Server 或绕过注册器挂载工具。
- MCP Tool 只能处理协议参数、认证上下文适配和公开 Service 调用，禁止依赖 Django View。
- 禁止使用延迟导入、动态导入或重新导出掩盖循环依赖。

## 5. 业务模块边界

- 一个 `apps/<domain>/` 必须对应一个清晰业务能力，不按数据库表或接口数量随意拆分。
- 模块自己的模型、服务、异常、权限策略和外部适配器全部留在模块内部。
- 另一个模块需要调用时，只能依赖目标模块的 `public.py` 或明确声明的公共 Service 接口。
- 禁止跨模块导入对方的 `views/`、`dao/`、`integrations/` 或内部 Model 实现。
- `apps/mcp_server/` 集中承载全部 MCP 工具，并在 `modules/<capability>/` 下按功能模块分层；
  业务模块不得新增 `mcp/` 目录或直接注册 MCP Tool。
- MCP 功能模块通过业务模块的公开 Service 接口复用业务能力，不得复制业务规则或直接访问
  业务模块内部层。
- 禁止跨模块直接复用对方内部 ORM 查询；数据库关系优先使用字符串形式声明模型引用。
- 两个模块共享的是业务概念时，应明确概念归属并由所有者模块公开能力，禁止复制代码。
- 只有真正无业务语义的能力才能提升到 `apps/core/` 或 `utils/`。
- `core`、`utils`、`common`、`helpers` 不得成为无法归类代码的堆放区。

## 6. Model 层规范

- 模型字段、关系、索引、唯一约束和检查约束必须显式定义。
- 金额、比例、时区、状态枚举等类型必须选择可保持精度和语义的字段。
- 表之间统一采用逻辑关联：禁止使用数据库外键约束、Django `ForeignKey`/`OneToOneField`/
  默认 `ManyToManyField` 生成物理关系，也禁止为关联字段创建外键索引。
- 逻辑关联使用明确的标量字段（例如 `user_id`、`report_id`）或显式中间表；关联完整性、
  删除策略和数据范围必须由 Service/DAO 校验，不依赖数据库外键级联。
- Model 可以维护单实体不变量和简单状态转换，禁止编排跨聚合业务流程。
- Model 禁止直接访问 HTTP 请求、Redis、AI SDK 或其他外部网络服务。
- 跨模型写操作和事务统一由 Service 层使用 `transaction.atomic()` 管理。
- 单表或简单过滤、排序、分页查询使用 Django ORM/Manager/QuerySet；查询不得散落在 Django View。
- 涉及两个及以上表的关联查询必须使用 DAO 管理的参数化 SQL 脚本，不得用 ORM 关系拼接替代。
- 单表列表查询仍必须检查 N+1、分页和必要的普通索引；关联字段的普通索引不得被当作外键约束。
- 模型变更必须生成迁移文件；禁止修改已在共享环境执行过的历史迁移。
- 谨慎使用 Django Signal。能由 Service 显式调用完成的业务流程，不得隐藏在 Signal 中。

## 7. Django View 输入输出规范

- 简单请求参数、类型、长度、枚举和格式校验直接写在对应的 Django View 文件中。
- 简单响应字段映射和序列化也直接写在 View 中，并通过 `apps/core/http/` 的公共函数返回。
- 当请求/响应类型跨多个入口复用且明显变复杂时，才在业务模块内抽取语义明确的类型文件；
  不创建固定的 `schemas/` 层作为模板目录。
- View 不得接收或返回包含秘密字段的未筛选 ORM 对象。
- View 禁止发送数据库查询、访问缓存、调用外部 SDK 或编写核心业务决策。
- HTTP 与 MCP 共用同一业务结果时，应复用 Service 返回的领域结果，不复制业务转换逻辑。
- 所有外部输入先按不可信数据处理，完成类型收窄和边界校验后再传给 Service。
- 所有 HTTP 响应必须通过 `apps/core/http.py` 的公共函数生成，不得在各业务模块自行定义响应包络。

## 8. Django View 控制层规范

Django View 只允许执行以下工作：

1. 接收 `HttpRequest` 并读取已由认证层建立的身份上下文。
2. 执行接口级权限、限流、幂等和审计拦截器。
3. 完成必要的请求结构校验。
4. 调用一个明确的业务 Service 用例。
5. 将已知领域异常交给统一异常映射。
6. 使用统一响应函数返回 `JsonResponse`。

Django View 禁止：

- 直接调用 ORM、Redis、AI SDK 或第三方 HTTP SDK。
- 编写事务、复杂循环、领域计算或跨模块业务规则。
- 捕获 `Exception` 后静默返回成功。
- 在每个接口重复认证、响应包络、日志和耗时统计代码。
- 直接把异常堆栈、内部路径、配置或密钥返回给客户端。
- 返回未经过字段白名单处理的 ORM 对象。

单个 View 函数超过 80 行、调用两个以上独立业务流程或包含三个以上业务分支时，必须
把业务编排下沉到 Service，不能继续扩展入口函数。

## 9. Service、DAO 与 Integration

### 9.1 Service

- 一个公开 Service 函数或类方法对应一个可命名的业务用例。
- Service 是事务边界、幂等控制和跨实体业务规则的主要承载层。
- Service 不得依赖 `HttpRequest`、`JsonResponse`、MCP Session 等协议对象。
- 同一用例被 HTTP、MCP、管理命令或后台任务调用时，必须复用同一 Service。
- 业务失败使用语义明确的领域异常，禁止使用布尔值或字符串暗示失败原因。

### 9.2 DAO

- DAO（Data Access Object）是业务模块连接 MySQL/Django ORM 的唯一入口。
- 单表或简单查询使用 Django ORM/Manager/QuerySet；Service 不得直接执行 ORM 或 SQL。
- 多表关联查询必须在 `dao/sql/<query_name>.sql` 中维护参数化 SQL 脚本，并由 DAO 统一加载和执行；
  禁止在 Python 字符串中拼接 SQL，禁止在 View 或 Service 中直接执行 SQL。
- DAO 方法名必须表达数据访问意图，例如 `find_pending_reports`、`save_report`。
- DAO 只负责查询、持久化、批量读写和数据库锁，禁止编写业务决策、HTTP 响应或权限判断。
- DAO 不得调用 Redis、AI SDK、第三方 HTTP 或 MCP。
- 批量读取和写入必须明确性能、锁和事务策略；事务边界由 Service 管理。

### 9.3 Integration

- 每个外部提供方必须有独立适配器，业务 Service 依赖本地接口而不是 SDK 具体响应对象。
- 超时、重试、并发限制和提供方错误映射必须集中处理。
- 重试只用于安全或具备幂等保证的操作，并设置次数上限和退避策略。
- 外部客户端应复用连接，并在 ASGI 生命周期结束时正确关闭。
- 单元测试必须替换外部适配器，禁止真实请求 AI 或第三方生产服务。

## 10. 公共 utils 规范

- 全局公共工具统一放在 `backend/utils/`，该目录必须是可导入的 Python 包。
- `utils` 只放无状态、无业务语义、可独立测试的函数，例如 ID、时间、脱敏和通用编码工具。
- `utils` 禁止导入 `apps` 中的 Model、Service、Django View 或业务常量。
- 依赖 Django 请求、响应、认证或 ORM 的公共能力放在 `apps/core/`，不放入 `utils`。
- 只被一个业务模块使用的工具留在该模块内部，禁止过早提升为全局工具。
- 文件必须按能力命名，例如 `identifiers.py`、`datetime.py`、`masking.py`；禁止新增含糊的 `common.py`、`helpers.py` 或 `misc.py`。

## 11. 中间件与拦截器规范

### 11.1 中间件

- 全局 Django/ASGI 中间件放在 `apps/core/middleware/`，并在 `config/settings/base.py` 或 `config/asgi.py` 统一装配。
- 中间件用于每个请求都需要的横切能力，例如 Request ID、安全响应头、统一日志、耗时统计和全局异常兜底。
- 中间件必须保持轻量，不得查询业务模型、执行领域流程或调用 AI 服务。
- 中间件顺序必须显式维护并有注释说明依赖关系；认证、CORS、CSRF、异常处理等顺序不得随意调整。
- 同一请求只能生成一个 Request ID，并在响应头和日志上下文中复用。
- 中间件不得吞掉异常。可处理的已知异常映射后返回，未知异常必须记录并交由统一错误策略处理。
- ASGI 中间件禁止执行阻塞 I/O；同步 Django ORM 不能直接在异步中间件中调用。

### 11.2 拦截器

- 仅特定接口需要的前后置逻辑放在 `apps/core/interceptors/`，例如接口级限流、幂等键、权限声明和审计事件。
- 拦截器必须可组合、职责单一，并保留原函数元数据。
- 拦截器只处理横切规则，不得包含某个业务模块的核心判断。
- 业务专属前置条件放在所属模块的 `policies/` 或 Service 中。
- 禁止在 Django View 中复制粘贴相同的认证、限流、幂等或审计代码。

## 12. 认证与权限规范

### 12.1 认证

- 认证只负责确认调用者身份并建立认证上下文，不负责业务授权。
- 通用认证后端、Token/Cookie/API Key 解析放在 `apps/core/authentication/`。
- 用户、组织、角色等业务实体属于明确的身份业务模块，不得全部堆入 `core`。
- 除健康检查、登录/刷新等明确公开接口外，新增接口默认要求认证；公开接口必须显式标记。
- 页面密码必须先使用统一 RSA-OAEP-SHA256 公钥加密后传输，数据库凭证字段必须使用统一加密字段保存版本化密文；禁止明文保存、明文日志或绕过统一安全工具。
- Token 必须校验签名、过期时间、签发方和适用范围；需要撤销能力时定义明确策略。
- MCP 认证策略必须与部署方式一致，并在 `/mcp` 挂载处统一接入，不能由每个工具自行解析凭证。
- 凭证、Cookie、Authorization Header、API Key 和完整 Token 禁止写入日志。

### 12.2 权限

- 权限判断必须发生在业务 Service 调用之前，但领域不变量仍由 Service/Policy 保证。
- 跨模块通用权限原语放在 `apps/core/permissions/`，业务权限规则放在 `apps/<domain>/policies/`。
- 认证失败与权限不足必须区分，分别映射为 401 和 403。
- 列表和详情查询必须同时应用数据范围权限，禁止只隐藏前端入口。
- 后台管理、普通用户、服务账号和 MCP 调用方必须采用最小权限原则。
- 权限默认拒绝；缺少明确允许规则时不得放行。

## 13. 路由规范

### 13.1 REST 路由

- 根路由只在 `config/urls.py` 挂载各模块，不编写业务处理逻辑。
- REST API 统一使用 `/api/` 前缀；当前版本统一位于 `/api/v1/`。
- 每个业务模块在自己的 `urls.py` 注册路由，并设置唯一的 `app_name` 和 route name。
- URL 使用小写、连字符和名词资源形式；动作语义优先由 HTTP Method 表达。
- 同一资源的尾部斜杠策略必须一致，不得同时维护两套地址。
- Django View 通过模块 `urls.py` 暴露，其他模块禁止直接引用其路由实现。
- 破坏兼容性的接口变更必须升级 API 版本，禁止静默改变既有响应字段语义。

### 13.2 MCP 路由

- MCP 统一挂载在 `/mcp/`，挂载和 Session 生命周期只在 `config/asgi.py` 装配。
- 所有 MCP 工具必须放在 `apps/mcp_server/modules/<capability>/`，按功能模块分层管理；
  不得在 `apps/<domain>/mcp/` 或其他业务目录实现工具。
- `apps/mcp_server/registry.py` 统一汇总并注册各功能模块工具，`server.py` 不承载具体业务工具
  实现；`config/asgi.py` 只负责挂载 `/mcp/` 和生命周期，不直接注册工具。
- MCP Tool 只做参数描述、认证上下文适配和公开 Service 调用，禁止复制 REST View 的业务逻辑。
- MCP 使用 Streamable HTTP 协议时，客户端访问统一的 `/mcp/` 端点并通过协议调用工具，
  不为每个工具额外创建 `/mcp/<tool>` REST 地址。
- Tool 名称、输入结构、输出结构和错误语义必须稳定且可测试。
- 新增 Tool 必须在 `apps/mcp_server/tests/<capability>/` 同时测试工具发现、参数校验、
  认证策略和实际调用。

## 14. 配置规范

- `config/` 只负责 settings、根路由、ASGI/WSGI、日志和应用生命周期装配，禁止放业务规则。
- 公共设置放 `config/settings/base.py`，环境差异分别放 development、test、production。
- 所有系统配置、密钥、密码、域名、连接参数和环境差异必须通过对应的 `.env.*` 文件注入，
  禁止在 Python、启动脚本或容器编排文件中硬编码配置值。
- 新增环境变量必须同步更新 `.env.example` 和相关环境占位文件。
- `.env.example` 只放安全占位值，真实生产密钥不得写入代码库；每个配置项前必须有中文注释，
  说明用途和格式，数值类配置注明单位，必填项明确标记。
- 配置读取应集中进行并提供类型转换；必填配置缺失时必须明确启动失败，不得用代码默认值静默掩盖。
- 生产环境禁止使用开发默认密钥、调试模式或宽泛的 Host/CORS 配置。

### 14.1 数据库与 Redis 连接池

- MySQL 数据库连接和 Redis 连接必须通过连接池获取；禁止在请求、Service、DAO 或工具函数中
  为单次操作临时创建和销毁连接。
- 连接池的最小/最大连接数、获取超时、空闲回收、健康检查、重试和生命周期参数必须通过 `.env.*`
  配置，并在环境文件中使用中文注释说明。
- Django 的 MySQL 适配器必须选用支持连接池的实现；`CONN_MAX_AGE` 只能用于连接复用，
  不能替代连接池能力。
- Redis 必须使用 `django-redis`/redis-py 的连接池配置；业务代码只能通过统一缓存适配器访问。
- 应用关闭时必须释放连接池；连接池耗尽、连接失效和上游不可用必须有超时与降级策略。

## 15. 脚本与管理命令规范

- `scripts/` 只放本地开发、部署辅助、服务探测和跨应用烟雾测试脚本。
- 需要 Django ORM、事务或业务 Service 的运维操作，优先实现为所属模块的 Django management command。
- 脚本和命令必须复用 Service，禁止复制生产业务逻辑。
- 脚本必须提供明确入口、参数说明、退出码和错误输出，禁止 import 时自动执行。
- 可能修改大量数据的命令必须提供确认机制或 `--dry-run`，并设计为可重复执行或明确说明幂等边界。
- 运行时应用代码禁止反向导入 `scripts/`。
- 临时一次性脚本在任务完成后删除或提升为正式管理命令，不得长期堆积。

## 16. MySQL 与事务规范

- MySQL 是持久化业务事实的默认唯一来源。
- 所有 MySQL 连接必须从统一连接池获取，禁止在 View、Service、DAO 或脚本中自行创建连接。
- 所有写流程必须明确事务边界；事务放在 Service，不放在 Django View。
- 事务中禁止执行耗时 AI/HTTP 调用；必须先缩短锁持有时间，再通过状态机或补偿机制衔接外部调用。
- 并发更新必须明确采用唯一约束、条件更新、版本号或行锁策略。
- 用户输入不得拼接原生 SQL；多表关联只能通过 DAO 加载参数化 SQL 脚本，脚本必须说明查询用途和参数。
- 批量任务必须分页或分批，禁止一次加载全部业务数据。
- 时间统一使用 Django timezone-aware 值，数据库字符集保持 `utf8mb4`。

## 17. Redis 规范

- Redis 只用于缓存、分布式锁、限流或可丢弃的临时状态，不得作为关键业务事实唯一来源。
- Redis 客户端必须使用连接池；连接池大小、超时、健康检查和重试参数统一从 `.env.*` 注入。
- 缓存访问放在 Service 或专用缓存适配器中，Django View 和 DAO 不得直接操作 Redis。
- Key 必须集中构造并包含应用、环境、模块、用途、标识和版本，例如 `dwr:dev:report:detail:42:v1`。
- 每个缓存项必须明确 TTL、序列化格式、失效策略和数据源。
- 数据写入成功后必须执行对应缓存删除或刷新，禁止依赖 TTL 偶然恢复一致性。
- 分布式锁必须设置超时和所有者标识，只允许所有者释放；不得使用无过期时间的锁。
- Redis 不可用时是降级还是失败必须由场景明确决定，并通过配置和测试覆盖。

## 18. AI 大模型调用规范

- AI SDK 只能出现在 AI 所属模块的 `integrations/` 或专用网关适配器中。
- 业务层依赖本地接口和结果 DTO，禁止把提供方响应对象传到 Django View。
- 模型、Base URL、密钥、超时等全部通过配置注入。
- 请求必须限制消息数量、单条长度和总长度；输出也必须设置合理上限。
- 对外部错误、超时、限流、空结果和配置缺失分别映射稳定错误类型。
- 日志不得包含密钥和完整敏感 Prompt；确需审计时先脱敏并遵守数据保留策略。
- 具备副作用的 AI 调用不得盲目自动重试。
- 流式响应与非流式响应必须使用不同、清晰的 View/响应契约。

## 19. API 响应与异常规范

成功响应：

~~~json
{"success": true, "data": {}}
~~~

失败响应：

~~~json
{"success": false, "error": {"code": "ERROR_CODE", "message": "错误说明"}}
~~~

- Django View 必须通过 `apps/core/http.py` 的统一方法生成 JSON 响应。
- 错误 `code` 使用稳定的大写下划线格式，不以异常类名或临时文案充当错误码。
- 领域异常由统一映射层转换为 HTTP/MCP 错误，Django View 不重复解析。
- 4xx 表示调用方输入、认证或权限问题；5xx 表示服务端或上游依赖问题。
- 未知异常必须记录 Request ID 和堆栈，对外只返回安全通用文案。
- 禁止在成功响应中夹带失败状态，或对所有异常统一返回 HTTP 200。

## 20. 异步与 ASGI 规范

- 仅在存在真实并发 I/O 收益时使用异步 View/Service。
- 异步路径禁止直接执行同步 ORM、文件 I/O 或阻塞 SDK；必须使用异步能力或安全适配。
- HTTP 与 MCP 共用的异步客户端在 ASGI lifespan 中创建和关闭。
- 禁止为每次请求新建可复用的 AI、Redis 或 HTTP Client。
- 后台长任务不得占用请求生命周期，应使用明确的任务机制；未引入任务系统前不得伪造“后台执行”。
- 完整服务入口使用 `config.asgi:application`，确保 MCP 生命周期正常运行。

## 21. 日志、审计与安全

- 使用模块级 logger 和结构化上下文字段，至少包含 Request ID、模块、动作和结果。
- 禁止使用 `print()` 记录运行时日志。
- 禁止记录密码、Token、Cookie、密钥、完整 Authorization Header 和敏感业务原文。
- 安全相关操作和关键写操作必须留下可追踪审计事件；审计失败策略由业务风险决定。
- CORS、CSRF、Allowed Hosts 和安全响应头必须在配置或中间件层统一处理。
- 所有输入执行长度、类型、格式和允许值校验；文件输入还必须校验大小、扩展名与实际内容。
- 错误信息不得泄漏数据库结构、内部路径、堆栈或提供方秘密。

## 22. 命名与文件拆分

| 对象 | 规则 | 示例 |
| --- | --- | --- |
| 业务模块目录 | snake_case 业务名词 | `weekly_report` |
| Model | 单数 PascalCase | `WeeklyReport` |
| Service 用例 | 动词开头 | `create_report`、`submit_report` |
| Django View | 动词或资源动作 | `list_reports`、`create_report` |
| DAO 方法 | 业务语义名称 | `find_pending_reports`、`save_report` |
| URL name | 模块内唯一 kebab-case | `report-detail` |
| 数据库表名 | 小写 snake_case，不使用驼峰或连字符 | `weekly_reports` |
| 数据库字段名 | 小写 snake_case，不使用驼峰或连字符 | `created_at`、`user_id` |
| 环境变量 | 必须下划线开头，主体使用小写 snake_case | `_ai_timeout_seconds` |
| 系统/全局变量 | 必须下划线开头，主体使用小写 snake_case | `_database_url`、`_ai_model` |
| 局部/临时变量 | 必须字母开头，使用小写 snake_case | `report_items`、`tmp_result` |
| 错误码 | 大写下划线 | `REPORT_NOT_FOUND` |

命名强制规则：

- 表名和字段名统一使用小写字母与下划线；关联字段使用明确的逻辑标识命名，例如 `<entity>_id`，
  不使用数据库外键类型或隐式关系命名。
- 系统变量、环境变量和模块级/全局变量必须以 `_` 开头，后续使用小写 snake_case；
  局部变量和临时变量必须以字母开头，禁止使用无语义的单字母（循环索引除外）。
- 新增环境变量的 `.env.*` 键名、配置读取标识和文档示例必须保持同一命名规则；已有兼容键只有在迁移
  方案明确后才能调整。

满足以下任一条件时必须拆分：

1. 单个函数超过 50 行。
2. Django View 函数超过 80 行。
3. 单个文件超过 300 行且包含两个以上独立职责。
4. 同一文件同时出现协议解析、ORM 查询、业务规则和外部 SDK 调用中的两项以上。
5. 同一逻辑在 HTTP、MCP、脚本或另一个模块中第二次出现。

禁止新增 `common.py`、`helpers.py`、`misc.py`、`service.py` 等含义宽泛且持续膨胀的文件。

## 23. 测试规范

- Model 测试覆盖约束、状态转换和关键 QuerySet。
- Service 测试覆盖正常流程、边界、权限策略、事务回滚和幂等。
- Django View 测试覆盖认证、权限、参数、状态码和统一 JSON 响应结构。
- Middleware/Interceptor 测试覆盖执行顺序、短路行为、异常传播和上下文清理。
- DAO 测试关注真实数据库查询行为和查询数量。
- Integration 测试使用 Mock/Fake，默认禁止调用真实 AI 或第三方生产服务。
- MCP 测试统一放在 `apps/mcp_server/tests/<capability>/`，必须覆盖工具列表、参数校验、
  认证策略和工具调用结果。
- 每个缺陷修复必须补充能在修复前失败的回归测试。
- 测试不得依赖执行顺序、开发数据库或开发 Redis。

标准验证命令：

~~~powershell
python -m ruff check .
python -m pytest
python manage.py check --settings=config.settings.test
~~~

涉及模型变更时额外执行：

~~~powershell
python manage.py makemigrations --check --dry-run
~~~

## 24. 新业务模块实施流程

1. 明确模块业务边界、所有者和对外能力。
2. 创建 `apps/<domain>/`，只建立本次需要的目录。
3. 定义 Model、约束和迁移。
4. 定义请求/响应 View 与领域错误。
5. 实现单一业务用例 Service，并确定事务边界。
6. 仅在查询或外部依赖复杂时增加 DAO、Integration。
7. 实现薄 Django View，接入认证、权限和必要拦截器。
8. 在模块 `urls.py` 注册路由，再由 `config/urls.py` 挂载。
9. 提供 MCP 能力时，在 `apps/mcp_server/modules/<capability>/` 新增工具适配，让其复用业务
   模块公开 Service，并通过 `registry.py` 由统一 Server 注册。
10. 新增环境变量时同步占位配置。
11. 按层级补齐测试并执行完整验证。

## 25. 完成定义

- [ ] 业务代码位于明确的 `apps/<domain>/`，模块边界清晰。
- [ ] Model、Django View、Service、DAO 职责分离，View 未直接操作 ORM、Redis 或外部 SDK。
- [ ] Service 承载业务用例和事务，HTTP/MCP/脚本入口没有重复业务逻辑。
- [ ] 跨模块调用只依赖对方公开入口，没有导入内部实现。
- [ ] 所有 MCP 工具均位于 `apps/mcp_server/modules/<capability>/`，没有业务模块内的 `mcp/`。
- [ ] 中间件、拦截器、认证、权限和路由位于规范目录并保持职责单一。
- [ ] 新增接口默认认证，公开接口显式声明；认证与权限失败分别返回 401、403。
- [ ] REST 和 MCP 路由分别保持 `/api`、`/mcp` 前缀。
- [ ] 公共纯工具、脚本和配置分别位于 `utils/`、`scripts/`、`config/`。
- [ ] MySQL 和 Redis 均通过连接池访问，连接池大小、超时和健康检查来自 `.env.*`。
- [ ] 系统配置均来自 `.env.*`，每个配置项有中文注释，代码和脚本没有硬编码配置值。
- [ ] MySQL 事务、Redis TTL/失效策略和外部调用边界明确。
- [ ] 密钥、凭证和环境差异没有硬编码或写入日志。
- [ ] 超时、空结果、依赖失败和未知异常均有明确处理。
- [ ] Ruff、Pytest 和 Django system check 通过。
- [ ] 涉及 Model 时迁移文件与迁移检查通过。
- [ ] 文档、环境变量示例和接口契约已同步更新。

## 26. 强制安全基础设施实现

### 26.1 请求追踪与滚动日志

- 所有 HTTP、WebSocket 和 `/mcp/` 请求必须经过 `apps/core/middleware/trace_id.py`；ASGI
  入口负责覆盖所有挂载，Django middleware 负责 WSGI/测试入口。
- 请求携带合法 `X-Trace-ID` 时必须原样复用；缺失或格式非法时由服务端生成安全的随机值。
  响应必须返回同名 `X-Trace-ID`，日志上下文必须包含同一值。
- 统一日志使用 `logging.handlers.RotatingFileHandler`，日志目录、文件名、级别、单文件大小、
  历史文件数量和是否输出控制台全部从 `.env.*` 读取；代码禁止写死这些运行参数。
- 日志默认 UTF-8 编码，禁止记录密码明文、RSA 密文、私钥、公钥文件内容、Token、Cookie 和完整
  Authorization Header；异常堆栈也必须经过敏感信息审查。

### 26.2 雪花主键

- 新建业务模型的主键必须使用 `apps/core/services/id_generator.py` 的
  `generate_primary_id()`，底层实现位于无业务语义的 `utils/snowflake.py`。
- 业务模型可继承 `apps/core/models/base.py` 的 `SnowflakeIdModel`，以复用统一的 `id`
  字段；模型不得自行声明另一套主键生成策略。
- 禁止使用数据库自增、UUID 或随机字符串作为新业务表主键；雪花算法使用 64 位有序整数，
  `worker_id` 与 `datacenter_id` 必须通过 `.env.*` 唯一配置，实例间不得冲突。
- 时钟回拨必须显式失败并告警，禁止静默生成可能重复的 ID；序列耗尽时等待下一毫秒。

### 26.3 RSA 密码传输与存储

- 统一算法为 `RSA-OAEP-SHA256`。前端只能调用 `shared/security/password.ts` 的
  `encryptPassword()`，先通过 `/api/v1/security/public-key/` 获取公钥，再把密文放入请求体；
  页面和 feature API 不得自行实现 RSA 或直接传输密码明文。
- 后端只能通过 `apps/core/security/` 的统一工具解密客户端密文；明文只允许短暂存在于请求处理
  内存中，数据库字段必须使用 `EncryptedPasswordField`、
  `encrypt_client_password_for_storage()` 或 `encrypt_password_for_storage()` 保存带
  `rsa_oaep_sha256:` 版本前缀的密文。
- RSA 私钥只能由 `CRYPTO_PRIVATE_KEY_PATH` 和 `CRYPTO_PRIVATE_KEY_PASSWORD` 注入服务端，
  不得进入前端环境变量、Git、接口响应或日志。公钥也不得硬编码，接口未配置密钥时返回明确
  的 `CRYPTO_NOT_CONFIGURED` 错误。
- 密钥生成必须由 `python scripts/generate_crypto_keys.py` 显式执行，禁止在项目启动、健康检查或
  请求处理中自动生成/覆盖密钥；密钥轮换时必须保留算法版本和兼容迁移方案。
- HTTPS 仍是生产环境的强制传输层保护；RSA 是应用层保护，不能替代 TLS、认证、限流和审计。

## 27. 前后端 API 对接契约

前后端只依赖版本化 API 契约，不依赖对方内部实现：后端不关心 Vue 页面、组件和 CSS，前端不关心
Django View、Service、DAO、Model、SQL 和数据库表。详细协作规则统一维护在
`docs/frontend-backend-api-conventions.md`。

- 每个 REST 接口必须在路由/View 旁写中文 docstring 或引用契约文档，至少说明：用途、HTTP 方法和
  完整路径、认证/权限/幂等、请求参数位置与类型、必填性/默认值/范围/枚举/单位、响应字段类型和
  示例、错误状态码/错误码、`X-Trace-ID` 和兼容性。
- 接口只返回前端完成业务所需的稳定 JSON 数据，必须通过白名单/映射组装，禁止直接序列化 ORM、
  Model、数据库列全集或内部异常；统一使用 `apps/core/http.py` 的成功/失败包络。
- 64 位 Snowflake ID 在 JSON 中必须序列化为字符串；时间使用带时区的 ISO 8601，分页、空值、金额、
  比例和时长的语义必须在中文注释中明确。
- 新增/修改接口时先更新契约和契约测试，再分别实现后端 View/Service 与前端 feature API；破坏性
  修改必须升级 API 版本，新增字段、错误码和弃用计划同步两端文档。
- 后端不得把页面设计要求、组件名称或 UI 文案写进业务接口；前端不得根据数据库字段、内部异常或
  后端目录推断接口行为。
