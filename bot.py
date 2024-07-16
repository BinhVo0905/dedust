from dedust import Asset, Factory, PoolType, SwapParams, VaultNative,JettonRoot, JettonWallet, VaultJetton
from pytoniq import WalletV4R2, LiteBalancer
import asyncio
import sys
import time


mnemonics = ["easy", "sunny", "senior", "ritual", "deputy", "garden", "circle", "diary", "flip", "west",
             "topple", "rubber", "rubber", "luggage", "combine", "version", "educate", "pilot", "journey",
             "start", "busy", "matter", "leopard", "outside"]

async def buy(token_address, amount=0.1):
    provider = LiteBalancer.from_mainnet_config(1)
    await provider.start_up()
    wallet = await WalletV4R2.from_mnemonic(provider=provider, mnemonics=mnemonics) 
    TON = Asset.native()
    TOKEN = Asset.jetton(token_address)
    pool = await Factory.get_pool(pool_type=PoolType.VOLATILE, assets=[TON, TOKEN], provider=provider)
    swap_params = SwapParams(deadline=int(time.time() + 60 * 5), recipient_address=wallet.address)
    if amount == None:
        swap_amount = int(float(0.1) * 1e9)
    else: swap_amount = int(float(amount) * 1e9)
    print(swap_amount)
    swap = VaultNative.create_swap_payload(amount=swap_amount, pool_address=pool.address, swap_params=swap_params)
    swap_amount += int(0.25 * 1e9) 
    await wallet.transfer(destination="EQDa4VOnTYlLvDJ0gZjNYm5PXfSmmtL6Vs6A_CZEtXCNICq_", amount=swap_amount, body=swap)
    await provider.close_all()

async def sell(token_address, amount=None):
    provider = LiteBalancer.from_mainnet_config(1)
    await provider.start_up()
    wallet = await WalletV4R2.from_mnemonic(provider=provider, mnemonics=mnemonics)
    TON = Asset.native()
    TOKEN = Asset.jetton(token_address)
    pool = await Factory.get_pool(pool_type=PoolType.VOLATILE, assets=[TON, TOKEN], provider=provider)
    token_vault = await Factory.get_jetton_vault(token_address, provider=provider)
    token_root = JettonRoot.create_from_address(token_address)
    token_wallet = await JettonRoot.get_wallet(token_root, wallet.address, provider)
    if amount == None:
        swap_amount = await token_wallet.get_balance(provider=provider)
    else:
        swap_amount = int(float(amount) * 1e9) 
    print(swap_amount)
    swap = token_wallet.create_transfer_payload(
        destination=token_vault.address,
        amount=swap_amount,
        response_address=wallet.address,
        forward_amount=int(0.25*1e9),
        forward_payload=VaultJetton.create_swap_payload(pool_address=pool.address)
    )
    await wallet.transfer(destination=token_wallet.address, amount=int(0.3*1e9), body=swap)
    await provider.close_all()
    
async def main(action, amount, token_address):
    if action == "buy":
        await buy(token_address, amount)
    elif action == "sell":
        await sell(token_address,amount)
    else:
        print("Action không hợp lệ.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python bot.py [buy/sell] [amount (optional)] [token_address]")
        sys.exit(1)
    action = sys.argv[1]
    if len(sys.argv) > 3: 
        amount = float(sys.argv[2])
        token_address = sys.argv[3]
    else:
        amount = None
        token_address = sys.argv[2]

    asyncio.run(main(action, amount, token_address))
