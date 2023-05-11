import xml.etree.ElementTree as ET
from db import process_order, process_query, process_cancel
from exception import InvalidAccount, InvalidOrder, InvalidTransaction, InsufficientSymbol, InsufficientFund
from multiprocessing import Value,Lock
transaction = Value('i',1 )
lock = Lock()


def handle_transaction(eTree: ET.ElementTree):

    global transaction
    root = eTree.getroot()
    account_id = root.get('id')
    response = ET.Element('results')
    for child_elem in root:
        if child_elem.tag == 'order':
            symbol = child_elem.attrib['sym']
            amount = float(child_elem.attrib['amount'])
            limit = float(child_elem.attrib['limit'])

            try:
                process_order(account_id, symbol, amount, limit, transaction.value)
                with lock:
                    opened = ET.Element('opened', sym=symbol, amount=str(amount), limit=str(limit), id=str(transaction.value))
                    response.append(opened)
                    transaction.value +=1
                

            except InvalidAccount as e:
                error = ET.Element('error', sym=symbol, amount=str(amount), limit=str(limit))
                error.text=str(e)
                response.append(error)
                print(str(e))

            except InvalidOrder as e:
                error = ET.Element('error', sym=symbol, amount=str(amount), limit=str(limit))
                error.text=str(e)
                response.append(error) 
                print(str(e))

            except InsufficientSymbol as e:
                error = ET.Element('error', sym=symbol, amount=str(amount), limit=str(limit))
                error.text=str(e)
                response.append(error)
                print(str(e))   
            
            except InsufficientFund as e:
                error = ET.Element('error', sym=symbol, amount=str(amount), limit=str(limit))
                error.text=str(e)
                response.append(error)
                print(str(e))             


        elif child_elem.tag == 'query':
            trans_id = child_elem.attrib['id']

            try:
                queries = process_query(trans_id, account_id)
                parent_status = ET.Element('status', id = str(trans_id))

                for query in queries:
                    if query.status == 'open':
                        opened= ET.Element('open', shares=str(abs(query.num_shares)))
                        parent_status.append(opened)
                    elif query.status == 'canceled':
                        canceled = ET.Element('canceled', shares=str(abs(query.num_shares)))
                        parent_status.append(canceled)
                    elif query.status == 'executed':
                        executed = ET.Element('executed', shares=str(abs(query.num_shares)), price = str(query.price_limit), time = str(int(query.executed_at.timestamp()) ))
                        parent_status.append(executed)
                    else:
                        raise InvalidTransaction (trans_id)
                response.append(parent_status)

            except InvalidTransaction as e:
                error = ET.Element('error', trans_id=str(trans_id))
                error.text = str(e)
                response.append(error)

        elif child_elem.tag == 'cancel':
            trans_id = child_elem.attrib['id']
            canceled_parent= ET.Element('canceled', id = str(trans_id))

            try:
                query_tuples = process_cancel(trans_id, account_id)
                
                for query_tuple in query_tuples:
                    if query_tuple['status'] == 'canceled':
                        canceled_child = ET.Element('canceled', shares=str(abs(query_tuple['num_shares'])), time = str(int(query_tuple['executed_at'].timestamp())))
                        canceled_parent.append(canceled_child)
                    else:
                        pass
                    if query_tuple['status'] == 'executed':
                        executed = ET.Element('executed', shares=str(abs(query_tuple['num_shares'])), price = str(query_tuple['price_limit']), time = str(int((query_tuple['executed_at'].timestamp()))))
                        canceled_parent.append(executed)
                    else:
                        pass        
                response.append(canceled_parent)
            
            except InvalidTransaction as e:
                error = ET.Element('error', trans_id=str(trans_id))
                error.text = str(e)
                response.append(error)
                print(str(e)) 

        else:
            error = ET.Element('error')
            error.text = 'No order, query, or cancel elements found in the XML'
            response.append(error)

    response_str = ET.tostring(response) 
    return response_str
        


        