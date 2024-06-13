# Scalable Stock Exchange Server

## Project Overview

In this project, I developed the backend of a small stock exchange server program that can handle thousands of concurrent transaction requests from buyer and sellers at the same time.

*     Buyers and sellers create account on the server and deposit funds to start the market.
*     Participants are matched on the market based on their selling and buying prices, and their transactions are recorded in the database, PostgreSQL.
*     I used SQLAlchemy to interact with the database.
*     After each transaction, buyers' and sellers' account balances are updated to reflect the transactions.

## Communication 

* Buyers and sellers make TCP connection requests with the server.
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

## To run the test
Set the number of tests to generate in generate_tests.py 
    N = 5000 for example
Run python3 generate_tests.py
While server is running run python3 client.py
