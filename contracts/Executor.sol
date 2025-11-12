// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// 我们从 npm install @openzeppelin/contracts 导入
// 这将处理 Wallet A 的所有权 (Owner)
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Executor
 * @dev 这个合约由 Wallet A (Owner) 部署。
 * 它持有资金，并根据 Owner 的链下指令，将资金“执行”转账到目标地址。
 */
contract Executor is Ownable {
    
    // 当合约 Owner (Wallet A) 部署时，构造函数会自动运行
    // 部署者 (msg.sender) 将自动被设为 Owner
    // 我们指定 initialOwner 为 'payable'，以便 Ownable 库知道
    constructor() Ownable(payable(msg.sender)) {}

    /**
     * @dev 核心执行函数。
     * 只有 Owner (Wallet A) 才能调用此函数。
     * 它从 *本合约* 的余额中向 'target' 发送 'amount' 的 ETH。
     * @param target 接收 ETH 的目标地址 (例如 Wallet B)
     * @param amount 要发送的 ETH 数量 (以 wei 为单位)
     */
    function executeTransfer(address payable target, uint amount) public onlyOwner {
        require(target != address(0), "Executor: Target address cannot be zero");
        require(address(this).balance >= amount, "Executor: Insufficient funds in contract");

        // 使用 .call() 发送 ETH，这是推荐的安全做法
        (bool success, ) = target.call{value: amount}("");
        require(success, "Executor: Transfer failed");
    }

    /**
     * @dev 紧急提款函数。
     * 允许 Owner (Wallet A) 提取合约中的所有剩余 ETH。
     */
    function withdraw() public onlyOwner {
        uint balance = address(this).balance;
        address payable ownerAddress = payable(owner());
        
        (bool success, ) = ownerAddress.call{value: balance}("");
        require(success, "Executor: Withdraw failed");
    }

    /**
     * @dev 接收 ETH 的函数。
     * 这使得我们可以从 Wallet A 向该合约地址发送 ETH 进行注资。
     * (阶段 4 将会用到)
     */
    receive() external payable {}
}