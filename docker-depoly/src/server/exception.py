class InvalidAccount(Exception):
    def __init__(self, account_id):
        self.account_id = account_id

    def __str__(self):
        return f"Account {self.account_id} is invalid"

class InvalidTransaction(Exception):
    def __init__(self, trans_id):
        self.trans_id = trans_id

    def __str__(self):
        return f"Transaction {self.trans_id} is invalid"

class InsufficientFund(Exception):
    def __init__(self, account_id, symbol):
        self.account_id=account_id
        self.symbol=symbol

    def __str__(self):
        return f"Insufficient fund in {self.account_id} to buy {self.symbol}"


class InsufficientSymbol(Exception):
    def __init__(self, account_id, symbol):
        self.account_id=account_id
        self.symbol= symbol

    def __str__(self):
        return f"Account {self.account_id} do not have enough stock {self.symbol} to sell"

class InvalidOrder(Exception):
    def __init__(self, account_id):
        self.account_id=account_id

    def __str__(self):
        return f"Order placed by account {self.account_id} doesn't provide executable stock amount to buy/sell"
    
class ExistingAccount(Exception):
    def __init__(self, account_id):
        self.account_id=account_id

    def __str__(self):
        return f"Account {self.account_id} already exists"
    
class InvalidAccountId(Exception):
    def __init__(self, account_id):
        self.account_id=account_id

    def __str__(self):
        return f"Account id does not follow the format"
    
class InvalidSymbol(Exception):

    def __str__(self):
        return f"Symbol does not folloow the format"
    
class NegativeAmount(Exception):

    def __str__(self):
        return f"Short sales are not allowed (negative amount of stock)"