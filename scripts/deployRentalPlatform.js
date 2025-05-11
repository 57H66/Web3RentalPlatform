async function main() {
  // 获取部署者账户
  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);

  // 获取合约工厂
  // 注意：这里的 "RentalPlatform" 必须与你的合约名称完全一致
  const RentalPlatform = await hre.ethers.getContractFactory("RentalPlatform");

  // 部署合约
  console.log("Deploying RentalPlatform...");
  const rentalPlatform = await RentalPlatform.deploy();

  // 等待部署完成
  // 在 ethers v5 及更早版本中使用 rentalPlatform.deployed()
  // 在 ethers v6+ 和 hardhat-ethers 中，contract.deployed() 已被移除，
  // deploy() 方法本身会等待部署完成，或者使用 contract.waitForDeployment()
  await rentalPlatform.waitForDeployment();

  console.log("RentalPlatform deployed to:", await rentalPlatform.getAddress());
}

// 我们推荐这种模式，以便能够在任何地方使用 async/await 并正确处理错误。
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 