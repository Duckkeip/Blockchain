import { ethers } from "hardhat";

async function main() {
  const Verifier = await ethers.getContractFactory("SignatureVerifier");
  const verifier = await Verifier.deploy();
  await verifier.waitForDeployment();

  console.log("Contract deployed at:", await verifier.getAddress());
}

main().catch(console.error);
