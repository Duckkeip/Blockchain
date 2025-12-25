    // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Hello {
    string public message = "Hello Blockchain";

    function setMessage(string memory _msg) public {
        message = _msg;
    }
}
