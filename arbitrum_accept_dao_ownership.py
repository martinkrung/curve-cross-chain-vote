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


BROADCASTER = "0xb7b0FF38E0A01D798B5cd395BbA6Ddb56A323830"
ARBI_AGENT = "0x452030a5D962d37D97A9D65487663cD5fd9C2B32"

stablewswap_factory = boa.from_etherscan(
    "0x9AF14D26075f142eb3F292D5065EB3faa646167b",
    name="CurveStableswapFactoryNG",
    uri="https://api.arbiscan.io/api",
    api_key=ARBISCAN_API_KEY
)

# some test
assert stablewswap_factory.admin() == '0x2d12D0907A388811e3AA855A550F959501d303EE'
assert stablewswap_factory.future_admin() == ARBI_AGENT


 # accept_transfer_ownership (0xe5ea47b8)

arbi_actions = [
    (stablewswap_factory.address, stablewswap_factory.accept_transfer_ownership.prepare_calldata()),
]
actions = [
    (BROADCASTER, 'broadcast', arbi_actions, 10_000_000, 10**9)
]

print(arbi_actions)

print(arbi_actions[0][1].hex())


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


assert stablewswap_factory.admin() == ARBI_AGENT


print("Success! CurveStableswapFactoryNG ownership has been transferred to arbitrum agent.")