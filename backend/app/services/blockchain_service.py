"""区块链存证服务 - 将证据数据写入区块链"""
import json
import hashlib
import time
from datetime import datetime, timezone
from app.config import settings


async def store_evidence(image_hash: str, phash: str, product_name: str, task_id: int) -> dict:
    """
    将存证数据写入区块链

    返回:
        dict: {
            "tx_hash": str,        # 交易哈希
            "block_number": int,   # 区块高度
            "timestamp": datetime, # 存证时间
        }
    """
    evidence = {
        "image_hash": image_hash,
        "phash": phash,
        "product_name": product_name,
        "task_id": task_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if settings.BLOCKCHAIN_PROVIDER == "mock":
        return await _mock_store(evidence)
    else:
        return await _fisco_store(evidence)


async def _mock_store(evidence: dict) -> dict:
    """
    模拟区块链存证（不需要真实链节点）
    生成假的交易哈希和区块号，数据仅存数据库
    """
    # 模拟网络延迟
    time.sleep(0.5)

    # 生成模拟交易哈希
    data_str = json.dumps(evidence, sort_keys=True)
    tx_hash = "0x" + hashlib.sha256(data_str.encode()).hexdigest()

    # 模拟区块号（递增）
    block_number = int(time.time()) % 100000

    return {
        "tx_hash": tx_hash,
        "block_number": block_number,
        "timestamp": datetime.now(timezone.utc),
    }


async def _fisco_store(evidence: dict) -> dict:
    """
    FISCO BCOS 真实上链
    TODO: 接入 FISCO BCOS Python SDK
    """
    # 1. 安装 SDK: pip install python-sdk
    # 2. 部署存证智能合约
    # 3. 调用合约的 storeEvidence 方法
    # 示例伪代码：
    #   from eth_account import Account
    #   w3 = Web3(Web3.HTTPProvider(settings.FISCO_RPC_URL))
    #   contract = w3.eth.contract(address=CONTRACT_ADDR, abi=ABI)
    #   tx = contract.functions.storeEvidence(evidence).transact()
    #   receipt = w3.eth.wait_for_transaction_receipt(tx)
    #   return {"tx_hash": receipt.transactionHash.hex(), "block_number": receipt.blockNumber, ...}
    raise NotImplementedError("FISCO BCOS 接入待实现，目前请使用 mock 模式")


async def verify_evidence(image_hash: str, tx_hash: str) -> bool:
    """验证链上存证"""
    if settings.BLOCKCHAIN_PROVIDER == "mock":
        # mock 模式：简单比对
        return True
    else:
        # TODO: 从链上读取存证并比对
        return True
