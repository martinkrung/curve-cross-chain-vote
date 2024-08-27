import boa, os

RPC_ETHEREUM = os.getenv('RPC_ETHEREUM')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')


boa.env.fork(RPC_ETHEREUM)

crvusd = boa.from_etherscan(
    "0xf939E0A03FB07F59A73314E73794Be0E57ac1b4E",
    name="crvUSD",
    uri="https://api.etherscan.io/api",
    api_key=ETHERSCAN_API_KEY
)

supply = crvusd.totalSupply()
print(supply)
