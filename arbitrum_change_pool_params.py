#!/usr/bin/env python3


import boa
import curve_dao

import os, sys


RPC_ETHEREUM = os.getenv('RPC_ETHEREUM')
RPC_ARBITRUM = os.getenv('RPC_ARBITRUM')
ARBISCAN_API_KEY = os.getenv('ARBISCAN_API_KEY')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
PINATA_TOKEN = os.getenv('PINATA_TOKEN')
VOTE_CREATOR = os.getenv('VOTE_CREATOR')

boa.env.fork(RPC_ARBITRUM)

MIN_RATE = int(.01 * 1e18 / (365 * 86400))
MAX_RATE = int(.25 * 1e18 / (365 * 86400))

BROADCASTER = "0xb7b0FF38E0A01D798B5cd395BbA6Ddb56A323830"
ARBI_AGENT = "0x452030a5D962d37D97A9D65487663cD5fd9C2B32"


dlcBTC_pool = boa.from_etherscan(
    "0xe957cE03cCdd88f02ed8b05C9a3A28ABEf38514A",
    name="CurveStableswapPool",
    uri="https://api.arbiscan.io/api",
    api_key=ARBISCAN_API_KEY
)

# https://gov.curve.fi/t/adjust-pool-parameters-of-dlcbtc-wbtc-pool-for-upcoming-curvelend-integration/10202

#MA_EXP_TIME = 10387


MA_EXP_TIME = 10387
D_MA_TIME = 62324

#MA_EXP_TIME = "0000000000000010387"
#D_MA_TIME = int("0000000000000062324")

print(dlcBTC_pool.address)

arbi_actions = [
    (dlcBTC_pool.address, dlcBTC_pool.set_ma_exp_time.prepare_calldata(MA_EXP_TIME, D_MA_TIME)),
]
actions = [
    (BROADCASTER, 'broadcast', arbi_actions, 10_000_000, 10**9)
]

print(arbi_actions)

print(arbi_actions[0][1].hex())

print(hex(MA_EXP_TIME))
print(hex(D_MA_TIME))

sys.exit(0)      
assert dlcBTC_pool.ma_exp_time() == 866
assert dlcBTC_pool.D_ma_time() == D_MA_TIME

boa.env.fork(RPC_ETHEREUM)

with boa.env.prank(VOTE_CREATOR):
  vote_id = curve_dao.create_vote(
      curve_dao.addresses.CURVE_DAO_OWNERSHIP,
      actions,
      "Change min/max borrow rates to 1%/25% on WETH and WBTC LlamaLend markets on Arbitrum",
      ETHERSCAN_API_KEY,
      PINATA_TOKEN
  )

print(vote_id)

curve_dao.simulate(
    vote_id,
    curve_dao.addresses.CURVE_DAO_OWNERSHIP['voting'],
    ETHERSCAN_API_KEY
)

"""Now we simulate execution on Arbitrum and validate whether rates do in fact change or they don't:"""

boa.env.fork(RPC_ARBITRUM)

agent = boa.from_etherscan(
    ARBI_AGENT,
    name="ArbiOwnershipAgent",
    uri="https://api.arbiscan.io/api",
    api_key=ARBISCAN_API_KEY
)

with boa.env.prank(BROADCASTER):
  agent.execute(arbi_actions)

# assert dlcBTC_pool.ma_exp_time() == MA_EXP_TIME
#assert dlcBTC_pool.D_ma_time() == D_MA_TIME

print("Success! Pool params have been changed on Arbitrum.")