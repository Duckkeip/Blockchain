import { ethers } from "hardhat";
import fs from "fs";

async function main() {
  // 1️⃣ Lấy deployer 
  const signers = await ethers.getSigners();
  const deployer = signers[1]; // chọn account #1
  // 2️⃣ Deploy contract
  const Factory = await ethers.getContractFactory("SignatureVerifier");
  const contract = await Factory.deploy();
  await contract.deployed();

  console.log("Contract deployed at:", contract.address);

  // 3️⃣ Log thông tin ra file
  const logData = `
  Case 1: Single transaction verification
========================
Date: ${new Date().toLocaleString()}
Deployer: ${deployer.address}
Contract deployed at: ${contract.address}
ETH sent: 0
Transaction hash: ${contract.deployTransaction.hash}
Gas used: ${contract.deployTransaction.gasLimit.toString()}
========================
`;

  fs.appendFileSync("transaction_log.txt", logData, { encoding: "utf8" });
  console.log("Transaction info logged to transaction_log.txt");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
