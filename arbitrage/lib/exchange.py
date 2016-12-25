from .helpers import *
import config
import urllib.parse as urlparse


class exchange:

    def __init__(self, url, apiKey, secretToken, role='default'):
        """
        FIXME: Change this to something more understandable :)
        Role : market is role

        """
        self.url = url
        self.apikey = apiKey
        self.secretToken = secretToken
        self.role = role

    def _create_nonce(self):
        return str(time.time() * 1000000)
    def _create_nonce_int(self):
        return int(time.time()*1000)

    def market(self):
        return self.role

    def trim_uri(self, uri):
        return uri.split(self.url['host'])[1]

    def buy(self, amount, price, tradePassword=None,
            tradeid=None, type='market'):
        if self.role == 'btfnx':
            payload = {'request': self.trim_uri(self.url['new_order']),
                       'nonce': self._create_nonce(),
                       'symbol': config.btfnx_symbol,
                       'amount': amount,
                       'price': price,
                       'side': 'buy',
                       'type': type
            }
            signedPayload = self.create_bfnx_payload(payload)
            return requestPost(self.url['new_order'], payload, headers=signedPayload)
        if self.role == 'krn':
            payload ={
                'pair': config.krn_pair,
                'type': 'buy',
                'ordertype': type,
                'volume': amount,
            }
            signedPayload = self.create_krn_payload(payload)
            return requestPost(self.url['new_order'], payload,
                               headers=signedPayload)

        if self.role == 'haobtc' or self.role == 'default':
            payload = {'amount': amount, 'price': price, 'api_key': self.apikey,
                       'secret_key': self.secretToken, 'type': 'buy'}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['trade'], payload)

        if self.role == 'okcoin':
            body = requestBody(self.url['trade'], self.url['host'])
            params = {
                'api_key': self.apikey,
                'symbol': 'btc_cny',
                'type': 'buy'
            }
            if price:
                params['price'] = price
            if amount:
                params['amount'] = amount

            params['sign'] = buildSign(params, self.secretToken, self.role)
            r = httpPost(self.url['host'], body, params)
            if r:
                return json.loads(r)
            else:
                return None

        if self.role == 'huobi':
            timestamp = int(time.time())
            params = {"access_key": self.apikey,
                      "secret_key": self.secretToken,
                      "created": timestamp,
                      "price": price,
                      "coin_type": 1,
                      "amount": amount,
                      "method": self.url['buy']}
            sign = signature(params)
            params['sign'] = sign
            del params['secret_key']
            if tradePassword:
                params['trade_password'] = tradePassword
            if tradeid:
                params['trade_id'] = tradeid

            payload = urlparse.urlencode(params)
            r = requests.post("http://" + self.url['host'], params=payload)
            if r.status_code == 200:
                data = r.json()
                return data
            else:
                return None

    def bidMakerOnly(self, amount, price):
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'amount': amount, 'price': price, 'api_key': self.apikey,
                       'secret_key': self.secretToken, 'type': 'buy_maker_only'}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['trade'], payload)

    def askMakerOnly(self, amount, price):
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'amount': amount, 'price': price, 'api_key': self.apikey,
                       'secret_key': self.secretToken, 'type': 'sell_maker_only'}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['trade'], payload)




    def sell(self, amount, price, tradePassword=None,
             tradeid=None, type='market'):
        # BTFNX
        if self.role == 'btfnx':
            payload = {'request': self.trim_uri(self.url['new_order']),
                       'nonce': self._create_nonce(),
                       'symbol': config.btfnx_symbol,
                       'amount': amount,
                       'price': price,
                       'side': 'sell',
                       'type': type
                       }
            signedPayload = self.create_bfnx_payload(payload)
            return requestPost(self.url['new_order'], payload, headers=signedPayload)
        # KRN
        if self.role == 'krn':
            payload ={
                'pair': config.krn_pair,
                'type': 'sell',
                'ordertype': type,
                'volume': amount,
            }
            signedPayload = self.create_krn_payload(payload)
            return requestPost(self.url['new_order'], payload,
                               headers=signedPayload)
        # HAOBTC
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'amount': amount, 'price': price, 'api_key': self.apikey,
                       'secret_key': self.secretToken, 'type': 'sell'}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['trade'], payload)
        # OKCoin
        if self.role == 'okcoin':
            body = requestBody(self.url['trade'], self.url['host'])
            params = {
                'api_key': self.apikey,
                'symbol': 'btc_cny',
                'type': 'sell'
            }
            if price:
                params['price'] = price
            if amount:
                params['amount'] = amount

            params['sign'] = buildSign(params, self.secretToken, self.role)
            r = httpPost(self.url['host'], body, params)
            if r:
                return json.loads(r)
            else:
                return None
        # HUOBI
        if self.role == 'huobi':
            timestamp = int(time.time())
            params = {"access_key": self.apikey,
                      "secret_key": self.secretToken,
                      "created": timestamp,
                      "price": price,
                      "coin_type": 1,
                      "amount": amount,
                      "method": self.url['sell']}
            sign = signature(params)
            params['sign'] = sign
            del params['secret_key']
            if tradePassword:
                params['trade_password'] = tradePassword
            if tradeid:
                params['trade_id'] = tradeid

            payload = urlparse.urlencode(params)
            r = requests.post("http://" + self.url['host'], params=payload)
            if r and r.status_code == 200:
                data = r.json()
                return data
            else:
                return None

    def marketBuy(self, amount, price=None):
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'amount': amount, 'api_key': self.apikey,
                       'secret_key': self.secretToken, 'type': 'buy_market'}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['trade'], payload)

        if self.role == 'okcoin':
            body = requestBody(self.url['trade'], self.url['host'])
            params = {
                'api_key': self.apikey,
                'symbol': 'btc_cny',
                'type': 'buy_market'
            }
            if price:
                params['price'] = price
            if amount:
                params['amount'] = amount

            params['sign'] = buildSign(params, self.secretToken, self.role)
            r = httpPost(self.url['host'], body, params)
            if r:
                return json.loads(r)
            else:
                return None

        if self.role == 'huobi':
            timestamp = int(time.time())
            params = {"access_key": self.apikey,
                      "secret_key": self.secretToken,
                      "created": timestamp,
                      "coin_type": 1,
                      "amount": amount,
                      "method": self.url['buy_market'],
                      }
            sign = signature(params)
            params['sign'] = sign
            del params['secret_key']
            payload = urlparse.urlencode(params)
            r = requests.post("http://" + self.url['host'], params=payload)
            if r.status_code == 200:
                data = r.json()
                return data
            else:
                return None

    def marketSell(self, amount, price=None):
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'amount': amount, 'api_key': self.apikey,
                       'secret_key': self.secretToken, 'type': 'sell_market'}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['trade'], payload)

        if self.role == 'okcoin':
            body = requestBody(self.url['trade'], self.url['host'])
            params = {
                'api_key': self.apikey,
                'symbol': 'btc_cny',
                'type': 'buy_market'
            }
            if price:
                params['price'] = price
            if amount:
                params['amount'] = amount

            params['sign'] = buildSign(params, self.secretToken, self.role)
            r = httpPost(self.url['host'], body, params)
            if r:
                return json.loads(r)
            else:
                return None

        if self.role == 'huobi':
            timestamp = int(time.time())
            params = {"access_key": self.apikey,
                      "secret_key": self.secretToken,
                      "created": timestamp,
                      "coin_type": 1,
                      "amount": amount,
                      "method": self.url['sell_market'],
                      }
            sign = signature(params)
            params['sign'] = sign
            del params['secret_key']
            payload = urlli(params)
            r = requests.post("http://" + self.url['host'], params=payload)
            if r.status_code == 200:
                data = r.json()
                return data
            else:
                return None

    def cancel(self, id):
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'api_key': self.apikey, "order_id": id}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['cancel_order'], payload)

        if self.role == 'okcoin':
            body = requestBody(self.url['cancel_order'], self.url['host'])
            params = {
                'api_key': self.apikey,
                'symbol': 'btc_cny',
                'order_id': id
            }

            params['sign'] = buildSign(params, self.secretToken, self.role)
            r = httpPost(self.url['host'], body, params)
            if r:
                return json.loads(r)
            else:
                return None

        if self.role == 'huobi':
            timestamp = int(time.time())
            params = {"access_key": self.apikey,
                      "secret_key": self.secretToken,
                      "created": timestamp,
                      "coin_type": 1,
                      "method": self.url['cancel_order'],
                      "id": id}
            sign = signature(params)
            params['sign'] = sign
            del params['secret_key']
            payload = urlparse.urlencode(params)
            r = requests.post("http://" + self.url['host'], params=payload)
            if r.status_code == 200:
                data = r.json()
                return data
            else:
                return None

    def cancelAll(self):
        if self.role == 'btfnx':
            payload = {

            }
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'api_key': self.apikey}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['cancel_all'], payload)

        if self.role == '':
            return

        if self.role == '':
            return

    def orderInfo(self, id):
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'api_key': self.apikey, "order_id": id}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['order_info'], payload)

        if self.role == 'okcoin':
            body = requestBody(self.url['order_info'], self.url['host'])
            params = {
                'api_key': self.apikey,
                'symbol': 'btc_cny',
                'order_id': id
            }

            params['sign'] = buildSign(params, self.secretToken, self.role)
            r = httpPost(self.url['host'], body, params)
            if r:
                return json.loads(r)
            else:
                return None

        if self.role == 'huobi':
            timestamp = int(time.time())
            params = {"access_key": self.apikey,
                      "secret_key": self.secretToken,
                      "created": timestamp,
                      "coin_type": 1,
                      "method": self.url['order_info'],
                      "id": id}
            sign = signature(params)
            params['sign'] = sign
            del params['secret_key']
            payload = urlparse.urlencode(params)
            r = requests.post("http://" + self.url['host'], params=payload)
            if r.status_code == 200:
                data = r.json()
                return data
            else:
                return None

    def ordersInfo(self, id=''):
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'api_key': self.apikey}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['orders_info'], payload)

        if self.role == 'okcoin':
            body = requestBody(self.url['orders_info'], self.url['host'])
            params = {
                'api_key': self.apikey,
                'symbol': 'btc_cny',
                'order_id': id,
                'type': 0
            }

            params['sign'] = buildSign(params, self.secretToken, self.role)
            r = httpPost(self.url['host'], body, params)
            if r:
                return json.loads(r)
            else:
                return None

    def orderHistory(self):
        if self.role == 'okcoin':
            body = requestBody(self.url['order_history'], self.url['host'])
            params = {
                'api_key': self.apikey,
                'current_page': 1,
                'page_length': 199,
                'status': 0,
                'symbol': 'btc_cny'
            }

            params['sign'] = buildSign(params, self.secretToken, self.role)
            r = httpPost(self.url['host'], body, params)
            if r:
                return json.loads(r)
            else:
                return None

    def historyInfo(self, size):
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'api_key': self.apikey, 'size': size}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['history_info'], payload)
        if self.role == '':
            return

    def create_bfnx_payload(self, payload):
        j = json.dumps(payload)

        data = base64.standard_b64encode(
                    j.encode('utf8'))

        return {'X-BFX-APIKEY': self.apikey,
                'X-BFX-PAYLOAD': data,
                'X-BFX-SIGNATURE': sha384(data, self.secretToken)
                }
    def create_krn_payload(self, payload, uri):
        payload['nonce'] = self._create_nonce_int()
        postdata = urlparse.urlencode(payload)
        encoded = (str(payload['nonce']) + postdata).encode()
        message = uri.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.secretToken),
                             message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())
        # j = (str(payload['nonce']) + payload).encode()
        # j = json.dumps(payload)
        # j = (str(j['nonce'])+j).encode()

        # decodedSecret = base64.b64decode(self.secretToken)
        # payload1 = hashlib.sha256(j).digest()
        # payload2 = uri.encode() + payload1
        # sig = hmac.new(decodedSecret, payload2, hashlib.sha512).digest()

        return {
            'API-Key': self.apikey,
            'API-Sign': sigdigest.decode(),
        }


    def accountInfo(self):
        if self.role == 'btfnx':
            payload = {
                'request': self.url['balance'].split(self.url['host'])[1],
                'nonce': self._create_nonce()
            }
            signedPayload = self.create_bfnx_payload(payload)
            return requestPost(self.url['balance'], payload, headers=signedPayload)

        if self.role == 'krn':
            payload = {}
            signedPayload = self.create_krn_payload(payload, self.trim_uri(self.url['balance']))
            return requestPost(self.url['balance'], payload, headers=signedPayload)

        if self.role == 'haobtc' or self.role == 'default':
            payload = {'api_key': self.apikey}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestPost(self.url['account_info'], payload)

        if self.role == 'okcoin':
            params = {}
            body = requestBody(self.url['userInfo'], self.url['host'])
            params['api_key'] = self.apikey
            params['sign'] = buildSign(params, self.secretToken, 'okcoin')
            r = httpPost(self.url['host'], body, params)
            if r:
                return json.loads(r)
            else:
                return None

        if self.role == 'huobi':
            timestamp = int(time.time())  # python3 use int to replace int
            params = {"access_key": self.apikey, "secret_key": self.secretToken,
                      "created": timestamp, "method": self.url['account_info']}
            sign = signature(params)
            params['sign'] = sign
            del params['secret_key']
            payload = urlparse.urlencode(params)
            r = requests.post("http://" + self.url['host'], params=payload)
            if r.status_code == 200:
                data = r.json()
                return data
            else:
                return None

    def ticker(self, symbol=''):
        if self.role == 'btfnx':
            params = {'symbol': config.btfnx_symbol}
            return requestGet(self.url['ticker'], params)

        if self.role == 'krn':
            params = {'pair': config.krn_pair}
            return requestGet(self.url['ticker', params])

        if self.role == 'haobtc' or self.role == 'default':
            return requestGet(self.url['ticker'])

        if self.role == 'okcoin':
            body = requestBody(self.url['ticker'], self.url['host'])
            if symbol:
                params = 'symbol=%(symbol)s' % {'symbol': symbol}
            else:
                params = ''
            r = httpGet(self.url['host'], body, params)
            return r

        if self.role == 'huobi':
            return requestGet(self.url['ticker'])

    def depth(self, size=10, merge=1, symbol=''):
        params = ''
        if self.role == 'haobtc' or self.role == 'default':
            payload = {'api_key': self.apikey, 'size': size}
            payload = tradeLoad(payload, self.secretToken, self.role)
            return requestGet(self.url['depth'], payload)

        if self.role == 'okcoin':
            body = requestBody(self.url['depth'], self.url['host'])
            if symbol:
                params = 'symbol=%(symbol)s' % {'symbol': symbol}
            else:
                params = ''

            params += '&size=%(size)s&merge=%(merge)s' % {
                'size': size, 'merge': merge}
            # print params
            r = httpGet(self.url['host'], body, params)
            return r

        if self.role == 'huobi':
            # init huobi depth list to the same format as okcoin
            r = {}
            return r

    def fast_ticker(self):
        if self.role == 'default' or self.role == 'haobtc':
            return requestGet(self.url['fast_ticker'])