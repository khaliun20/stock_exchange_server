import xml.etree.cElementTree as ET
import random

N = 50

def generate_create_account(account_id, balance):
    account = ET.Element('account', id=str(account_id), balance=str(balance))
    return account


def generate_create_symbol(symbol, account_list):
    _symbol = ET.Element('symbol', sym=symbol)
    for ele in account_list:
        account = ET.Element('account', id=str(ele[0]))
        account.text = ele[1]
        _symbol.append(account)
    return _symbol


def generate_trans_order(symbol, amount, limit):
    order = ET.Element('order', sym=symbol,
                       amount=str(amount), limit=str(limit))
    return order


def generate_trans_cancel(trans_id):
    cancel = ET.Element('cancel', id=str(trans_id))
    return cancel


def generate_trans_query(trans_id):
    query = ET.Element('query', id=str(trans_id))
    return query


def generate_create():
    create = ET.Element('create')
    for i in range(N):
        create.append(generate_create_account(i,100000))
    for i in range(N):
        list = []
        for j in range(10):
            list.append([random.randint(0,N),"1000"])
        create.append(generate_create_symbol('sym'+str(random.randint(1,10)),list))
    create_str= ET.tostring(create).decode()
    with open("testCreate.xml",'w+') as f:
        f.write(create_str)

def generate_transactions(index):
    trans = ET.Element('transactions', id = str(random.randint(0,99)))
    for i in range(N):
        symbol = 'sym'+str(random.randint(1,10))
        amount = random.randrange(5,10)
        limit = random.randrange(5,10)
        trans.append(generate_trans_order(symbol,amount,limit))
    for i in range(N):
        trans_id = random.randrange(1,N)
        trans.append(generate_trans_query(trans_id))
    for i in range(N):
        trans_id = random.randrange(1,N)
        trans.append(generate_trans_cancel(trans_id))
    trans_str= ET.tostring(trans).decode()
    with open("testTrans"+str(index)+".xml",'w+') as f:
        f.write(trans_str)


def main():
    generate_create()
    for i in range(10):
        generate_transactions(i)
    return


if __name__ == '__main__':
    main()