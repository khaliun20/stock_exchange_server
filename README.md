# Scalable Stock Exchange Server

## Project Overview

This project implements an exchange matching engine with database (PostgreSQL), which matches buy and sell orders for a stock/commodities market. The engine supports account management, order creation, matching, execution, cancellation, and querying. The server communicates using XML over TCP and follows a specific protocol to handle requests and responses.

**Tech used: Python, Docker, Docker-compose, PostgreSQL, SQLAlchemy, TCP Sockets**

## Features

1. **Account Management**: Create and manage accounts with unique IDs and balances.
2. **Symbol Management**: Create and manage symbols representing stocks or commodities.
3. **Order Management**: Place, execute, cancel, and query orders for buying and selling symbols.
4. **Order Matching**: Match buy and sell orders based on limit prices and execution rules.
5. **Error Handling**: Handle errors gracefully and provide informative error messages.

## Communication 

* The server listens for incoming connections on port 12345. Clients send requests in the following XML format. 
* XML is used as the primary data format for communication between clients and the server.
    * XML (eXtensible Markup Language) is chosen for its flexibility and ability to structure complex data in a readable format.
    * Each request and response is encapsulated within XML tags to ensure that data is self-descriptive and easy to parse.
    * Example XML request to create an account with a balance and initialize it with stocks.
         ```xml
        <create>
            <account id="ACCOUNT_ID" balance="BALANCE"/> #0 or more
            <symbol sym="SPY"> #0 or more
                <account id="11">100000</account> # 1 or more
            </symbol>
        </create>
        ```
    * Example XML response: 
         ```xml
        <results>
             <created id="ACCOUNT_ID"/> #For account create
             <created sym="SYM" id="ACCOUNT_ID"/> #For symbol create
             <error id="ACCOUNT_ID">Msg</error> #For account create error
                 <error sym="SYM" id="ACCOUNT_ID">Msg</error> #For symbol create error
         </results>
        ```

      * Example XML for transaction requests:
        ```xml
        <transactions id="ACCOUNT_ID"> #contains 1 or more of the below
        children
            <order sym="SYM" amount="AMT" limit="LMT"/>
            <query id="TRANS_ID">
            <cancel id="TRANS_ID">
        </transactions>
        ```
        
      * Example XML for transaction response:
        ```xml

        <results>
            <opened sym="SYM" amount="AMT" limit="LMT" id="TRANS_ID"/>
            <error sym="SYM" amount="AMT" limit="LMT">Message</error> #Note there is 1 error for every order/query/cancel of the transactions tag if ID is invalid
            <status id="TRANS_ID">
                <open shares=.../>
                <canceled shares=... time=.../>
                <executed shares=... price=... time=.../>
            </status>
            <canceled id="TRANS_ID">
                <canceled shares=... time=.../>
                <executed shares=... price=... time=.../>
                </canceled>
        </results>
        ```

## To scalability tests: 

Navigate to the `testing` directory and run the provided test scripts to analyze the server's performance across different CPU core counts.

Set the number of tests to generate in generate_tests.py 
    N = 5000 for example
Run python3 generate_tests.py
While server is running run python3 client.py
