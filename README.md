# Scalable Stock Exchange Server

## Project Overview

In this project, I developed a small stock exchange program (backend only) that is able to handle thousands of concurrent transactions at the same time.

Buyers and sellers create account on the server and deposit fund to start the market. Participants are matched on the market based on their selling and buying prices, and their transactions are recorded in the database, PostgreSQL. I used SQLAlchemy to interact with the database. After each transactions, buyers and sellers account balances are updated to reflect the transactions.


## To run the program


## To run the test
Set the number of tests to generate in generate_tests.py 
    N = 5000 for example
Run python3 generate_tests.py
While server is running run python3 client.py
