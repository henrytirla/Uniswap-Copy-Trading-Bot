import asyncio
import json
import time
import websockets
from web3 import Web3
import requests
from alchemy import Alchemy, Network
import datetime
import os
from dotenv import load_dotenv
# Load.env file
load_dotenv()

class Style:
    """Class to define text styles for printing."""
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


class TradeSimulator:
    def __init__(self, api_key, network, provider_url, monitored_wallets):
        self.alchemy = Alchemy(api_key, network)
        self.provider_url = provider_url

        self.WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        self.private_key = os.getenv("PRIVATE_KEY")
        self.WalletAddress = os.getenv("WALLET_ADDRESS")
        self.web3 = Web3(Web3.HTTPProvider(os.getenv("HTTP_RPC_URL")))

        self.eth_amount= os.getenv("BUY_AMOUNT")

        self.tokenAbi = [
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}],
             "payable": False, "stateMutability": "view", "type": "function"},
            {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}],
             "payable": False, "stateMutability": "view", "type": "function"},
            {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}],
             "payable": False, "stateMutability": "view", "type": "function"},
            {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf",
             "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view",
             "type": "function"}
        ]
        self.sellAbi = '[{"inputs":[{"internalType":"string","name":"_NAME","type":"string"},{"internalType":"string","name":"_SYMBOL","type":"string"},{"internalType":"uint256","name":"_DECIMALS","type":"uint256"},{"internalType":"uint256","name":"_supply","type":"uint256"},{"internalType":"uint256","name":"_txFee","type":"uint256"},{"internalType":"uint256","name":"_lpFee","type":"uint256"},{"internalType":"uint256","name":"_MAXAMOUNT","type":"uint256"},{"internalType":"uint256","name":"SELLMAXAMOUNT","type":"uint256"},{"internalType":"address","name":"routerAddress","type":"address"},{"internalType":"address","name":"tokenOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"minTokensBeforeSwap","type":"uint256"}],"name":"MinTokensBeforeSwapUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"tokensSwapped","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"ethReceived","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"tokensIntoLiqudity","type":"uint256"}],"name":"SwapAndLiquify","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"enabled","type":"bool"}],"name":"SwapAndLiquifyEnabledUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"_liquidityFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_maxTxAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_taxFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"claimTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"}],"name":"deliver","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"geUnlockTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromFee","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromReward","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"time","type":"uint256"}],"name":"lock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"numTokensSellToAddToLiquidity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"},{"internalType":"bool","name":"deductTransferFee","type":"bool"}],"name":"reflectionFromToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"liquidityFee","type":"uint256"}],"name":"setLiquidityFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"maxTxPercent","type":"uint256"}],"name":"setMaxTxPercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"swapNumber","type":"uint256"}],"name":"setNumTokensSellToAddToLiquidity","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_enabled","type":"bool"}],"name":"setSwapAndLiquifyEnabled","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"taxFee","type":"uint256"}],"name":"setTaxFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"swapAndLiquifyEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"rAmount","type":"uint256"}],"name":"tokenFromReflection","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"uniswapV2Pair","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"uniswapV2Router","outputs":[{"internalType":"contract IUniswapV2Router02","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"unlock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

        self.uniswap_abi = '[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
        self.router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

        self.uniswap_contract = self.web3.eth.contract(address=self.router_address, abi=self.uniswap_abi)

        self.queue = asyncio.Queue()
        self.monitored_wallets_hex = [self.format_hex(addr) for addr in monitored_wallets]

    @staticmethod
    def get_timestamp():
        time_stamp_data = datetime.datetime.now()
        return "[" + time_stamp_data.strftime("%H:%M:%S.%f")[:-3] + "]"

    @staticmethod
    def format_hex(original_hex):
        hex_without_prefix = original_hex[2:]
        desired_length = 64
        padded_hex = hex_without_prefix.zfill(desired_length)
        return "0x" + padded_hex.lower()

    async def buy_token(self, TokenAddress):

        amt = self.eth_amount
        self.web3.to_checksum_address(TokenAddress)
        sender_address = self.WalletAddress
        private_key = self.private_key
        balance = self.web3.eth.get_balance(sender_address)
        print("This address has:", self.web3.from_wei(balance, "ether"), "ETH")

        # specify token to buy
        token_to_buy = self.web3.to_checksum_address(TokenAddress)
        getTokenName = self.web3.eth.contract(address=TokenAddress, abi=self.tokenAbi)
        tokenSymbol = getTokenName.functions.symbol().call()
        tokenContract = self.web3.eth.contract(address=TokenAddress, abi=self.sellAbi)
        decimals = tokenContract.functions.decimals().call()
        DECIMAL = 10 ** decimals
        Token_balance = tokenContract.functions.balanceOf(sender_address).call()
        if Token_balance < 1:
            print("\nTrying to buy... ", tokenSymbol)
            spend = self.web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
            nonce = self.web3.eth.get_transaction_count(sender_address)
            start = time.time()  # start of the tx
            gasPrice = self.web3.eth.gas_price + (2 * 10 ** 9)


            uniswap_tx = self.uniswap_contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                0, [spend, token_to_buy], sender_address, (int(time.time()) + 10000)
            ).build_transaction(
                {
                    "from": sender_address,
                    "value": self.web3.to_wei(amt, "ether"),
                    "gas":300000,
                    "gasPrice": gasPrice,
                    # 'maxFeePerGas': self.web3.to_wei(100, "gwei"),
                    # 'maxPriorityFeePerGas': self.web3.to_wei(20, "gwei"),
                    "nonce": nonce,
                }
            )

            try:
                sign_tx = self.web3.eth.account.sign_transaction(
                    uniswap_tx, private_key
                )


                tx_hash = self.web3.eth.send_raw_transaction(sign_tx.raw_transaction)
                txHash = str(self.web3.to_hex(tx_hash))
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(txHash, timeout=8)
                print(tx_receipt)
                print("Bought Waiting Confirmation") #You can extend to ensure transaction is confirmed it is my assumption high fees will always ensure transactions are added 1-3s

                if tx_receipt.status == 1:
                    return f"Successfuly Bought {tokenSymbol}  TX-ID: 'https://www.etherscan.com/tx/{txHash}"

                else:
                    return f" Fail to Buy {tokenSymbol}  TX-ID: 'https://www.etherscan.com/tx/{txHash}"


            except Exception as e:
                print(e, " Transaction failed.")
        else:
            print("You already have this token in your wallet")

    async def sell_token(self, tokenAddress):

        tokenAddress = self.web3.to_checksum_address(tokenAddress)
        private_key = self.private_key
        WalletAddress = self.WalletAddress
        sellAbi = self.sellAbi
        router_address = self.router_address
        V2SwapAbi = self.uniswap_abi
        tokenContract = self.web3.eth.contract(address=tokenAddress, abi=sellAbi)
        symbol = tokenContract.functions.symbol().call()
        decimals = tokenContract.functions.decimals().call()
        DECIMAL = 10 ** decimals
        balance = tokenContract.functions.balanceOf(WalletAddress).call()
        if balance > 1:

            token_balance = balance / 10 ** decimals
            tokenSymbol = tokenContract.functions.symbol().call()
            print("Token Balance: " + str(balance // DECIMAL) + " " + symbol, decimals)

            contractbuy = self.web3.eth.contract(address=router_address, abi=V2SwapAbi)

            spend = Web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")  # WETH

            print(f"Swapping {token_balance} {tokenSymbol} for ETH")

            gas_price = self.web3.eth.gas_price + (2 * 10 ** 9)


            pancakeswap2_txn = contractbuy.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                int(balance), 0,
                [tokenAddress, spend],
                WalletAddress,
                (int(time.time()) + 1000000)
            ).build_transaction({
                'from': WalletAddress,
                "gasPrice": gas_price,
                'nonce': self.web3.eth.get_transaction_count(WalletAddress),
            })

            try:
                signed_txn = self.web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=private_key)
                tx_token = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
                print(f"Sold {tokenSymbol}: " + self.web3.to_hex(tx_token))
            except Exception as e:
                print("Error ", e, )
                pass

    async def approve(self, tokenAddress):
        tokenContract = self.web3.eth.contract(address=tokenAddress, abi=self.sellAbi)
        balance = tokenContract.functions.balanceOf(self.WalletAddress).call()

        if balance > 1:

            approve = tokenContract.functions.approve(self.router_address, balance).build_transaction({
                'from': self.WalletAddress,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.WalletAddress)
            })

            try:
                signed_txn = self.web3.eth.account.sign_transaction(approve, private_key=self.private_key)
                tx_token = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
                print("Approved: " + self.web3.to_hex(tx_token))
                time.sleep(3)

            except:
                print("Already been approved")
            pass

    async def process_transaction(self, transaction_hash):
        try:
            receipt = self.alchemy.core.get_transaction_receipt(transaction_hash)
            transfer_details = self.alchemy.core.get_transaction(transaction_hash)
            from_address = transfer_details['from']
            txn_hash = self.web3.to_hex(transfer_details['hash'])
            block_num = transfer_details['blockNumber']

            print("=======================")

            if receipt['status'] == 1:
                eth_value = None

                for logs in receipt['logs']:
                    if logs['address'] == self.WETH and self.web3.to_hex(
                            logs['topics'][0]) == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef":
                        hex_value = self.web3.to_hex(logs['data'])
                        integer_value = int(hex_value, 16)
                        eth_value = self.web3.from_wei(integer_value, 'ether')
                        eth_value = '{:.4f}'.format(eth_value)

                for logs in receipt['logs']:
                    if logs['address'] != self.WETH:
                        if eth_value is not None:
                            if self.web3.to_hex(logs['topics'][
                                                       0]) == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" and self.web3.to_hex(
                                logs['topics'][2]) in self.monitored_wallets_hex:
                                print(
                                    f" {self.get_timestamp()} {Style.RED}{block_num}{Style.RESET} {Style.GREEN} TOKEN BOUGHT: {logs['address']} {Style.RESET} {Style.MAGENTA} WALLET_ADDRESS: {from_address}{Style.RESET} For {eth_value} ETH")
                                print(f"TxnHash: https://etherscan.io/tx/{txn_hash}")
                                await self.buy_token(logs['address']) #Buy Function
                                print(Style.CYAN + "====BUYING TRADE SIMULATION======" + Style.RESET)

                            elif self.web3.to_hex(logs['topics'][
                                                         0]) == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" and self.web3.to_hex(
                                logs['topics'][1]) in self.monitored_wallets_hex:
                                print(f" {self.get_timestamp()} {Style.RED}{block_num}{Style.RESET} {Style.YELLOW}TOKEN SOLD: {logs['address']} {Style.RESET} {Style.MAGENTA} WALLET_ADDRESS: {from_address}{Style.RESET} For {eth_value} ETH")
                                print(f"TxnHash: https://etherscan.io/tx/{txn_hash}")
                                await self.sell_token(logs['address']) #Sell Function
                                print(Style.MAGENTA + "====SELLING TRADE SALE SIMULATION=====" + Style.RESET)
                        else:
                            if self.web3.to_hex(logs['topics'][
                                                       0]) == "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925" and self.web3.to_hex(
                                logs['topics'][1]) in self.monitored_wallets_hex:
                                print(
                                    f"{self.get_timestamp()} {Style.RED}{block_num}{Style.RESET}{Style.MAGENTA} TOKEN APPROVED: {logs['address']}{Style.RESET}{Style.MAGENTA} WALLET_ADDRESS: {from_address}{Style.RESET}")
                                print(f"TxnHash: https://etherscan.io/tx/{txn_hash}")
                                await self.approve(logs['address']) #Approve Function
                                print(Style.MAGENTA + "====APPROVED TRANSACTION=====" + Style.RESET)

            self.queue.task_done()

        except Exception as e:
            print(f"Error processing transaction {transaction_hash}: {str(e)}")
            self.queue.task_done()

    async def subscribe_to_pending_transactions(self):
        """Subscribe to WebSocket for pending transactions."""
        print("Connecting to WebSocket...")
        async with websockets.connect(self.provider_url) as websocket:
            print("WebSocket connection established.")
            subscription_data = {
                "jsonrpc": "2.0",
                "method": "eth_subscribe",
                "params": ["alchemy_minedTransactions",
                           {"addresses": [{"from": addr} for addr in monitored_wallets], "includeRemoved": False,
                            "hashesOnly": True}],
                "id": 1
            }

            await websocket.send(json.dumps(subscription_data))
            while True:
                response = await websocket.recv()
                response_data = json.loads(response)
                if "params" in response_data and "result" in response_data["params"]:
                    transaction_hash = response_data["params"]["result"]['transaction']['hash']
                    self.queue.put_nowait(transaction_hash)

    async def process_queue(self):
        """Process the queue of transactions."""
        print(Style.GREEN + "=====Monitoring Target Wallets To Copy Transactions======" + Style.RESET)
        while True:
            if self.queue.qsize() <= 3:
                wait_time = 3
            else:
                wait_time = 1

            transaction_hash = await self.queue.get()
            print(self.get_timestamp(), transaction_hash)
            await asyncio.sleep(wait_time)
            await self.process_transaction(transaction_hash)


if __name__ == "__main__":
    network = Network.ETH_MAINNET
    provider_url = os.getenv("WS_RPC_URL")
    raw_wallets = os.getenv("MONITOR_WALLETS", "[]")
    monitored_wallets = json.loads(raw_wallets)

    simulator = TradeSimulator(network, provider_url, monitored_wallets)

    asyncio.gather(simulator.subscribe_to_pending_transactions(), simulator.process_queue())
    asyncio.get_event_loop().run_forever()
