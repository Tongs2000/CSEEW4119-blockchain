import requests
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.blockchain.chain import Blockchain

# 1) 构造并挖出一个新区块
bc = Blockchain()
bc.add_transaction({'from':'Alice','to':'Bob','amount':5})
new_block = bc.mine_pending_transactions()
data = new_block.to_dict()

# 2) 发给本地 Flask
resp = requests.post("http://localhost:5000/new_block", json=data, timeout=5)

print(resp.status_code, resp.json())