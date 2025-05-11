require("@nomicfoundation/hardhat-toolbox");
require('dotenv').config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.20",
  paths: {
    sources: "./rental_platform/rental_platform/smart_contracts",
  },
  networks: {
    hardhat: {
      // chainId: 31337 // 默认的 chainId
    },
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "",
      accounts: 
        process.env.DEPLOYER_PRIVATE_KEY !== undefined 
          ? [process.env.DEPLOYER_PRIVATE_KEY] 
          : [],
      // gasPrice: 20000000000, // 20 Gwei (可选, Hardhat 会自动估算)
      // chainId: 11155111 // Sepolia 的 Chain ID (通常 Hardhat 会自动从节点获取)
    }
  }
};
