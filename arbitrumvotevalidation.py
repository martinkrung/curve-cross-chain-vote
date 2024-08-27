#!/usr/bin/env python3

import boa
import curve_dao

import os
import sys


RPC_ETHEREUM = os.getenv('RPC_ETHEREUM')
RPC_ARBITRUM = os.getenv('RPC_ARBITRUM')
ARBISCAN_API_KEY = os.getenv('ARBISCAN_API_KEY')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
PINATA_TOKEN = os.getenv('PINATA_TOKEN')
VOTE_CREATOR = os.getenv('VOTE_CREATOR')

boa.env.fork(RPC_ETHEREUM)

MIN_RATE = int(.01 * 1e18 / (365 * 86400))
MAX_RATE = int(.25 * 1e18 / (365 * 86400))

BROADCASTER = "0xb7b0FF38E0A01D798B5cd395BbA6Ddb56A323830"
ARBI_AGENT = "0x452030a5D962d37D97A9D65487663cD5fd9C2B32"

weth_policy = boa.from_etherscan(
    "0xEB9c27A490eDE4f82c05d320FA741989048BD597",
    name="LendFactory",
    uri="https://api.arbiscan.io/api",
    api_key=ARBISCAN_API_KEY
)

wbtc_policy = boa.from_etherscan(
    "0xEdbbD476893C7A938c14AAC27A05B0e98C8a68F7",
    name="LendFactory",
    uri="https://api.arbiscan.io/api",
    api_key=ARBISCAN_API_KEY
)

# print(wbtc_policy.min_rate())
# sys.exit(0)

arbi_actions = [
    (weth_policy.address, weth_policy.set_rates.prepare_calldata(MIN_RATE, MAX_RATE)),
    (wbtc_policy.address, wbtc_policy.set_rates.prepare_calldata(MIN_RATE, MAX_RATE))
]
actions = [
    (BROADCASTER, 'broadcast', arbi_actions, 10_000_000, 10**9)
]


with boa.env.prank(VOTE_CREATOR):
  vote_id = curve_dao.create_vote(
      curve_dao.addresses.CURVE_DAO_OWNERSHIP,
      actions,
      "Change min/max borrow rates to 1%/25% on WETH and WBTC LlamaLend markets on Arbitrum",
      ETHERSCAN_API_KEY,
      PINATA_TOKEN
  )
# vote_id

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

print( weth_policy.min_rate())

assert weth_policy.min_rate() == MIN_RATE
assert weth_policy.max_rate() == MAX_RATE

assert wbtc_policy.min_rate() == MIN_RATE
assert wbtc_policy.max_rate() == MAX_RATE
