# Inventory Management System

一个基于 Flask 和 Vue.js 构建的库存管理系统，旨在帮助企业有效管理产品、库存、订单和生产流程。

## 功能特性

- 产品管理：添加、编辑、删除和查看产品信息
- 分类管理：管理产品分类和层级结构
- 库存管理：跟踪库存水平，记录出入库交易
- 订单管理：创建和管理采购/销售订单
- BOM管理：维护产品的物料清单（Bill of Materials）
- 生产管理：制定和跟踪生产计划
- 交易记录：记录所有的库存交易历史
- 仪表板：可视化展示关键指标和统计数据

## 技术栈

### 后端
- [Python](https://www.python.org/) - 编程语言
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM框架
- [SQLite](https://www.sqlite.org/) - 数据库

### 前端
- [Vue.js](https://vuejs.org/) - 前端框架
- [Vue Router](https://router.vuejs.org/) - 路由管理
- [Axios](https://axios-http.com/) - HTTP客户端
- [Vite](https://vitejs.dev/) - 构建工具

## 项目结构

```
inventory-system/
│
├── backend/                    # 后端应用程序
│   ├── data/                   # 数据库文件
│   ├── models/                 # 数据模型
│   ├── routes/                 # API路由
│   ├── services/               # 业务逻辑层
│   ├── utils/                  # 工具函数
│   ├── app.py                  # Flask应用入口
│   ├── config.py               # 配置文件
│   ├── requirements.txt        # Python依赖
│   ├── run.py                  # 应用启动文件
│   └── start.py                # 启动脚本
│
└── frontend/                   # 前端应用程序
    ├── node_modules/           # Node.js依赖包
    ├── src/                    # 源代码目录
    │   ├── components/         # 可复用组件
    │   ├── router/             # 路由配置
    │   ├── services/           # API服务
    │   ├── views/              # 页面视图
    │   ├── App.vue             # 根组件
    │   └── main.js             # 应用入口
    ├── index.html              # 主页面
    ├── package.json            # Node.js依赖配置
    ├── vite.config.js          # Vite配置文件
    └── proxy_server.py         # 开发代理服务器
```

## 快速开始

### 后端启动

1. 进入后端目录：
   ```
   cd backend
   ```

2. 安装Python依赖：
   ```
   pip install -r requirements.txt
   ```

3. 初始化数据库（可选）：
   ```
   python start.py
   ```

4. 启动后端服务：
   ```
   python run.py
   ```

   后端服务将在 `http://127.0.0.1:5000` 上运行。

### 前端启动

1. 进入前端目录：
   ```
   cd frontend
   ```

2. 安装前端依赖：
   ```
   npm install
   ```

3. 启动开发服务器：
   ```
   npm run dev
   ```

   前端将在 `http://localhost:8080` 上运行。

## API接口

后端提供了RESTful API接口，主要的API端点包括：

- `/api/products` - 产品管理
- `/api/categories` - 分类管理
- `/api/orders` - 订单管理
- `/api/bom` - BOM管理
- `/api/production` - 生产管理
- `/api/transactions` - 交易记录
- `/api/dashboard` - 仪表板数据

## 部署说明

1. 构建前端项目：
   ```
   npm run build
   ```

2. 使用生产级WSGI服务器（如Gunicorn）运行后端：
   ```
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 run:app
   ```

3. 配置Web服务器（如Nginx）来提供静态文件并反向代理API请求。

## 开发指南

1. 保持代码风格一致
2. 添加适当的注释和文档
3. 遵循现有的项目结构和命名约定
4. 在修改代码后进行充分测试

## 安全注意事项

- 生产环境中应配置适当的身份验证和授权机制
- 不要在生产环境中启用调试模式
- 定期备份数据库文件
- 使用HTTPS保护数据传输

## 故障排除

### 常见问题

1. **无法连接到后端API**
   - 确保后端服务正在运行
   - 检查前端代理配置是否正确

2. **数据库初始化失败**
   - 确保有写入[data](file:/inventory-system/backend/data)目录的权限
   - 检查SQLite是否正确安装

3. **前端页面空白**
   - 检查浏览器控制台中的JavaScript错误
   - 确保所有依赖都已正确安装

### 日志查看

后端日志存储在项目根目录的[logs](file:/inventory-system/logs)目录中，可以通过查看日志来诊断问题。

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request


## 联系方式

项目链接: [https://github.com/Aurora209/inventory-system](https://github.com/Aurora209/inventory-system)
