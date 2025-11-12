import os
import json
from web3 import Web3
from dotenv import load_dotenv

def main():
    """
    主执行函数：加载配置、构建交易、签名并发送。
    """
    
    print("--- 链下 Python 脚本启动 ---")

    # 1. --- 加载配置 ---
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)
    
    abi_path = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'contracts', 'Executor.sol', 'Executor.json')
    
    try:
        with open(abi_path, 'r') as f:
            artifact = json.load(f)
        abi = artifact['abi']
    except FileNotFoundError:
        print(f"错误: 找不到 ABI 文件。请确保已编译合约: {abi_path}")
        return

    rpc_url = os.getenv("SEPOLIA_RPC_URL")
    wallet_a_key = os.getenv("WALLET_A_PRIVATE_KEY")
    wallet_b_addr_raw = os.getenv("WALLET_B_ADDRESS")
    contract_addr_raw = os.getenv("CONTRACT_ADDRESS")
    
    if not all([rpc_url, wallet_a_key, wallet_b_addr_raw, contract_addr_raw]):
        print("错误: .env 文件中的变量不完整。")
        return

    print(f"已加载配置：")
    print(f"  RPC 节点: {rpc_url[:25]}...")

    # 2. --- 连接到区块链 ---
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("错误: 无法连接到 Sepolia RPC 节点。")
        return
    
    chain_id = w3.eth.chain_id
    print(f"成功连接到链 ID: {chain_id} (Sepolia 应为 11155111)")

    # 2b. --- 转换地址为校验和格式 ---
    try:
        wallet_b_addr = w3.to_checksum_address(wallet_b_addr_raw)
        contract_addr = w3.to_checksum_address(contract_addr_raw)
        print(f"  合约地址 (校验和): {contract_addr}")
        print(f"  目标 (Wallet B) (校验和): {wallet_b_addr}")
    except ValueError as e:
        print(f"错误: .env 文件中的地址无效: {e}")
        return

    # 3. --- 设置签名账户 (Wallet A) ---
    account_a = w3.eth.account.from_key(wallet_a_key)
    w3.eth.default_account = account_a.address
    print(f"签名账户 (Wallet A): {account_a.address}")

    # 4. --- 实例化合约 ---
    executor_contract = w3.eth.contract(address=contract_addr, abi=abi)

    # 5. --- 定义交易参数 (链下决策) ---
    amount_to_send_eth = 0.0001
    amount_to_send_wei = w3.to_wei(amount_to_send_eth, 'ether')
    
    print("---------------------------------")
    print(f"决策：准备从合约向 Wallet B 发送 {amount_to_send_eth} ETH...")

    # 6. --- 构建、签名并发送交易 ---
    try:
        print("正在构建交易 (调用 executeTransfer)...")
        
        tx_call = executor_contract.functions.executeTransfer(
            wallet_b_addr,
            amount_to_send_wei
        )

        transaction = tx_call.build_transaction({
            'from': account_a.address,
            'nonce': w3.eth.get_transaction_count(account_a.address),
            'gas': 100000,
            'maxFeePerGas': w3.to_wei('50', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('2', 'gwei'),
        })

        print("正在使用 Wallet A 的私钥签名交易...")
        signed_tx = w3.eth.account.sign_transaction(transaction, wallet_a_key)

        print("正在将已签名的交易发送到 Sepolia 网络...")
        
        tx_hash_bytes = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # (关键修正!)
        # 1. 将 HexBytes 转换为标准十六进制字符串 (不带 0x)
        tx_hash_hex = tx_hash_bytes.hex()
        # 2. 手动添加 '0x' 前缀，确保链接 100% 正确
        tx_hash_with_prefix = f"0x{tx_hash_hex}"

        print(f"交易已发送! Tx Hash: {tx_hash_with_prefix}")
        print("正在等待交易回执 (这可能需要 15-30 秒)...")

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash_bytes)

        print("---------------------------------")
        if tx_receipt.status == 1:
            print("✅ 交易成功!")
            print(f"区块号: {tx_receipt.blockNumber}")
            print(f"Gas 消耗: {tx_receipt.gasUsed}")
            print("--- 验证链接 ---")
            print(f"在 Etherscan 上查看你的交易:")
            # (使用我们手动修正的、带 '0x' 的哈希)
            print(f"https://sepolia.etherscan.io/tx/{tx_hash_with_prefix}")
        else:
            print(f"❌ 交易失败! 回执: {tx_receipt}")

    except Exception as e:
        print(f"\n--- ❌ 发生错误 ---")
        if "insufficient funds" in str(e).lower():
            print("错误: 你的 Wallet A (0xf237...) 没有足够的 Sepolia ETH 来支付 Gas 费用。")
            print("请确保你的 Wallet A 有 ETH 来支付调用合约的 Gas。")
        else:
            print(f"错误详情: {e}")

if __name__ == "__main__":
    main()