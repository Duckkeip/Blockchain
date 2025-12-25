import { ethers } from "hardhat";

async function main() {
  // 1️⃣ Deploy contract
  const Factory = await ethers.getContractFactory("SignatureVerifier");
  const contract = await Factory.deploy();
  await contract.deployed();
  console.log("Contract deployed at:", contract.address);

  // 2️⃣ Test verify chữ ký Python
  const signer = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266";
  const message = "Authorize transaction";
  const v = 27;
  const r = "0x727ace29061cbc5bc958cc15d23ea56f163d2ec41a3423682009a609df8f6ac1";
  const s = "0x2e72449bc21a19818e6d93b40c6d197125a316fd2d767fb0df97fa36a6b749e6";

  const valid = await contract.verifySignature(signer, message, v, r, s);
  console.log("Signature valid?", valid);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
