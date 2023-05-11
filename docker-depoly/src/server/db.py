from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Enum, CheckConstraint, and_, DateTime, Double
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from exception import InvalidAccount, InvalidOrder, InvalidTransaction, InsufficientSymbol, InsufficientFund, ExistingAccount
from datetime import datetime
from contextlib import contextmanager
import sqlalchemy as sa

engine = create_engine('postgresql://postgres:passw0rd@db:5432/hw4db')
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Account(Base):
    __tablename__ = 'Account'

    account_id = Column(Integer, primary_key=True)
    balance = Column(Double, CheckConstraint('balance >= 0'), nullable=False)
    positions = relationship('Position', backref='account')
    orders = relationship('Orders', backref='account')


class Position(Base):
    __tablename__ = 'Position'

    position_id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey(
        'Account.account_id', ondelete='CASCADE', onupdate='CASCADE'))
    symbol = Column(String, nullable=False)
    num_shares = Column(Double, nullable=False)


class Orders(Base):
    __tablename__ = 'Orders'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    trans_id = Column(Integer, nullable=True)
    account_id = Column(Integer, ForeignKey(
        'Account.account_id', ondelete='CASCADE', onupdate='CASCADE'))
    symbol = Column(String(20), nullable=False)
    num_shares = Column(Double, nullable=False)
    price_limit = Column(Double, CheckConstraint('price_limit > 0'), nullable=False)
    status = Column(Enum('open', 'canceled', 'executed',
                    name='order_status'), default='open')
    executed_at = Column(DateTime, nullable=True)


def create_tables():
    Base.metadata.create_all(bind=engine)


def delete_tables():
    Base.metadata.reflect(bind=engine)
    Base.metadata.drop_all(bind=engine)


def get_session():
    engine = create_engine(
        'postgresql://postgres:passw0rd@db:5432/hw4db')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


@contextmanager
def session_scope():
    session = get_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def account_exists(session, account_id):
    account = session.query(Account).filter(
        Account.account_id == account_id).first()
    if account:
        return 1
    else:
        return 0


def create_account(account_id, balance):
    with session_scope() as session:
        if account_exists(session, account_id) == 0:
            new_account = Account(account_id=account_id, balance=balance)
            session.add(new_account)
        else:
            raise ExistingAccount(account_id)


def create_position(account_id, symbol, num_shares):
    with session_scope() as session:
        if account_exists(session, account_id) == 0:
            raise InvalidAccount(account_id)
        position = session.query(Position).filter(
            Position.account_id == account_id, Position.symbol == symbol).first()
        if position is None:
            new_order = Position(account_id=account_id, symbol=symbol,
                                 num_shares=num_shares)
            session.add(new_order)
        else:
            position.num_shares += num_shares


def sufficient_asset(session, account_id, symbol, amount):
    symbol_query = session.query(Position).filter_by(
        account_id=account_id, symbol=symbol).first()
    if symbol_query:
        if symbol_query.num_shares < abs(amount):
            raise InsufficientSymbol(account_id, symbol)
        else:
            pass
    else:
        raise InsufficientSymbol(account_id, symbol)


def sufficient_balance(session, account_id, amount, limit, symbol):
    balance_query = session.query(Account).filter_by(
        account_id=account_id).first()
    if balance_query.balance < (amount * limit):
        raise InsufficientFund(account_id, symbol)
    else:
        pass


def process_order(account_id, symbol, amount, limit, transaction):
    with session_scope() as session:
        if account_exists(session, account_id) == 0:
            raise InvalidAccount(account_id)

        if amount < 0:
            sufficient_asset(session, account_id, symbol, amount)
            process_sell_order(session, account_id, symbol,
                               amount, limit, transaction)

        elif amount > 0:
            sufficient_balance(session, account_id, amount, limit, symbol)
            process_buy_order(session, account_id, symbol,
                              amount, limit, transaction)

        else:
            raise InvalidOrder(account_id)


def process_sell_order(session, account_id, symbol, amount, limit, transaction):
    # update seller's position
    seller_position = session.query(Position).filter_by(
        account_id=account_id, symbol=symbol).first()
    seller_position.num_shares += amount
    # execute
    open_buy_orders = session.query(Orders).filter_by(symbol=symbol, status='open')\
        .filter(Orders.price_limit >= limit) \
        .filter(Orders.num_shares > 0) \
        .order_by(Orders.price_limit.desc(), Orders.order_id.asc()).all()
    if len(open_buy_orders) <= 0:
        session.add(Orders(account_id=account_id, symbol=symbol, num_shares=amount,
                           price_limit=limit, status='open', trans_id=transaction))
    else:
        for buy_order in open_buy_orders:
            # there is more buy than sell buy>sell
            if buy_order.num_shares >= abs(amount):
                # update buyer's position
                buyer_position = session.query(Position).filter_by(
                    account_id=buy_order.account_id, symbol=symbol).first()
                if buyer_position:
                    new_num_shares = buyer_position.num_shares + \
                        abs(amount)
                    buyer_position.num_shares = new_num_shares
                else:
                    session.add(Position(
                        account_id=buy_order.account_id, symbol=symbol, num_shares=abs(amount)))

                # update seller's account
                seller_account = session.query(Account).filter_by(
                    account_id=account_id).first()
                seller_account.balance += (
                    buy_order.price_limit * abs(amount))

                # add sell orders
                session.add(Orders(account_id=account_id, symbol=symbol, num_shares=amount,
                                   price_limit=buy_order.price_limit, status='executed', executed_at=datetime.now(), trans_id=transaction))
                # update buyer orders. If the shares from buy order is greater than sell order
                if buy_order.num_shares - abs(amount) > 0:
                    session.add(Orders(account_id=buy_order.account_id, symbol=symbol, num_shares=buy_order.num_shares-abs(amount),
                                       price_limit=buy_order.price_limit, status='open', trans_id=buy_order.trans_id))
                else:
                    pass

                buy_order.status = 'executed'
                buy_order.executed_at = datetime.now()
                buy_order.num_shares = abs(amount)

                break

            else:
                # there is more sell than buy sell>buy
                # update buyer position
                _current_index = 0
                buyer_position = session.query(Position).filter_by(
                    account_id=buy_order.account_id, symbol=symbol).first()
                if buyer_position:
                    new_num_shares = buyer_position.num_shares + buy_order.num_shares
                    buyer_position.num_shares = new_num_shares
                else:
                    session.add(Position(account_id=buy_order.account_id,
                                symbol=symbol, num_shares=buy_order.num_shares))

                # update seller's account
                _seller_account = session.query(Account).filter_by(
                    account_id=account_id).first()
                _seller_account.balance += (buy_order.price_limit *
                                            buy_order.num_shares)

                # add seller order

                if _current_index == len(open_buy_orders) - 1:
                    session.add(Orders(account_id=account_id, symbol=symbol, num_shares=- (buy_order.num_shares),
                                       price_limit=buy_order.price_limit, status='executed', executed_at=datetime.now(), trans_id=transaction))
                    session.add(Orders(account_id=account_id, symbol=symbol, num_shares=buy_order.num_shares-abs(amount),
                                       price_limit=limit, status='open', trans_id=transaction))
                else:
                    session.add(Orders(account_id=account_id, symbol=symbol, num_shares=- (buy_order.num_shares),
                                       price_limit=buy_order.price_limit, status='executed', executed_at=datetime.now(), trans_id=transaction))

                # update buyer order
                buy_order.status = 'executed'
                buy_order.executed_at = datetime.now()
                amount += buy_order.num_shares
                _current_index += 1


def process_buy_order(session, account_id, symbol, amount, limit, transaction):
    # update buyer's account
    buyer_account = session.query(Account).filter_by(
        account_id=account_id).first()
    buyer_account.balance -= (limit * amount)
    # execute

    open_sell_orders = session.query(Orders).filter_by(symbol=symbol, status='open')\
        .filter(Orders.price_limit <= limit) \
        .filter(Orders.num_shares < 0) \
        .order_by(Orders.price_limit.asc(), Orders.order_id.asc()).all()
    if len(open_sell_orders) <= 0:
        session.add(Orders(account_id=account_id, symbol=symbol, num_shares=amount,
                           price_limit=limit, status='open', trans_id=transaction))
    else:
        for sell_order in open_sell_orders:

            if sell_order.price_limit < limit:
                # refund is given to the buyer because buying price is lower than the selling price
                if abs(sell_order.num_shares) >= amount:
                    print('a')
                    buy_order_no_split_purchase_lower(
                        session, sell_order, account_id, symbol, amount, limit, transaction)
                    break
                else:
                    buy_order_split_purchase_lower(
                        session, open_sell_orders, sell_order, account_id, symbol, amount, limit, transaction)
                    print('b')
                # no refund is given to the buyer because buying price matches selling price
            else:
                if abs(sell_order.num_shares) >= amount:
                    buy_order_no_split(
                        session, sell_order, account_id, symbol, amount, limit, transaction)
                    print('c')
                    break
                else:
                    buy_order_split(session, open_sell_orders, sell_order,
                                    account_id, symbol, amount, limit, transaction)
                    print('d')


def process_cancel(trans_id, account_id):
    with session_scope() as cancel_session:
        transactions = cancel_session.query(Orders).filter_by(
            trans_id=trans_id, account_id=account_id).all()
        if not transactions:
            raise InvalidTransaction(trans_id)
        try:
            for transaction in transactions:
                if transaction.status == 'open':
                    transaction.status = 'canceled'
                    transaction.executed_at = datetime.now()
                    if transaction.num_shares > 0:  # cancel buy order
                        account = cancel_session.query(Account).filter_by(
                            account_id=account_id).one_or_none()
                        if account:
                            account.balance += (transaction.num_shares *
                                                transaction.price_limit)
                        else:
                            raise InvalidTransaction(trans_id)
                    elif transaction.num_shares < 0:  # cancel sell order
                        position = cancel_session.query(Position).filter(
                            Position.account_id==account_id,Position.symbol==transaction.symbol).one_or_none()
                        if position:
                            position.num_shares += abs(transaction.num_shares)
                        else:
                            raise InvalidTransaction(trans_id)
                    else:
                        raise InvalidTransaction(trans_id)

            transactions = cancel_session.query(Orders).filter_by(
                trans_id=trans_id, account_id=account_id).all()
            query_results = []
            for transaction in transactions:
                query_results.append({'status':transaction.status,'num_shares':transaction.num_shares,'price_limit':transaction.price_limit,'executed_at':transaction.executed_at})
            #cancel_session.commit()
            #for transaction in query_results:
            #    cancel_session.refresh(transaction)
            return query_results

        except Exception as e:
            cancel_session.rollback()
            raise e


def process_query(trans_id, account_id):
    with session_scope() as query_session:
        transaction_query = query_session.query(Orders).filter_by(
            trans_id=trans_id, account_id=account_id).first()
        if transaction_query is None:
            raise InvalidTransaction(trans_id)
        else:
            query = query_session.query(Orders.num_shares, Orders.price_limit, Orders.status, Orders.executed_at)\
                .filter(and_(Orders.trans_id == trans_id, Orders.account_id == account_id)).all()
        return query


def buy_order_no_split(session, sell_order, account_id, symbol, amount, limit, transaction):
    # update buyer's position
    buyer_position = session.query(Position).filter_by(
        account_id=account_id, symbol=symbol).first()
    if buyer_position:
        new_num_shares = buyer_position.num_shares + amount
        buyer_position.num_shares = new_num_shares
    else:
        session.add(Position(account_id=account_id,
                    symbol=symbol, num_shares=(amount)))

    # update seller's position
    # seller_position = session.query(Position).filter_by(account_id=sell_order.account_id, symbol=symbol).first()
    # seller_position.num_shares -= amount

    # update seller's account
    seller_account = session.query(Account).filter_by(
        account_id=sell_order.account_id).first()
    seller_account.balance += (limit * amount)

    # add buy orders
    session.add(Orders(account_id=account_id, symbol=symbol, num_shares=amount,
                       price_limit=limit, status='executed', executed_at=datetime.now(), trans_id=transaction))
    # update seller orders. If the shares from sell order is greater than buy order
    if abs(sell_order.num_shares) - amount > 0:
        session.add(Orders(account_id=sell_order.account_id, symbol=symbol, num_shares=-(abs(sell_order.num_shares)-amount),
                           price_limit=sell_order.price_limit, status='open', trans_id=sell_order.trans_id))
    else:
        pass

    sell_order.status = 'executed'
    sell_order.executed_at = datetime.now()
    sell_order.num_shares = -amount
    sell_order.price_limit = limit


def buy_order_split(session, open_sell_orders, sell_order, account_id, symbol, amount, limit, transaction):
    current_index = 0
    # update buyer position
    buyer_position = session.query(Position).filter_by(
        account_id=account_id, symbol=symbol).first()
    if buyer_position:
        new_num_shares = buyer_position.num_shares + abs(sell_order.num_shares)
        buyer_position.num_shares = new_num_shares
    else:
        session.add(Position(account_id=account_id, symbol=symbol,
                    num_shares=sell_order.num_shares))

    # update seller position
    # seller_position = session.query(Position).filter_by(account_id=sell_order.account_id, symbol=symbol).first()
    # seller_position.num_shares -= abs(sell_order.num_shares)

    # update seller's account
    _seller_account = session.query(Account).filter_by(
        account_id=sell_order.account_id).first()
    _seller_account.balance += (limit * abs(sell_order.num_shares))

    # add buyer order

    if current_index == len(open_sell_orders) - 1:
        session.add(Orders(account_id=account_id, symbol=symbol, num_shares=amount - abs(sell_order.num_shares),
                           price_limit=limit, status='open', trans_id=transaction))
        session.add(Orders(account_id=account_id, symbol=symbol, num_shares=abs(sell_order.num_shares),
                           price_limit=limit, status='executed', executed_at=datetime.now(), trans_id=transaction))
    else:
        session.add(Orders(account_id=account_id, symbol=symbol, num_shares=amount - abs(sell_order.num_shares),
                           price_limit=limit, status='open', trans_id=transaction))

    # update seller order
    sell_order.status = 'executed'
    sell_order.executed_at = datetime.now()
    sell_order.price_limit = limit
    amount -= abs(sell_order.num_shares)
    current_index += 1


def buy_order_no_split_purchase_lower(session, sell_order, account_id, symbol, amount, limit, transaction):
    # update buyer's position
    buyer_position = session.query(Position).filter_by(
        account_id=account_id, symbol=symbol).first()
    if buyer_position:
        new_num_shares = buyer_position.num_shares + amount
        buyer_position.num_shares = new_num_shares
    else:
        session.add(Position(account_id=account_id,
                    symbol=symbol, num_shares=(amount)))

    # update seller's position
    # seller_position = session.query(Position).filter_by(account_id=sell_order.account_id, symbol=symbol).first()
    # seller_position.num_shares -= amount

    # update seller's account
    seller_account = session.query(Account).filter_by(
        account_id=sell_order.account_id).first()
    seller_account.balance += (sell_order.price_limit * amount)

    # update buyer's account
    buyer_account = session.query(Account).filter_by(
        account_id=account_id).first()
    buyer_account.balance += (limit-sell_order.price_limit) * amount
    print((limit-sell_order.price_limit) * amount)

    # add buy orders
    session.add(Orders(account_id=account_id, symbol=symbol, num_shares=amount,
                       price_limit=sell_order.price_limit, status='executed', executed_at=datetime.now(), trans_id=transaction))
    # update seller orders. If the shares from sell order is greater than buy order
    if abs(sell_order.num_shares) - amount > 0:
        session.add(Orders(account_id=sell_order.account_id, symbol=symbol, num_shares=-(abs(sell_order.num_shares)-amount),
                           price_limit=sell_order.price_limit, status='open', trans_id=sell_order.trans_id))
    else:
        pass

    sell_order.status = 'executed'
    sell_order.executed_at = datetime.now()
    sell_order.num_shares = -amount


def buy_order_split_purchase_lower(session, open_sell_orders, sell_order, account_id, symbol, amount, limit, transaction):
    current_index = 0
    # update buyer position
    buyer_position = session.query(Position).filter_by(
        account_id=account_id, symbol=symbol).first()
    if buyer_position:
        new_num_shares = buyer_position.num_shares + abs(sell_order.num_shares)
        buyer_position.num_shares = new_num_shares
    else:
        session.add(Position(account_id=account_id, symbol=symbol,
                    num_shares=sell_order.num_shares))

    # update seller position
    # seller_position = session.query(Position).filter_by(account_id=sell_order.account_id, symbol=symbol).first()
    # seller_position.num_shares -= abs(sell_order.num_shares)

    # update seller's account
    seller_account = session.query(Account).filter_by(
        account_id=sell_order.account_id).first()
    seller_account.balance += (sell_order.price_limit *
                               abs(sell_order.num_shares))

    # update buyer's account
    buyer_account = session.query(Account).filter_by(
        account_id=account_id).first()
    buyer_account.balance += (limit-sell_order.price_limit) * \
        abs(sell_order.num_shares)
    print((limit-sell_order.price_limit)*abs(sell_order.num_shares))

    # add buyer order

    if current_index == len(open_sell_orders) - 1:
        session.add(Orders(account_id=account_id, symbol=symbol, num_shares=amount - abs(sell_order.num_shares),
                           price_limit=limit, status='open', trans_id=transaction))
        session.add(Orders(account_id=account_id, symbol=symbol, num_shares=abs(sell_order.num_shares),
                           price_limit=sell_order.price_limit, status='executed', executed_at=datetime.now(), trans_id=transaction))
    else:
        session.add(Orders(account_id=account_id, symbol=symbol, num_shares=amount - abs(sell_order.num_shares),
                           price_limit=limit, status='open', trans_id=transaction))

    # update seller order
    sell_order.status = 'executed'
    sell_order.executed_at = datetime.now()
    amount -= abs(sell_order.num_shares)
    current_index += 1


def getTotalBalance():
    balance = 0
    with session_scope() as session:
        account_balance = session.query(sa.func.sum(Account.balance)).scalar()
        position_balance = session.query(sa.func.sum(Orders.num_shares*Orders.price_limit)).filter(Orders.status=='open',Orders.num_shares>0).scalar()
        if account_balance is not None:
            balance+=account_balance
        if position_balance is not None:
            balance+=position_balance

    return balance