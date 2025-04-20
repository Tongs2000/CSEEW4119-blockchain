# 区块链系统接口文档

## 基础信息

### 服务器地址
- Tracker服务器：`http://localhost:6000`
- Client服务器：`http://localhost:5001`（端口号根据实际运行情况调整）

### 通用响应格式
```json
{
    "status": "success/error",
    "message": "操作结果描述",
    "data": {} // 具体数据
}
```

## 客户端接口

### 1. 获取区块链
- **接口**：`GET /chain`
- **描述**：获取当前节点的完整区块链数据
- **响应示例**：
```json
{
    "status": "success",
    "data": {
        "chain": [
            {
                "index": 0,
                "timestamp": 1621234567,
                "transactions": [],
                "previous_hash": "0",
                "hash": "0000...",
                "merkle_root": "0000...",
                "nonce": 0
            },
            {
                "index": 1,
                "timestamp": 1621234568,
                "transactions": [
                    {
                        "sender": "Alice",
                        "recipient": "Bob",
                        "amount": 10
                    }
                ],
                "previous_hash": "0000...",
                "hash": "1111...",
                "merkle_root": "1111...",
                "nonce": 123
            }
        ]
    }
}
```

### 2. 添加交易
- **接口**：`POST /transaction`
- **描述**：添加新的交易到待处理交易池
- **请求体**：
```json
{
    "sender": "Alice",
    "recipient": "Bob",
    "amount": 10
}
```
- **响应示例**：
```json
{
    "status": "success",
    "message": "交易已添加到待处理池",
    "data": {
        "transaction": {
            "sender": "Alice",
            "recipient": "Bob",
            "amount": 10
        }
    }
}
```

### 3. 挖矿
- **接口**：`POST /mine`
- **描述**：将待处理交易打包成新区块
- **响应示例**：
```json
{
    "status": "success",
    "message": "新区块已创建",
    "data": {
        "block": {
            "index": 2,
            "timestamp": 1621234569,
            "transactions": [...],
            "previous_hash": "1111...",
            "hash": "2222...",
            "merkle_root": "2222...",
            "nonce": 456
        }
    }
}
```

### 4. 编辑区块（测试用）
- **接口**：`POST /edit_block`
- **描述**：修改指定区块中的交易内容
- **请求体**：
```json
{
    "block_index": 1,
    "transaction_index": 0,
    "field": "amount",
    "new_value": 1000
}
```
- **响应示例**：
```json
{
    "status": "success",
    "message": "区块修改成功",
    "data": {
        "block": {
            "index": 1,
            "transactions": [...],
            "hash": "3333...",
            "merkle_root": "3333..."
        },
        "original_transaction": {
            "sender": "Alice",
            "recipient": "Bob",
            "amount": 10
        },
        "original_merkle_root": "1111..."
    }
}
```

### 5. 验证区块
- **接口**：`GET /verify_block`
- **描述**：验证指定区块的完整性
- **参数**：
  - `block_index`：要验证的区块索引（可选，默认最新区块）
- **响应示例**：
```json
{
    "status": "success",
    "data": {
        "block_index": 1,
        "is_hash_valid": false,
        "is_merkle_valid": false,
        "current_merkle_root": "4444...",
        "stored_merkle_root": "3333...",
        "modified_transaction_indices": [0],
        "block": {
            "index": 1,
            "transactions": [...],
            "hash": "3333...",
            "merkle_root": "3333..."
        }
    }
}
```

### 6. 获取挖矿参数
- **接口**：`GET /mining_params`
- **描述**：获取当前挖矿参数配置
- **响应示例**：
```json
{
    "status": "success",
    "data": {
        "difficulty": 2,
        "target_block_time": 60,
        "adjustment_interval": 10,
        "time_tolerance": 0.1
    }
}
```

### 7. 更新挖矿参数
- **接口**：`POST /mining_params`
- **描述**：更新挖矿参数配置
- **请求体**：
```json
{
    "difficulty": 3,
    "target_block_time": 45,
    "adjustment_interval": 15,
    "time_tolerance": 0.2
}
```
- **响应示例**：
```json
{
    "status": "success",
    "message": "挖矿参数已更新",
    "data": {
        "difficulty": 3,
        "target_block_time": 45,
        "adjustment_interval": 15,
        "time_tolerance": 0.2
    }
}
```

## 错误处理

### 常见错误响应
```json
{
    "status": "error",
    "message": "错误描述"
}
```

### 错误码说明
- 400：请求参数错误
- 404：资源不存在
- 500：服务器内部错误

## 注意事项

1. 所有时间戳均为 Unix 时间戳（秒）
2. 所有哈希值均为 SHA-256 哈希的十六进制字符串
3. 交易金额应为正数
4. 区块索引从 0 开始
5. 交易索引从 0 开始

## 前端页面设计建议

### 1. 投票应用页面（Voting App）
- **功能**：展示和操作投票系统
- **主要组件**：
  1. 投票列表展示
     - 显示所有可投票项
     - 每个投票项的当前票数
     - 投票状态（是否已投）
  2. 投票操作区
     - 选择投票项
     - 提交投票按钮
  3. 投票结果统计
     - 饼图/柱状图展示投票分布
     - 实时更新投票结果
  4. 区块链信息展示
     - 当前区块高度
     - 最新区块的哈希值
     - 投票交易确认状态

### 2. 客户端仪表盘（Client Dashboard）
- **功能**：展示客户端节点状态和区块链信息
- **主要组件**：
  1. 节点状态
     - 当前节点地址和端口
     - 连接状态（是否在线）
     - 网络延迟
  2. 区块链信息
     - 区块链高度
     - 最新区块信息
     - 待处理交易数量
  3. 挖矿状态
     - 当前挖矿难度
     - 挖矿速度
     - 最近挖出的区块
  4. 网络拓扑
     - 连接的peer节点
     - 节点间连接状态
     - 网络延迟热力图

### 3. Tracker监控页面（Tracker Monitor）
- **功能**：展示整个网络的状态
- **主要组件**：
  1. 网络概览
     - 活跃节点数量
     - 网络总交易量
     - 平均区块时间
  2. 节点管理
     - 所有节点的状态列表
     - 节点加入/离开历史
     - 节点性能指标
  3. 区块链同步状态
     - 各节点的区块链高度
     - 分叉情况
     - 同步延迟
  4. 网络健康度
     - 节点在线率
     - 网络延迟分布
     - 异常节点告警

## 数据更新机制

### 实时更新
- 使用WebSocket或轮询机制保持数据实时性
- 建议更新频率：
  - 投票结果：1秒
  - 区块链状态：5秒
  - 网络状态：10秒
  - 节点状态：30秒

### 事件触发更新
- 新区块产生时
- 新交易提交时
- 节点状态变化时
- 网络拓扑变化时

## 注意事项

6. 前端应实现优雅降级，在网络延迟较高时仍能保持基本功能
7. 建议使用响应式设计，适配不同设备
8. 重要操作（如投票）需要用户确认
9. 错误提示应清晰明确，包含解决方案建议 