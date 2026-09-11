---
name: frontend-development-conventions
description: "在 Vue 3、TypeScript 与 Vite 6 前端中新增、重构或审查页面时，应用模块化视图、组件、组件分类、样式拆分、状态、API、路由和校验规范。仅用于明确采用本规范的前端项目，不用于后端或其他前端框架。"
---

# Vue 前端开发规范

按照项目约束完成 Vue 前端页面新增、重构或代码审查，使目录、依赖、组件职责和验证结果保持一致。

## 开始前

1. 确认目标是 Vue 3、TypeScript、Vite 6 项目，或用户明确要求采用本规范。
2. 查找并阅读目标目录及其父目录中的 `AGENTS.md` 等项目级指令。
3. 完整阅读 [references/frontend-development-conventions.md](references/frontend-development-conventions.md)，再检查目标项目现有目录、路由、状态管理、接口封装和样式入口。
4. 用户明确要求与参考规范冲突时，以用户要求为准，并在交付说明中列出偏离项。

## 实施要求

- 按功能模块组织 `views`，使用 `views/<module>/IndexView.vue` 作为默认入口，并把具体 UI 区块拆入模块私有组件。
- 根据复用范围决定组件位置；跨业务基础组件必须按功能分类放入 `components/<category>/`，不得平铺在根目录。
- 业务 API、状态和类型放入对应 `features/<domain>/`；页面和组件不得直接调用 Axios。
- 前端只按版本化 JSON API 契约对接后端；每个 `features/<domain>/api.ts` 的接口定义必须有中文注释，说明用途、方法/路径、请求参数与类型、响应 JSON、错误码、安全要求、`trace_id` 和兼容性；不得依赖 Django、Service、DAO、Model 等后端实现细节，也不得把页面设计要求写进接口。
- 页面或组件存在私有样式时，使用同目录、同名 CSS，并通过 `scoped style src` 一对一关联；全局样式只进入 `styles/`。
- 数据图表必须使用主流图表控件，禁止手写 SVG 静态图；没有特别说明时，不在文字前添加装饰性 icon。
- 保持参考规范定义的单向依赖、命名方式、拆分阈值、环境变量和路由约束。
- 开始接口联调前先阅读项目级 `docs/frontend-backend-api-conventions.md`（若项目提供），确认前后端使用同一契约、统一 JSON 包络、字段命名、ID 字符串化和版本策略。
- 不为补齐目录结构创建空目录，也不修改任务范围之外的代码。

## 验证与交付

1. 按参考规范的完成清单检查目录、复用边界、API 路径、加载/空/错误状态和样式归属。
2. 优先运行项目已有的类型检查与生产构建脚本；本规范项目通常执行 `npm run type-check` 和 `npm run build`。
3. 报告修改结果、验证命令及状态；如有无法执行的检查或规范偏离，明确说明原因。
