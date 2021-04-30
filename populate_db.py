"""
Populate the Edgar database.
Assumes the database and tables have already been created.
"""

import argparse
import logging
import os
import requests
import sys

import psycopg2

logger = logging.getLogger(__name__)

# Income table columns.
COLUMNS = ["symbol",
    "fillingDate",
    "period",
    "revenue", 
    "costOfRevenue", 
    "grossProfit", 
    "grossProfitRatio", 
    "researchAndDevelopmentExpenses", 
    "generalAndAdministrativeExpenses", 
    "sellingAndMarketingExpenses",
    "otherExpenses", 
    "operatingExpenses", 
    "costAndExpenses", 
    "interestExpense", 
    "depreciationAndAmortization", 
    "ebitda", 
    "ebitdaratio", 
    "operatingIncome", 
    "operatingIncomeRatio",
    "totalOtherIncomeExpensesNet", 
    "incomeBeforeTax", 
    "incomeBeforeTaxRatio", 
    "incomeTaxExpense", 
    "netIncome", 
    "netIncomeRatio", 
    "eps", 
    "epsdiluted", 
    "weightedAverageShsOut", 
    "weightedAverageShsOutDil"]

# Load credentials from environment. 
POSTGRES_ADDRESS = os.environ['POSTGRES_ADDRESS']
POSTGRES_PORT = os.environ['POSTGRES_PORT']
POSTGRES_USERNAME = os.environ['POSTGRES_USERNAME']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_DBNAME = os.environ['POSTGRES_DBNAME']
FMP_KEY = os.environ['FMP_KEY']


def populate_db(symbols):
    """Populate the database with financial data for the given list of symbols."""
    # Create connection and cursor    
    conn = psycopg2.connect(host=POSTGRES_ADDRESS,
                    database=POSTGRES_DBNAME,
                    user=POSTGRES_USERNAME,
                    password=POSTGRES_PASSWORD,
                    port=POSTGRES_PORT)
    cursor = conn.cursor()

    for symbol in symbols:
        logger.info("Processing symbol: {}".format(symbol))
        query_symbol(conn, cursor, symbol)


def query_symbol(conn, cursor, symbol):
    """Query and upload data for the requested symbol."""
    # Format the financialmodelingprep.com API endpoint
    # Docs: https://financialmodelingprep.com/developer/docs/#Company-Financial-Statements
    URL = "https://financialmodelingprep.com/api/v3/income-statement/{}".format(symbol)

    # Parameterize and send the request.
    query_params = {
        "limit": 10,
        "apikey": FMP_KEY,
    }
    response = requests.get(url=URL, params=query_params)
    records = response.json()

    if "Error Message" in records:
        print(records["Error Message"])
        return
        raise ValueError(records["Error Message"])

    for record in records:
        # Execute and commit insert
        data = [record[name] for name in COLUMNS]
        insert_query = """INSERT INTO income ({columns}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""".format(columns=", ".join(COLUMNS))
        cursor.execute(insert_query, data)
        conn.commit()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--symbols", default="symbols.txt",
        help="Path to file containing stock ticker symbols.")
    args = parser.parse_args()
    
    with open(args.symbols, 'r') as f:
        symbols = [symbol.strip() for symbol in f.readlines()]
    populate_db(symbols)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())