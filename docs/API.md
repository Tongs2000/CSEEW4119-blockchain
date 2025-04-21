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

## Tracker接口

### 1. 获取节点列表
- **接口**：`GET /peers`
- **描述**：获取当前网络中所有活跃的peer节点
- **响应示例**：
```json
{
    "status": "success",
    "data": {
        "peers": [
            "http://localhost:5001",
            "http://localhost:5002",
            "http://localhost:5003"
        ],
        "active_peers_count": 3,
        "last_updated": 1621234567
    }
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
    "block": {
        "index": 2,
        "transactions": [...],
        "timestamp": 1621234569,
        "previous_hash": "1111...",
        "hash": "2222...",
        "nonce": 456,
        "difficulty": 2,
        "merkle_root": "2222..."
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
    "block_index": 1,
    "local_verification": {
        "expected_hash": "预期哈希值",
        "expected_merkle_root": "预期Merkle根",
        "hash_ok": false,
        "merkle_ok": false
    },
    "peer_verification": {
        "节点URL": {
            "hash_match": false,
            "previous_hash_match": false,
            "merkle_root_match": false,
            "difficulty_match": false,
            "transactions_match": false
        }
    }
}
```
- **验证结果说明**：
  - `local_verification`：本地验证结果
    - `expected_hash`：根据区块内容计算出的预期哈希值
    - `expected_merkle_root`：根据交易计算出的预期Merkle根
    - `hash_ok`：区块哈希是否与预期一致
    - `merkle_ok`：Merkle根是否与预期一致
  - `peer_verification`：与各对等节点的比较结果
    - `hash_match`：区块哈希是否匹配
    - `previous_hash_match`：前一个区块哈希是否匹配
    - `merkle_root_match`：Merkle根是否匹配
    - `difficulty_match`：挖矿难度是否匹配
    - `transactions_match`：交易内容是否匹配
  - **重要说明**：
    - 任何验证结果为 `false` 都表示区块可能被篡改
    - 需要同时检查本地验证和对等节点验证的结果
    - 如果发现不一致，建议重新同步区块链

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

### 8. 提交投票
- **接口**：`POST /vote`
- **描述**：提交新的投票
- **请求体**：
```json
{
    "voter": "user123",
    "candidate": "candidate1"
}
```
- **响应示例**：
```json
{
    "status": "success",
    "message": "Vote submitted successfully",
    "data": {
        "transaction": {
            "sender": "user123",
            "recipient": "candidate1",
            "amount": 1
        }
    }
}
```
- **重要说明**：
  - 投票提交后，交易会进入待处理池
  - 必须调用 `/mine` 接口进行挖矿，投票才会被记录到区块链中
  - 只有被记录到区块链中的投票才会被计入统计结果

### 9. 获取投票结果
- **接口**：`GET /votes`
- **描述**：获取所有候选人的得票数
- **响应示例**：
```json
{
    "status": "success",
    "data": {
        "results": [
            {
                "candidate": "candidate1",
                "votes": 10
            },
            {
                "candidate": "candidate2",
                "votes": 5
            }
        ],
        "total_votes": 15,
        "last_updated": 1621234567
    }
}
```

### 10. 获取投票状态
- **接口**：`GET /vote_status`
- **描述**：获取指定用户的投票状态
- **参数**：
  - `voter`：用户ID
- **响应示例**：
```json
{
    "status": "success",
    "data": {
        "voter": "user123",
        "has_voted": true,
        "voted_candidate": "candidate1",
        "vote_time": 1621234567,
        "block_height": 5
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
6. 每个用户只能投一次票
7. 投票后必须进行挖矿才能生效
8. 投票结果会实时更新到区块链中
9. 投票状态可以通过区块链验证
10. 验证接口返回的任何 `false` 值都表示可能存在篡改

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
  2. 区块链信息
     - 区块链高度
     - 最新区块信息（时间戳、交易数量、哈希值）
     - 待处理交易数量
  3. 挖矿状态
     - 当前挖矿难度
     - 最近挖出的区块
  4. 网络信息
     - 当前连接的peer节点列表
     - 各节点的区块链高度

## 数据更新机制

### 实时更新
- 使用轮询机制保持数据实时性
- 建议更新频率：
  - 投票结果：5秒
  - 区块链状态：10秒
  - 节点状态：30秒

### 事件触发更新
- 新区块产生时
- 新交易提交时
- 节点状态变化时

## 注意事项

11. 前端应实现优雅降级，在网络延迟较高时仍能保持基本功能
12. 建议使用响应式设计，适配不同设备
13. 重要操作（如投票）需要用户确认
14. 错误提示应清晰明确，包含解决方案建议 