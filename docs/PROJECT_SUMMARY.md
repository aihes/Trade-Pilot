# Trade-Pilot 项目总结

## 项目概述

Trade-Pilot 是一个基于 AI Agent 的量化交易实验项目，用于在 Hyperliquid 平台上执行智能交易操作。

## 技术架构

### 核心技术栈

1. **CCXT** - 统一的加密货币交易 API
   - 用于与 Hyperliquid 交易所交互
   - 支持市价单、限价单等多种订单类型
   - 提供行情数据、持仓查询等功能

2. **LangChain** - AI 应用开发框架
   - 用于构建 AI Agent
   - 提供工具调用能力
   - 支持多种 LLM 模型

3. **LangGraph** - 工作流编排
   - 构建 Agent 的状态机
   - 管理工具调用流程
   - 实现复杂的决策逻辑

4. **OpenRouter** - AI 模型接入平台
   - 提供多种 AI 模型访问
   - 默认使用 Claude 3.5 Sonnet
   - 支持切换其他模型

### 项目结构

```
Trade-Pilot/
├── src/trade_pilot/          # 核心代码
│   ├── __init__.py           # 包初始化和主入口
│   ├── hyperliquid_client.py # Hyperliquid 客户端封装
│   ├── agent.py              # AI Agent 实现
│   └── tools.py              # LangChain 工具封装
├── examples/                 # 使用示例
│   └── basic_usage.py        # 基础使用示例
├── docs/                     # 文档
│   ├── QUICKSTART.md         # 快速开始指南
│   └── PROJECT_SUMMARY.md    # 项目总结
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略文件
├── pyproject.toml            # 项目配置
└── README.md                 # 项目说明
```

## 核心功能

### 1. Hyperliquid 客户端 (`hyperliquid_client.py`)

封装了 CCXT 的 Hyperliquid 交易功能：

- **账户管理**
  - `get_balance()` - 获取账户余额
  - `get_positions()` - 获取当前持仓

- **行情数据**
  - `get_ticker(symbol)` - 获取实时行情
  - `get_orderbook(symbol)` - 获取订单簿

- **订单操作**
  - `create_market_order()` - 创建市价单
  - `create_limit_order()` - 创建限价单
  - `cancel_order()` - 取消订单
  - `cancel_all_orders()` - 取消所有订单

- **订单查询**
  - `get_open_orders()` - 获取未成交订单
  - `get_order_status()` - 查询订单状态

- **持仓管理**
  - `close_position()` - 平仓

### 2. LangChain 工具 (`tools.py`)

将交易功能封装为 LangChain Tools：

1. **PlaceOrderTool** - 下单工具
   - 支持市价单和限价单
   - 支持只减仓模式
   - 返回订单详情

2. **CancelOrderTool** - 取消订单工具
   - 根据订单 ID 取消订单

3. **QueryOrderStatusTool** - 查询订单状态工具
   - 获取订单详细信息
   - 包含成交情况

4. **GetOpenOrdersTool** - 获取未成交订单工具
   - 支持按交易对筛选
   - 返回订单列表

5. **GetPositionsTool** - 获取持仓工具
   - 显示所有持仓
   - 包含盈亏信息

6. **GetTickerTool** - 获取行情工具
   - 实时价格数据
   - 买卖盘信息

7. **ClosePositionTool** - 平仓工具
   - 一键平仓
   - 自动判断方向

### 3. AI Agent (`agent.py`)

使用 LangGraph 构建的智能交易代理：

- **状态管理**
  - 维护对话历史
  - 管理工具调用流程

- **工作流**
  - Agent 节点：调用 LLM 分析用户意图
  - Action 节点：执行工具调用
  - 条件判断：决定是否继续执行

- **交互模式**
  - `run()` - 单次执行
  - `chat()` - 交互式聊天

## 使用场景

### 1. 行情查询

```python
agent.run("帮我查看 BTC 的当前价格")
```

### 2. 持仓管理

```python
agent.run("我现在有哪些持仓？")
agent.run("帮我平掉 BTC 的持仓")
```

### 3. 订单操作

```python
agent.run("帮我以市价买入 0.1 张 BTC")
agent.run("在 44000 美元挂一个买入限价单，数量 0.2 张 BTC")
agent.run("取消我的所有未成交订单")
```

### 4. 订单查询

```python
agent.run("查看我的未成交订单")
agent.run("查询订单 xxx 的状态")
```

## 安全特性

1. **测试网支持**
   - 默认使用测试网
   - 避免真实资金风险

2. **API 密钥保护**
   - 使用环境变量管理
   - .gitignore 排除敏感文件

3. **错误处理**
   - 完善的异常捕获
   - 详细的日志记录

4. **用户确认**
   - Agent 会说明操作影响
   - 建议用户确认后执行

## 扩展方向

### 1. 信号源集成

- **Jina AI** - 新闻搜索和分析
- **技术指标** - 集成 TA-Lib
- **链上数据** - 集成区块链数据源

### 2. 策略开发

- 趋势跟踪策略
- 网格交易策略
- 套利策略
- 做市策略

### 3. 风险管理

- 仓位管理
- 止损止盈
- 风险评估
- 资金管理

### 4. 性能优化

- 异步执行
- 批量操作
- 缓存机制
- 连接池

### 5. 监控告警

- 持仓监控
- 盈亏告警
- 异常检测
- 性能监控

## 开发计划

### Phase 1: 基础框架 ✅

- [x] 项目初始化
- [x] CCXT 集成
- [x] LangChain 集成
- [x] 基础交易工具
- [x] AI Agent 实现

### Phase 2: 信号源集成

- [ ] Jina AI 新闻搜索
- [ ] 技术指标计算
- [ ] 市场情绪分析
- [ ] 多源信号融合

### Phase 3: 策略开发

- [ ] 策略框架设计
- [ ] 回测系统
- [ ] 策略优化
- [ ] 实盘测试

### Phase 4: 风险管理

- [ ] 仓位管理系统
- [ ] 风险评估模型
- [ ] 止损止盈机制
- [ ] 资金管理策略

### Phase 5: 生产就绪

- [ ] 性能优化
- [ ] 监控告警
- [ ] 日志分析
- [ ] 文档完善

## 依赖安装

由于网络问题，依赖可能未完全安装。请在网络稳定时执行：

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .

# 如果遇到网络问题，可以使用国内镜像
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  ccxt langchain langgraph langchain-openai python-dotenv
```

## 提交到 GitHub

代码已提交到本地仓库，但由于网络问题可能未推送成功。请手动执行：

```bash
git push origin main
```

## 下一步

1. **安装依赖** - 在网络稳定时完成依赖安装
2. **配置环境** - 复制 `.env.example` 到 `.env` 并填写配置
3. **测试功能** - 运行示例代码测试基础功能
4. **集成信号源** - 添加 Jina AI 等信号源
5. **开发策略** - 实现具体的交易策略

## 参考资源

- [CCXT 文档](https://docs.ccxt.com/)
- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Hyperliquid 文档](https://hyperliquid.gitbook.io/)
- [OpenRouter 文档](https://openrouter.ai/docs)

## 联系方式

- GitHub: https://github.com/aihes/Trade-Pilot
- Email: aihehe123@gmail.com

