# -*- coding: utf-8 -*-
"""
CryptAPI's Python Helper
"""
from typing import Any, Dict, Optional

import aiohttp
import ujson as json
from loguru import logger as loguru_logger


class CryptAPIException(Exception):
    pass


class CryptAPIHelper:

    CRYPTAPI_URL = "https://api.cryptapi.io/"
    CRYPTAPI_HOST = "api.cryptapi.io"
    SUPPORTED_COINS_DISPALY_PAGE = "https://cryptapi.io/cryptocurrencies"

    def __init__(
        self,
        *,
        coin: Optional[str] = None,
        owner_address: Optional[str] = None,
        callback_url: Optional[str] = None
    ):
        if not coin:
            raise CryptAPIException("CryptAPIHelper.__init__ Error: Coin is Missing.")
        if not owner_address:
            raise CryptAPIException("CryptAPIHelper.__init__ Error: Owner Address is Missing.")
        if not callback_url:
            raise CryptAPIException("CryptAPIHelper.__init__ Error: Callback URL is Missing.")

        self.coin = coin
        self.owner_address = owner_address
        self.callback_url = callback_url
        self.payment_address = ""
        
        self._aio_session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=32),
            connector_owner=True,
            timeout=aiohttp.ClientTimeout(total=180)
        )

    async def close(
        self
    ):
        if self._aio_session:
            await self._aio_session.close()

    async def generate_payment_address(
        self,
        *,
        be_notified_of_pending_transactions: bool = False,
        owner_email: Optional[str] = None,
        priority: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a payment address for the owner address.

        :param be_notified_of_pending_transactions: when enabled you will be notified of pending transactions (were sent by the customer but not yet confirmed by the blockchain)
        :param owner_email: e-mail address to receive payment notifications, one more note:
            1). the email address must be comfirmed by CryptAPI (https://cryptapi.io/confirm_email) before it can be used to receive notifications.
        :param priority: priority for forwarding funds to the designated address (e.g default, fast, economic, etc.), two more notes:
            1). you can refer to 'https://support.cryptapi.io/article/how-the-priority-parameter-works' to find the specific priorities to use for each blockchain.
            2). the priority is supported only when utilizing Bitcoin, Ethereum/ERC-20, and Litecoin.

        :return: payment address information

        Example Response:
        -----------------
        {
            "address_in": "14PqCsA7KMgseZMPwg6mJy754MtQkrgszu",
            "address_out": "1H6ZZpRmMnrw8ytepV3BYwMjYYnEkWDqVP (single address)\n\n{1H6ZZpRmMnrw8ytepV3BYwMjYYnEkWDqVP: 0.70, 1PE5U4temq1rFzseHHGE2L8smwHCyRbkx3: 0.30} (multiple addresses)\n",
            "callback_url": "https://example.com/invoice/1234?payment_id=5678",
            "priority": "default",
            "status": "success"
        }
        """
        _address = None

        _optional_params = {}
        _optional_params["pending"] = 1 if be_notified_of_pending_transactions else 0
        if owner_email:
            _optional_params["email"] = owner_email
        # When enabled the callback(s) will be sent as POST.
        _optional_params["post"] = 0
        # When enabled the callback body will be sent in JSON format.
        _optional_params["json"] = 1
        # The priority for forwarding funds to the designated address.
        _optional_params["priority"] = priority
        # When enabled, returns the converted value converted to FIAT in the callback.
        _optional_params["convert"] = 0
        _params = {
            # The URL where the callbacks will be sent to.
            "callback": self.callback_url,
            # Address(es) where the payment will be forwarded to.
            # Address(es) must be valid for the ticker you are using.
            # Otherwise, the API will reject the payment.
            # For example, if you try to use a Bitcoin address while requesting a USDT TRC-20 address,
            # the API will throw an error.
            "address": self.owner_address,
            **_optional_params
        }
        _address = await CryptAPIHelper.process_request(session=self._aio_session, coin=self.coin, endpoint="create", params=_params)
        if _address:
            self.payment_address = _address["address_in"]
            loguru_logger.debug(f"Payment Address: {self.payment_address}")
        else:
            loguru_logger.error("Failed Payment Address Generation.")
        
        return _address

    async def get_payment_logs(
        self
    ) -> Dict[str, Any]:
        """
        Get payment callbacks for the owner address.
        It allows users to retrieve a list of callbacks made at the specified callbacks parameter,
        allows to track payment activity and troubleshoot any issues that may arise.

        :return: payment logs information

        Example Response:
        -----------------
        {
            "address_in": "14PqCsA7KMgseZMPwg6mJy754MtQkrgszu",
            "address_out": "1H6ZZpRmMnrw8ytepV3BYwMjYYnEkWDqVP",
            "callback_url": "https://example.com/invoice/1234?payment_id=5678",
            "status": "success",
            "notify_pending": true,
            "notify_confirmations": 1,
            "priority": "default",
            "callbacks": [
                {
                    "txid_in": "33f11611f863d7475eb10daada2f225f0877561cf58cdfff175e99635dfd9120",
                    "txid_out": "5ea53d5e728bfdb56b54c0b945990b69ae1e66cec56ab24679c9a622c4695276",
                    "value": 100000,
                    "value_coin": 0.1,
                    "value_forwarded": 100000,
                    "value_forwarded_coin": 0.1,
                    "confirmations": 13,
                    "last_update": "14/10/2022 12:47:18",
                    "result": "done",
                    "fee_percent": 1,
                    "fee": 2000,
                    "fee_coin": 0.02,
                    "prices": 55.59,
                    "logs": []
                }
            ]
        }
        """
        _params = {
            "callback": self.callback_url
        }
        return await CryptAPIHelper.process_request(session=self._aio_session, coin=self.coin, endpoint="logs", params=_params)

    async def get_qrcode(
        self,
        *,
        size: int = 512
    ):
        """
        Get a base64-encoded QR Code image for the payment address.

        :param size: size of the QR Code image in pixels, must be in the range of 64 to 1024

        :return: base64-encoded QR Code image information

        Example Response:
        -----------------
        {
            "status": "success",
            "qrcode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5fY51AAAgAElEQVR4nOzdeZgVZf7H8e9/5+9jZ7,
            "payment_uri": "..."
        }
        """
        _params = {
            "address": self.payment_address,
            "value": "",
            "size": size
        }
        return await CryptAPIHelper.process_request(session=self._aio_session, coin=self.coin, endpoint="qrcode", params=_params)

    async def get_conversion(
        self,
        *,
        from_coin: Optional[str] = None,
        value: int = 10
    ) -> Dict[str, Any]:
        """
        Convert price between a FIAT currency/cryptocurrency to a cryptocurrency/FIAT currency.

        :param from_coin: coin or token ticker or fiat (e.g btc, eth, usdt, usd, etc.)
        :param value: the value that you intend to convert

        :return: conversion price information

        Example Response:
        -----------------
        {
            "value_coin": "0.01",
            "exchange_rate": "47000",
            "status": "success"
        }
        """
        if not from_coin:
            raise CryptAPIException("CryptAPIHelper.get_conversion Error: From Coin is Missing.")
        _params = {
            "from": from_coin,
            "value": value
        }
        return await CryptAPIHelper.process_request(session=self._aio_session, coin=self.coin, endpoint="convert", params=_params)

    @staticmethod
    async def get_info(
    ) -> Dict[str, Any]:
        """
        Get information regarding CryptAPI Service (e.g supported blockchains, cryptocurrencies and tokens).

        :return: information regarding CryptAPI Service
        """
        async with aiohttp.ClientSession() as session:
            return await CryptAPIHelper.process_request(session=session, coin="", endpoint="info", params={"prices": "0"})

    @staticmethod
    async def get_supported_coins(
    ) -> Dict[str, str]:
        """
        Get supported cryptocurrencies and tokens.

        :return: supported cryptocurrencies and tokens
        """
        _info = await CryptAPIHelper.get_info()
        _info.pop("fee_tiers", None)
        _coins = {}
        for ticker, coin_info in _info.items():
            if "coin" in coin_info.keys():
                _coins[ticker] = coin_info["coin"]
            else:
                for token, token_info in coin_info.items():
                    _coins[ticker + "_" + token] = token_info["coin"] + " (" + ticker.upper() + ")"
        return _coins

    @staticmethod
    async def get_coin_info(
        *,
        coin: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get information regarding a specific coin or token.

        :param coin: coin or token ticker (e.g btc, eth, usdt, etc.)

        :return: information regarding a specific coin or token
        """
        if not coin:
            raise CryptAPIException("CryptAPIHelper.get_coin_info Error: Coin is Missing.")
        async with aiohttp.ClientSession() as session:
            return await CryptAPIHelper.process_request(session=session, coin=coin, endpoint="info", params={"prices": "0"})

    @staticmethod
    async def get_estimate_fees(
        *,
        coin: Optional[str] = None,
        addresses: int = 1,
        priority: str = "default"
    ):
        """
        Get estimated blockchain fees to process a transaction.

        :param coin: coin or token ticker (e.g btc, eth, usdt, etc.)
        :param addresses: number of addresses to forward the funds to (Blockchain fees will increase with the number of addresses)
        :param priority: priority for forwarding funds to the given address (e.g default, fast, economic, etc.), two more notes:
            1). you can refer to 'https://support.cryptapi.io/article/how-the-priority-parameter-works' to find the specific priorities to use for each blockchain.
            2). the priority is supported only when utilizing Bitcoin, Ethereum/ERC-20, and Litecoin.

        :return: estimated fees to process a transaction
        """
        if not coin:
            raise CryptAPIException("CryptAPIHelper.get_estimate_fees Error: Coin is Missing.")
        params = {
            "addresses": addresses,
            "priority": priority
        }
        async with aiohttp.ClientSession() as session:
            return await CryptAPIHelper.process_request(session=session, coin=coin, endpoint="estimate", params=params)

    @staticmethod
    async def process_request(
        *,
        session: aiohttp.ClientSession,
        coin: Optional[str] = None,
        endpoint: str = "",
        params: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        if coin:
            coin += "/"

        async with session.get(
            url="{base_url}{coin}{endpoint}/".format(
                base_url=CryptAPIHelper.CRYPTAPI_URL,
                coin=coin.replace("_", "/"),
                endpoint=endpoint
            ),
            params=params,
            headers={"Host": CryptAPIHelper.CRYPTAPI_HOST},
        ) as response:
            body = await response.text()
            data = json.loads(body)
            if data.get("status", "") == "error":
                raise CryptAPIException(data["error"])
            return data


if __name__ == "__main__":
    # import asyncio
    # import os

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)

    ## Test CryptAPIHelper Static Methods
    # ret = loop.run_until_complete(CryptAPIHelper.get_info())
    # print(f"CryptAPIHelper.get_info() -> {ret}")
    # ret = loop.run_until_complete(CryptAPIHelper.get_supported_coins())
    # print(f"CryptAPIHelper.get_supported_coins() -> {ret}")
    # ret = loop.run_until_complete(CryptAPIHelper.get_coin_info(coin="trc20_usdt"))
    # print(f"CryptAPIHelper.get_coin_info() -> {ret}")
    # ret = loop.run_until_complete(CryptAPIHelper.get_estimate_fees(coin="trc20_usdt"))
    # print(f"CryptAPIHelper.get_estimate_fees() -> {ret}")

    ## Test CryptAPIHelper Instance Methods
    # async def create_cryptapi_helper():
    #     crypt_api = CryptAPIHelper(
    #         coin="polygon/usdt",
    #         # The address must be valid for the ticker you are using.
    #         owner_address=os.getenv("MY_CRYPTAPI_OWNER_ADDRESS", None),
    #         callback_url=os.getenv("MY_CRYPTAPI_CALLBACK_URL", None)
    #     )
    #     await asyncio.sleep(0)
    #     return crypt_api

    # crypt_api = loop.run_until_complete(create_cryptapi_helper())
    # try:
    #     ret = loop.run_until_complete(crypt_api.generate_payment_address(
    #         be_notified_of_pending_transactions=True,
    #         owner_email=os.getenv("MY_CRYPTAPI_OWNER_EMAIL", None),
    #         priority="default"
    #     ))
    #     print(f"CryptAPIHelper.generate_payment_address() -> {ret}")
    #     import time
    #     time.sleep(5)
    #     ret = loop.run_until_complete(crypt_api.get_payment_logs())
    #     print(f"CryptAPIHelper.get_payment_logs() -> {ret}")
    #     ret = loop.run_until_complete(crypt_api.get_qrcode(size=512))
    #     print(f"CryptAPIHelper.get_qrcode() -> {ret}")
    # except CryptAPIException as e:
    #     print(f"CryptAPIException: {e}")
    # finally:
    #     loop.run_until_complete(crypt_api.close())

    # # NOTE: Wait 250 ms for the underlying connections to close.
    # # https://docs.aiohttp.org/en/stable/client_advanced.html#Graceful_Shutdown
    # loop.run_until_complete(asyncio.sleep(0.250))
    # loop.close()

    pass
