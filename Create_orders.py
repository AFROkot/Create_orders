import ccxt 
import random

binace_auth_data = {'apiKey': 'aliF1AwgamcjxBgWWrmznNRWxkyAfUH0OFxq7vPswxHGf0DfpxUkwzAiQ4V2hddf',
                   'secret': 'PEtCQUqxL1bNZ1w3Getx1iMKPql8ynd8Y6XTxwl1t31OYAG6ylkefb4hb6CZnFiF'}

exchange = ccxt.binance(binace_auth_data)
exchange.rateLimit = 0
exchange.set_sandbox_mode(True)
market = exchange.load_markets()

def chek_balance(ps):
    balance = exchange.fetch_balance()
    if ps['side'] == 'SELL':
        
        if balance[ps['symbol'][:ps['symbol'].find("/")]]['free'] * exchange.fetch_order_book(ps['symbol'])['bids'][0][0] > volume['volume']:
            return True
        
        else: 
            print('Недостаточно средств')
            return False
        
    elif balance[ps['symbol'][ps['symbol'].find("/")+1:]]['free'] > volume['volume']:
        return True
    else:
        print('Недостаточно средств')
        return False
    

def order_volums(ps):
    vol = ps['volume']
    numb = ps['number']
    amount = ps['amountDif']
    
    order_vol=[]
    amountMin = vol // numb - amount
    amountMax = vol // numb + amount
    
    if amount < 0:
        return print('Отрицательное значение amountDif')
    
    elif amountMin <= 0:
        return print('Не корректное значение amountDif или number')
    
    for i in range(numb-1):
        base_price = vol // numb
        
        if (base_price-amount) < amountMin :
            volume = random.randint(amountMin,base_price+amount)
            
        elif (base_price+amount) > amountMax > base_price-amount:
            volume = random.randint(base_price-amount,amountMax)
        
        else: volume = random.randint(base_price-amount,base_price+amount)
        
        vol -= volume
        numb -= 1
        order_vol.append(volume)
    order_vol.append(int(vol))

    if amountMin <= order_vol[-1] <= amountMax:
        result = order_vol
    else: 
        result = order_volums(ps)
    return result

def order_prices(ps):
    prices = []
    symbol = ps['symbol']
    
    for i in range(ps['number']):
    
        if exchange.markets[symbol]['limits']['price']['min'] > ps['priceMin']:
            print('Цена ниже минимальной')

        elif exchange.markets[symbol]['limits']['price']['max'] < ps['priceMax']:
            print('Цена выше максимальной')

        prices.append(round(random.uniform(ps['priceMin'],ps['priceMax']),exchange.markets[symbol]['precision']['price']))
    return prices

def create_orders(ps):
    
    if  chek_balance(ps):
        number = ps['number']
        symbol = ps['symbol']
        type_order = 'limit'
        side = ps['side']
        amount_list = order_volums(ps)
        price_list = order_prices(ps)
        
        for i in range(ps['number']):
            exchange.create_order(symbol,
                                  type_order,
                                  side,
                                  round(amount_list[i]/price_list[i],exchange.markets[symbol]['precision']['amount']),
                                  price_list[i])
            
            print('exchange.create_order(',
                  symbol,
                  type_order,
                  side,
                  round(amount_list[i]/price_list[i],exchange.markets[symbol]['precision']['amount']),
                  price_list[i],
                  ')')
                
				
def test_volums(ps):
    volums = order_volums(ps)

    assert len(volums) == ps['number']  # проверка количества

    assert ps['volume'] == sum(volums)  # проверка на соответствие суммарного баланса

    base_price = ps['volume'] / ps['number']
    for i in volums:  # проверка на соответствие диапазону
        assert base_price - ps['amountDif'] <= i <= base_price + ps['amountDif']


def test_prices(ps):
    prices = order_prices(ps)

    assert len(prices) == ps['number']  # проверка количества

    for i in prices:  # проверка на соответствие диапазону
        assert ps['priceMin'] <= i <= ps['priceMax']