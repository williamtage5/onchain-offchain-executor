// 1. (新) 导入 "ethers" 库本身，而不是 hardhat
import { ethers } from "ethers";

// 2. (新) 导入 "dotenv" 来读取 .env
import "dotenv/config";

// 3. (新) 导入我们编译好的合约 ABI 和 Bytecode
//    (路径 ../ 是从 /scripts 目录返回到根目录)
import ExecutorArtifact from "../artifacts/contracts/Executor.sol/Executor.json";

async function main() {
  console.log("正在从 .env 文件加载配置...");

  // 4. (新) 从 .env 获取我们的配置
  const rpcUrl = process.env.SEPOLIA_RPC_URL;
  const privateKey = process.env.WALLET_A_PRIVATE_KEY;

  if (!rpcUrl) {
    throw new Error("SEPOLIA_RPC_URL 未在 .env 文件中找到");
  }
  if (!privateKey) {
    throw new Error("WALLET_A_PRIVATE_KEY 未在 .env 文件中找到");
  }

  // 5. (新) 设置 Ethers.js Provider 和 Wallet
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const wallet = new ethers.Wallet(privateKey, provider);
  console.log("已连接到 Wallet A:", wallet.address);
  console.log("---------------------------------");

  // 6. (新) 从 Artifacts 加载 ABI 和 Bytecode
  const abi = ExecutorArtifact.abi;
  const bytecode = ExecutorArtifact.bytecode;

  // 7. (新) 创建合约工厂
  const ExecutorFactory = new ethers.ContractFactory(abi, bytecode, wallet);

  console.log("正在部署 Executor.sol...");
  
  // 8. (新) 部署合约
  const executor = await ExecutorFactory.deploy();
  
  // 等待部署完成
  await executor.waitForDeployment();

  const contractAddress = await executor.getAddress();

  console.log("---------------------------------");
  console.log("✅ 合约 'Executor.sol' 部署成功!");
  console.log("部署者 (Owner):", wallet.address);
  console.log("合约地址 (CONTRACT_ADDRESS):", contractAddress);
  console.log("---------------------------------");
  console.log("请将此合约地址复制到你的 .env 文件和阶段 5 的 Python 脚本中。");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});