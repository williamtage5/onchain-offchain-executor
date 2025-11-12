import { HardhatUserConfig } from "hardhat/config";

// 1. (关键!) 只导入我们刚刚安装的 v3 兼容插件
import "@nomicfoundation/hardhat-ethers";

// 2. (删除) 不再需要 'hardhat-toolbox'
// import "@nomicfoundation/hardhat-toolbox";

import "dotenv/config";

const sepoliaRpcUrl = process.env.SEPOLIA_RPC_URL || "";
const walletAPrivateKey = process.env.WALLET_A_PRIVATE_KEY || "";

const config: HardhatUserConfig = {
  solidity: "0.8.20",
  networks: {
    sepolia: {
      type: "http", 
      url: sepoliaRpcUrl,
      accounts: [walletAPrivateKey],
    },
  },
};

export default config;