# 🚚 美国物流运营数据看板系统

## 项目简介
美国地区物流运营数据监控平台，通过可视化看板实时展示6个美国主要城市的站点KPI指标和配送员绩效，帮助管理者进行日/周复盘和成本优化。

## 🌟 功能特点
- 📊 实时监控完成率、拒收率、ETA达成率
- 📈 数据可视化图表展示
- 🚨 自动标识异常站点和配送员
- 💰 单均成本分析（美元）
- 🏪 6个美国主要城市站点覆盖
- 🚴 18个配送员绩效排名

## 🏪 覆盖城市
- **洛杉矶市中心站** (Los Angeles, CA)
- **纽约曼哈顿站** (New York, NY)
- **旧金山站** (San Francisco, CA)
- **芝加哥站** (Chicago, IL)
- **迈阿密站** (Miami, FL)
- **西雅图站** (Seattle, WA)

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 现代浏览器（Chrome/Firefox/Edge）

### 运行步骤

1. **初始化数据库**
   ```cmd
   cd C:\Users\zhuha\OneDrive\Desktop\GOFODEMO
   python database\setup_database.py
   ```

2. **启动后端服务**
   ```cmd
   cd backend
   python main.py
   ```
   *保持此窗口运行，不要关闭*

3. **打开前端界面**
   - 进入 `frontend` 文件夹
   - 双击 `index.html` 文件

### 访问地址
- 后端API: http://localhost:8000
- 前端看板: 直接打开 `frontend/index.html`

## 🛠️ 技术架构

### 技术栈
- **后端**: Python + FastAPI + SQLite
- **前端**: HTML + JavaScript + Chart.js
- **数据库**: SQLite

### 项目结构
```
GOFODEMO/
├── README.md                    # 项目说明
├── logistics.db                 # 数据库文件
├── backend/                     # 后端代码
│   ├── main.py                 # FastAPI主程序
│   ├── database.py             # 数据库配置
│   ├── requirements.txt        # Python依赖
│   └── __init__.py            # Python包标识
├── frontend/                   # 前端代码
│   └── index.html             # 看板界面
└── database/                   # 数据库脚本
    └── setup_database.py      # 数据库初始化
```

## 🔧 F12开发者工具调试指南

### 查看API请求数据

1. **打开开发者工具**
   - 在前端页面按 `F12`
   - 或右键 → 检查

2. **查看网络请求**
   - 点击 **Network** 标签
   - 刷新页面或点击"查询"按钮
   - 查看API请求状态和响应数据

3. **主要API接口**
   ```
   GET /api/kpi/daily?start_date=2025-01-25&end_date=2025-01-28
   GET /api/kpi/sites?date=2025-01-28
   GET /api/riders/performance?date=2025-01-28
   GET /api/sites/list
   ```

### 调试JavaScript

1. **查看Console输出**
   - 点击 **Console** 标签
   - 查看加载日志和错误信息
   ```javascript
   // 手动测试数据加载
   loadData()
   
   // 检查当前选中的站点
   document.getElementById('siteSelect').value
   ```

2. **实时修改日期测试**
   ```javascript
   // 设置特定日期范围
   document.getElementById('startDate').value = '2025-01-25'
   document.getElementById('endDate').value = '2025-01-28'
   loadData()
   ```

### 数据分析示例

在Console中直接分析数据：
```javascript
// 获取配送员数据并分析
fetch('http://localhost:8000/api/riders/performance?date=2025-01-28')
  .then(r => r.json())
  .then(data => {
      console.log('总配送员数:', data.length)
      console.log('平均完成率:', 
          (data.reduce((sum, r) => sum + r.completion_rate, 0) / data.length).toFixed(2) + '%'
      )
      console.log('最佳配送员:', 
          data.sort((a, b) => b.completion_rate - a.completion_rate)[0].rider_name
      )
  })
```

## 📊 数据说明

### 数据规模
- 6个美国站点
- 18个配送员（每个站点3个）
- 30天的模拟运营数据
- 540条配送记录

### KPI指标
- **完成率**: 订单成功配送比例
- **拒收率**: 客户拒收订单比例  
- **ETA达成率**: 准时送达比例
- **单均成本**: 每单平均成本（美元）
- **时均单量**: 每小时配送订单数

### 状态判定标准
- 🟢 **正常**: 完成率 ≥ 97%, 拒收率 ≤ 1.5%
- 🟡 **警告**: 完成率 95-97%, 拒收率 1.5-3%
- 🔴 **异常**: 完成率 < 95%, 拒收率 > 3%

## 🐛 故障排除

### 常见问题

1. **前端无数据**
   ```javascript
   // 在Console中检查
   console.log('API基础URL:', API_BASE)
   // 应该显示: http://localhost:8000/api
   ```

2. **图表不显示**
   - 检查Chart.js是否加载成功
   - 查看Network标签中Chart.js的加载状态

3. **日期不匹配**
   ```javascript
   // 手动设置正确日期
   document.getElementById('startDate').value = '2025-01-25'
   document.getElementById('endDate').value = '2025-01-28'
   ```

4. **CORS错误**
   - 确保后端服务正在运行
   - 检查后端CORS配置

### 重新初始化
```cmd
# 删除数据库重新开始
cd C:\Users\zhuha\OneDrive\Desktop\GOFODEMO
del logistics.db
python database\setup_database.py
```

## 📝 开发说明

此项目展示了完整的前后端开发流程：
- RESTful API设计和实现
- 数据库操作和ORM使用
- 数据可视化和前端开发
- 项目架构和部署流程

适合学习全栈开发、数据分析和可视化技术。