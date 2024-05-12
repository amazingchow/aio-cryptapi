[<img src="https://i.imgur.com/IfMAa7E.png" width="300"/>](image.png)

# CryptAPI's Python Library, in Asynchronous IO Mode

Python implementation of CryptAPI's payment gateway. The code requires Python version 3.8 or newer.

## How to Install?

```shell
pip install aio-cryptapi
```

## How to Use?

Here is a short example.

```python

if __name__ == "__main__":
    import asyncio
    import os
    from cryptapi import CryptAPIHelper

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # CryptAPIHelper Static Methods
    ret = loop.run_until_complete(CryptAPIHelper.get_info())
    print(f"CryptAPIHelper.get_info() -> {ret}")
    ret = loop.run_until_complete(CryptAPIHelper.get_supported_coins())
    print(f"CryptAPIHelper.get_supported_coins() -> {ret}")
    ret = loop.run_until_complete(CryptAPIHelper.get_coin_info(coin="polygon/usdt"))
    print(f"CryptAPIHelper.get_coin_info() -> {ret}")
    ret = loop.run_until_complete(CryptAPIHelper.get_estimate_fees(coin="polygon/usdt"))
    print(f"CryptAPIHelper.get_estimate_fees() -> {ret}")

    # CryptAPIHelper Instance Methods
    async def create_cryptapi_helper():
        crypt_api = CryptAPIHelper(
            coin="polygon/usdt",
            # The address must be valid for the ticker you are using.
            owner_address=os.getenv("MY_CRYPTAPI_OWNER_ADDRESS", None),
            callback_url=os.getenv("MY_CRYPTAPI_CALLBACK_URL", None)
        )
        await asyncio.sleep(0)
        return crypt_api

    crypt_api = loop.run_until_complete(create_cryptapi_helper())
    try:
        ret = loop.run_until_complete(crypt_api.generate_payment_address(
            be_notified_of_pending_transactions=True,
            owner_email=os.getenv("MY_CRYPTAPI_OWNER_EMAIL", None),
            priority="default"
        ))
        print(f"CryptAPIHelper.generate_payment_address() -> {ret}")
        import time
        time.sleep(5)
        ret = loop.run_until_complete(crypt_api.get_payment_logs())
        print(f"CryptAPIHelper.get_payment_logs() -> {ret}")
        ret = loop.run_until_complete(crypt_api.get_qrcode(size=512))
        print(f"CryptAPIHelper.get_qrcode() -> {ret}")
    except CryptAPIException as e:
        print(f"CryptAPIException: {e}")
    finally:
        loop.run_until_complete(crypt_api.close())

    loop.run_until_complete(asyncio.sleep(0.250))
    loop.close()

```
