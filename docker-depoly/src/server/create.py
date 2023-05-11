import xml.etree.ElementTree as ET
from db import create_account, create_position
from exception import InvalidAccount, ExistingAccount


def handle_create(eTree: ET.ElementTree):

    root = eTree.getroot()
    response = ET.Element('results')
    for child_elem in root:
        if child_elem.tag == 'account':
            account_id = child_elem.attrib['id']
            balance = float(child_elem.attrib['balance'])

            try:
                create_account(account_id, balance)
                createdAccount = ET.Element('created', id=str(account_id))
                response.append(createdAccount)

            except ExistingAccount as e:
                error = ET.Element('error', id=str(account_id))
                error.text = str(e)
                response.append(error)
                print(str(e))

        elif child_elem.tag == 'symbol':
            symbol = child_elem.attrib['sym']
            for account in child_elem:
                account_id = account.attrib['id']
                num_shares = float(account.text)
                try:
                    create_position(account_id, symbol, num_shares)
                    createdPosition = ET.Element(
                        'created', sym=symbol, id=str(account_id))
                    response.append(createdPosition)


                except InvalidAccount as e:
                    error = ET.Element('error', sym=symbol, id=str(account_id))
                    error.text = str(e)
                    response.append(error)

    response_str = ET.tostring(response)
    return response_str
