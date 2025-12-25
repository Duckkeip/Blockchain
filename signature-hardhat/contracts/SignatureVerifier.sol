// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SignatureVerifier {
    function verifySignature(
        address signer,
        string memory message,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public pure returns (bool) {
        bytes32 messageHash = keccak256(abi.encodePacked(message));
        bytes32 ethSignedHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash)
        );
        return ecrecover(ethSignedHash, v, r, s) == signer;
    }
}
