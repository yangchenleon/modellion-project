## 数据库后台管理系统（FastAPI + Vite）

### 功能概览
- 产品与图片后台管理：增删改查、筛选、排序、分页
- 批量导入：从服务端 `./data/import/product_details.json` UPSERT（按 url）
- 图片管理：上传去重（MD5）、MinIO 存储、预签名 URL 预览/下载、删除
- 统计与健康：产品总数、标签/系列分布、最近导入 Top N、健康检查
- 认证与权限：JWT 登录；角色：`admin`（可写）、`readonly`（只读）
- 文档：内置 Swagger/OpenAPI（中文）

---

## 快速开始（推荐 Docker Compose）

### 1) 准备环境变量
复制 `.env.example` 为 `.env`（本仓库已提供默认值，可直接使用）：
```bash
cp .env.example .env
```
关键变量说明：
- 数据库（默认 SQLite）
  - `DATABASE_PATH=/data/app.db`
  - 或使用 Postgres：设置 `DATABASE_URL=postgresql+psycopg://user:pass@postgres:5432/db` 并启用 compose profile `postgres`
- MinIO（容器内）
  - `MINIO_ENDPOINT=minio:9000`
  - 宿主机映射：`9002`(API) / `9003`(Console)
  - `MINIO_BUCKET=bandai-hobby`
- 导入目录：`DATA_DIR=/data/import`（宿主机挂载为 `./data/import`）
- 认证：`JWT_SECRET`、`JWT_EXPIRES_IN`
- 管理员初始化（首次启动自动创建）：`ADMIN_USERNAME`/`ADMIN_PASSWORD`/`ADMIN_ROLE`

### 2) 一键启动
```bash
# 方式 A（Makefile）
make up

# 方式 B（Docker Compose）
docker compose up -d --build
```
启动后：
- 后端 API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- 前端管理端: `http://localhost:5173`
- MinIO 控制台: `http://localhost:9003`（账号/密码见 `.env` 中 `MINIO_ACCESS_KEY`/`MINIO_SECRET_KEY`）
- 默认管理员：`admin / admin123`

### 3) 目录挂载
- SQLite：`./data/app.db`
- 导入 JSON：`./data/import/product_details.json`

---

## 前端（Vite + React + TypeScript）
- 登录后可进行产品 CRUD、筛选/排序/分页、批量导入、图片上传/预览。
- 只读角色仅可浏览，按钮自动隐藏写操作（如需更细分权限可扩展）。

开发模式（可选）：
```bash
# 若单独本地开发前端（不通过容器）
cd frontend
npm i
npm run dev
```

---

## 后端（FastAPI + SQLAlchemy + Alembic）
- 严格使用权威模型：`products` / `images`；最小演进：增加 `price_value`、`release_date_value` 便于高效查询
- 数据库默认 SQLite；可切换 Postgres（见上）
- 认证：PBKDF2-SHA256（标准库 `hashlib.pbkdf2_hmac`）存储密码 + JWT 访问令牌
- 日志：JSON 结构化；统一异常处理

迁移（容器内自动执行）：
```bash
# 如需手动执行（容器内）
docker compose exec backend alembic upgrade head
```

常用 Make 目标：
```bash
make up          # 启动
make down        # 停止并清理
make logs        # 汇总日志
make backend-shell  # 进入后端容器
```

---

## 批量导入
1) 将 JSON 放至宿主机 `./data/import/product_details.json`
2) 前端“导入”页面点击“执行导入”
3) 服务会对 `url` 做 UPSERT（按 `url` 查重）；返回报表（总数/新增/更新/错误）

JSON 示例：
```json
{
  "product_name": "HG 1/144 XXX",
  "image_links": ["https://.../a.jpg", "https://.../b.jpg"],
  "product_info": { "価格": "2,200円", "発売日": "2025-01" },
  "article_content": "<p>...</p>",
  "url": "https://bandai-hobby.net/item/xxxxx/",
  "product_tag": "premium",
  "series": "gunpla"
}
```

---

## 图片管理 & MinIO
- 上传：计算 MD5 去重（重复拒绝），存储到 MinIO，并记录 `minio_path`
- 预览：通过后端预签名 URL（临时访问）在前端打开
- 删除：可选删除 MinIO 对象（需在前端确认）

---

## API 速览（简要）
- 认证
  - `POST /api/auth/login`（返回 `access_token`）
  - `GET /api/auth/me`
- 产品
  - `GET /api/products/?page=&page_size=&name=&tag=&series=&price_min=&price_max=&release_from=&release_to=&created_from=&created_to=&has_images=&sort_by=&sort_order=`
  - `POST /api/products/`（admin）
  - `GET /api/products/{id}`
  - `PUT /api/products/{id}`（admin）
  - `DELETE /api/products/{id}`（admin）
- 图片
  - `GET /api/images/product/{product_id}`
  - `POST /api/images/upload/{product_id}`（multipart 文件，admin）
  - `GET /api/images/presign/{image_id}`
  - `DELETE /api/images/{image_id}`（admin，可选 `delete_object=true`）
- 导入
  - `POST /api/import/json`（admin）
- 统计/健康
  - `GET /api/stats/overview?top=10`
  - `GET /healthz`、`GET /version`

---

## 切换 PostgreSQL（可选）
1) 打开 `.env`，设置：
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/modellion
```
2) 使用 profile 启动：
```bash
docker compose --profile postgres up -d --build
```

---

## 常见问题
- 端口占用：
  - MinIO API/Console 映射为 `9002/9003` 避免冲突
- 导入文件未找到：请确认宿主机 `./data/import/product_details.json` 已存在
- URL 唯一冲突：创建/更新时 `url` 唯一；批量导入会 UPSERT（冲突走更新）
- 只读权限：`role=readonly` 的用户无法进行写操作

---

## 安全与生产建议
- 修改 `.env` 中 `JWT_SECRET`、管理员密码
- 通过 Nginx/Traefik 增加 TLS 与鉴权
- MinIO 生产环境使用独立存储与密钥管理
- 开启数据库备份与审计

---

## 许可证
本项目用于演示与内部运营后台搭建，不包含任何爬虫或调度逻辑。
