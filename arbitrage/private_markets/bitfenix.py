from .market import Market
import config
from lib.exchange import exchange
from lib.settings import BTFNX_API_URL
import logging

# Symbols


class PrivateBitfenix(Market):

    def __init__(self, BTFNX_API_KEY=None, BTFNX_SECRET_TOKEN=None):
        super().__init__()
        if BTFNX_API_KEY == None:
            BTFNX_API_KEY = config.bitfenix_api_key
            BTFNX_SECRET_TOKEN = config.bitfenix_secret_key
        self.market = exchange(BTFNX_API_URL, BTFNX_API_KEY, BTFNX_SECRET_TOKEN,
                               'btfnx')
        self.currency = "EUR"
        self.get_info()

    def _buy(self, amount, price):
        response = self.market.buy(amount, price)
        if response and "code" in response:
            logging.warn(response)
            return False
        if not response:
            return response

        return response['order_id']

    def _sell(self, amount, price):
        """Create a sell limit order"""
        response = self.market.sell(amount, price)
        if response and "code" in response:
            logging.warn(response)
            return False
        if not response:
            return response
        return response['order_id']

    def _buy_maker(self, amount, price):
        response = self.market.bidMakerOnly(amount, price)
        if response and "code" in response:
            logging.warn(response)
            return False
        if not response:
            return response

        return response['order_id']

    def _sell_maker(self, amount, price):
        response = self.market.askMakerOnly(amount, price)
        if response and "code" in response:
            logging.warn(response)
            return False
        if not response:
            return response

        return response['order_id']

    def _get_order(self, order_id):
        response = self.market.orderInfo(order_id)
        if not response:
            return response

        if "code" in response:
            logging.warn(response)
            return False

        return response

    def _cancel_order(self, order_id):
        response = self.market.cancel(order_id)

        if not response:
            return response

        if response and "code" in response:
            logging.warn(response)
            return False

        resp_order_id = response['order_id']
        if resp_order_id == -1:
            logging.warn("cancel order #%s failed, %s" %
                         (order_id, resp_order_id))
            return False
        else:
            logging.debug("Canceled order #%s ok" % (order_id))
            return True
        return True

    def _cancel_all(self):
        response = self.market.cancelAll()
        if response and "code" in response:
            logging.warn(response)
            return False
        return response

    # FIXME: update exchange responses
    def get_info(self):
        """Get balance"""
        response = self.market.accountInfo()
        if response:
            if "code" in response:
                logging.warn("get_info failed %s", response)
                return False
            else:
                self.btc_balance = float(response["exchange_btc"])
                self.cny_balance = float(response["exchange_cny"])
                self.btc_frozen = float(response["exchange_frozen_btc"])
                self.cny_frozen = float(response["exchange_frozen_cny"])

        return response
