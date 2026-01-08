const MiniBank = artifacts.require("MiniBank");

module.exports = function (deployer) {
  deployer.deploy(MiniBank);
};
