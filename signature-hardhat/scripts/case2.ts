import { ethers } from "hardhat";
import fs from "fs";

async function main() {
  // Lấy 3 signer đầu tiên từ local Hardhat node
  const signers = await ethers.getSigners();
  const signer1 = signers[0];
  const signer2 = signers[1];
  const signer3 = signers[2];
  const signer4 = signers[3];
  const signer5 = signers[4];
  const signer6 = signers[5];
  const signer7 = signers[6];
  const signer8 = signers[7];
  const signer9 = signers[8];
  const signer10 = signers[9];
  const signer11 = signers[10];

  // Deploy contract MultiSigVerifier
  const Factory = await ethers.getContractFactory("MultiSigVerifier");
  const contract = await Factory.deploy();
  await contract.deployed();
  console.log("Contract deployed at:", contract.address);


  let log = `Case 2: Multi-user verification & ETH transfers\n`;
  log += `Contract deployed at: ${contract.address}\n\n`;

  // =========================
  // ETH Transfers (demo)
  // =========================
  const transfers = [
    { from: signer1, to: signer2, value: "1.0" },
    { from: signer2, to: signer3, value: "0.5" },
    { from: signer3, to: signer4, value: "0.2" },
    { from: signer4, to: signer5, value: "0.3" },
    { from: signer5, to: signer6, value: "0.4" },
    { from: signer6, to: signer7, value: "0.1" },
    { from: signer7, to: signer8, value: "0.6" },
    { from: signer8, to: signer9, value: "0.7" },
    { from: signer9, to: signer10, value: "0.8" },
    { from: signer10, to: signer11, value: "0.9" },
  ];

  for (let i = 0; i < transfers.length; i++) {
    const tx = await transfers[i].from.sendTransaction({
      to: transfers[i].to.address,
      value: ethers.utils.parseEther(transfers[i].value),
    });
    const receipt = await tx.wait();
    console.log(`ETH Transfer #${i + 1}: from ${transfers[i].from.address} to ${transfers[i].to.address}, value ${transfers[i].value} ETH, gas used ${receipt.gasUsed.toString()}, block ${receipt.blockNumber}`);
    log += `ETH Transfer #${i + 1}: from ${transfers[i].from.address} to ${transfers[i].to.address}, value ${transfers[i].value} ETH, gas used ${receipt.gasUsed.toString()}, block ${receipt.blockNumber}\n`;
  }
  

  // Multi-signature demo (giả lập chữ ký)
  const messages = ["Vote proposal A", "Vote proposal B", "Vote proposal C", "Vote proposal D", "Vote proposal E", "Vote proposal F", "Vote proposal G", "Vote proposal H", "Vote proposal I", "Vote proposal J", "Vote proposal K"];
  const signatures = [
    { signer: signer1.address, v: 27, r: "0x727ace29061cbc5bc958cc15d23ea56f163d2ec41a3423682009a609df8f6ac1", s: "0x2e72449bc21a19818e6d93b40c6d197125a316fd2d767fb0df97fa36a6b749e6" },
    { signer: signer2.address, v: 28, r: "0x5e4912ee9687f547b9e5860b91417e987c884f916180e35f413c519c8af1b1a7", s: "0x438b966a471b20ee5ee1ccb00131d78d2fae67ca4ca088b8f467c4f396334aaa" },
    { signer: signer3.address, v: 27, r: "0xc7700a9e7afc375ab8f68d7ff8f8b43f1b22846d6fbcf6184f4f08aca3cb9963", s: "0x64b84b849e0ac7e39bbeb33ede8ee9ff9855a4386cdad6a15d4ea0880684bc10" },
    { signer: signer4.address, v: 27, r: "0x5b7742ae152ee434848dfe60f1db5224885abe1cab99be58f8edfa8489842663", s: "0x4cd0751c110b2d322f0422c84198edd085e806f3edec38eb0dabd1c11710450c" },

    { signer: signer5.address, v: 28, r: "0x9c5ad87b8657bfa458693b12b10017fea9992a972fb56265c5f3e0c205aacb73", s: "0x6739e370fc0edea4a21e073f454a694075dffc0afe3f635c40c1cc992bbff1cc" },

    { signer: signer6.address, v: 28, r: "0x2c92814094b37fb96f3cbbaf54f61374e30172b41a10af3e8ca03b7304754a3f", s: "0x35b9955c74450d67167491e56831896b67dcf79859261d4932d0f860d7ec590f" },

    { signer: signer7.address, v: 28, r: "0x34337679833081f9d446b66beb0298c7e09f08a6196cddf41e46356bbcbed35b", s: "0x67ce58e27a841a263d338a3f712f2b18a46023d8b88d7f783f83b5e1bea5ff5c" },
    { signer: signer8.address, v: 27, r: "0x1ce70af799cda5e8949bb25fcbafd8ab97f6e1a47c45d5426bd967830a587708", s: "0x51bce635c8196792fd98ea8c9a7b29a65774b06ea7aa3c004ad4a28689504d1f" },
    { signer: signer9.address, v: 27, r: "0x876ab74b3271f0ec6fa8e7492941e84f2179396b40d1261125abc5647e5bfa0e", s: "0x7e2154e145cdc6c7e4fb3b8001ed2405df4131b850b637e48c33e8040e2769ba" },
    { signer: signer10.address, v: 27, r: "0x613897ea706079c8be14048155e70c465db7ec71bb905d34f109aba82dc25e08", s: "0x320c7a0b38b93639b788ea710d6fb6b8540fbb49caf6ed529adbda5b9c9158d3" },
    { signer: signer11.address, v: 27, r: "0xe0bf5cadca985d4c2303cb747b68ed53999616e7c21781ef093fbd90b0d96b34", s: "0x745c7063b1344a5f4220811ba2f9e29b26f58ba7f2db66fa226d18bb6c4af1ef" },

];

  // Log chữ ký verification
  for (let i = 0; i < signatures.length; i++) {
    const sig = signatures[i];
    const valid = await contract.verifySignature(sig.signer, messages[i], sig.v, sig.r, sig.s);
    console.log(`Signature from ${sig.signer} valid?`, valid);
    log += `Signer: ${sig.signer}\nMessage: ${messages[i]}\nValid?: ${valid}\n\n`;
  }

  // Ghi ra file txt
  fs.appendFileSync("case2.txt", log, { encoding: "utf8" });
}

main().catch(console.error);
