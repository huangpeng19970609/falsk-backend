# Flask 博客系统

这是一个使用 Flask 构建的博客系统后端 API。

## 功能特性

- 用户认证（登录/注册）
- 文章管理（CRUD）
- 文件夹管理
- 图片上传
- JWT 认证

## 环境要求

- Python 3.8+
- MySQL 5.7+

## 安装步骤

1. 克隆项目并创建虚拟环境：

```bash
git clone <项目地址>
cd <项目目录>
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置数据库：

编辑 `db/config.py` 文件，修改数据库配置：

```python
DB_CONFIG = {
    'HOSTNAME': '127.0.0.1',  # 数据库主机名
    'PORT': 3306,             # 端口号
    'USERNAME': 'root',       # 数据库用户名
    'PASSWORD': '你的密码',    # 数据库密码
    'DATABASE': "flask-blog", # 数据库名称
}
```

4. 创建数据库：

在 MySQL 中创建数据库：

```sql
CREATE DATABASE `flask-blog` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. 初始化数据库：

```bash
# 初始化迁移
flask db init

# 创建迁移脚本
flask db migrate -m "initial migration"

# 应用迁移
flask db upgrade
```

## 运行项目

```bash
python app.py
```

默认情况下，服务器将在 http://127.0.0.1:8000 上运行。

## API 文档

主要路由：

- `/user/*` - 用户相关接口
- `/article/*` - 文章相关接口
- `/folder/*` - 文件夹相关接口
- `/upload/*` - 文件上传相关接口

## 开发说明

- 项目使用 Flask-JWT-Extended 进行身份认证
- 使用 Flask-SQLAlchemy 作为 ORM
- 图片上传支持的格式：PNG、JPG、JPEG、GIF

## 注意事项

1. 首次运行前请确保：

   - MySQL 服务已启动
   - 数据库配置正确
   - 已创建所需数据库

2. 开发环境下的图片上传路径为：

   - `static/uploads/` 目录

3. CORS 配置：
   - 默认允许 `http://localhost:3000` 的跨域请求
   - 如需修改，请在 `app.py` 中调整 CORS 配置

## 依赖说明

主要依赖包括：

- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-Migrate
- PyMySQL
- Flask-CORS

完整依赖列表请查看 `requirements.txt`。

## 问题排查

1. 数据库连接错误：

   - 检查 MySQL 服务是否运行
   - 验证数据库配置信息是否正确
   - 确认数据库用户权限

2. 迁移错误：

   - 删除 `migrations` 文件夹
   - 重新执行数据库初始化步骤

3. 图片上传失败：
   - 确保 `static/uploads` 目录存在且有写入权限
