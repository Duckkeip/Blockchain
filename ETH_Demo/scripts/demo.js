const readline = require("readline");

module.exports = async function (callback) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const ask = (q) => new Promise(res => rl.question(q, res));

  try {
    const MiniBank = artifacts.require("MiniBank");
    const bank = await MiniBank.deployed();
    const accounts = await web3.eth.getAccounts();

    console.log("\n📒 DANH SÁCH ACCOUNT:");
    accounts.forEach((acc, i) => {
      console.log(`${i}: ${acc}`);
    });

    let idx = await ask("\n👉 Chọn account (số): ");
    let user = accounts[parseInt(idx)];

    if (!user) {
      console.log("❌ Account không tồn tại");
      rl.close();
      return callback();
    }

    console.log("\n✅ Bạn đã chọn:", user);

    let depositEth = await ask("👉 Nhập số ETH muốn gửi: ");
    await bank.deposit({
      from: user,
      value: web3.utils.toWei(depositEth, "ether")
    });

    console.log("✅ Đã gửi", depositEth, "ETH");

    let withdrawEth = await ask("👉 Nhập số ETH muốn rút: ");

    try {
      await bank.withdraw(
        web3.utils.toWei(withdrawEth, "ether"),
        { from: user }
      );
      console.log("✅ Đã rút", withdrawEth, "ETH");
    } catch (e) {
      console.log("⚠️ Rút thất bại:", e.reason || "Không đủ số dư");
    }

    let balance = await bank.getBalance({ from: user });
    console.log("💰 Số dư hiện tại:", web3.utils.fromWei(balance.toString(), "ether"), "ETH");

    rl.close();
    callback();

  } catch (err) {
    console.error("❌ Lỗi:", err);
    rl.close();
    callback(err);
  }
};
