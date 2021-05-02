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

# Profile table columns.
PROFILE_COLUMNS = [
    "symbol",
    "price",
    "beta",
    "volAvg",
    "mktCap",
    "lastDiv",
    "changes",
    "companyName",
    "exchangeShortName",
    "industry",
    "website",
    "description",
    "ceo",
    "sector",
    "country",
    "fullTimeEmployees",
    "phone",
    "address",
    "city",
    "state",
    "dcf",
    "ipoDate",
]

# Income table columns.
INCOME_COLUMNS = [
    "date",
    "symbol",
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

# Balance sheet columns.
BALANCE_COLUMNS = [
    "date",
    "symbol",
    "period",
    "cashAndCashEquivalents",
    "shortTermInvestments",
    "cashAndShortTermInvestments",
    "netReceivables",
    "inventory",
    "totalCurrentAssets",
    "propertyPlantEquipmentNet",
    "goodwill",
    "intangibleAssets",
    "longTermInvestments",
    "taxAssets",
    "totalNonCurrentAssets",
    "otherAssets",
    "totalAssets",
    "accountPayables",
    "shortTermDebt",
    "taxPayables",
    "deferredRevenue",
    "totalCurrentLiabilities",
    "longTermDebt",
    "deferredRevenueNonCurrent",
    "totalLiabilities",
    "commonStock",
    "retainedEarnings",
    "totalStockholdersEquity",
    "totalLiabilitiesAndStockholdersEquity",
    "totalInvestments",
    "totalDebt",
    "netDebt",
]

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

        # Check that we haven't already queried this symbol.
        conn.commit()
        query = "SELECT * from profile_table where symbol='{}'".format(symbol.replace('.', '-'))
        cursor.execute(query)
        result = cursor.fetchall()
        if result:
            logger.info("Symbol already exists in database.")
            continue

        query_profile(conn, cursor, symbol)
        query_income(conn, cursor, symbol)
        query_balance(conn, cursor, symbol)


def query_profile(conn, cursor, symbol):
    """Query and upload data for the requested symbol."""
    # Parameterize and send the request.
    URL = "https://financialmodelingprep.com/api/v3/profile/{}".format(symbol)
    query_params = { "apikey": FMP_KEY }
    response = requests.get(url=URL, params=query_params)
    records = response.json()

    if "Error Message" in records:
        logger.error(records["Error Message"])
        return
        raise ValueError(records["Error Message"])

    for record in records:
        # Execute and commit insert
        data = [record[name] for name in PROFILE_COLUMNS]
        # import IPython;IPython.embed();quit()
        insert_query = (
            "INSERT INTO profile_table ({columns}) VALUES ("
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s);").format(columns=", ".join(PROFILE_COLUMNS))
        try:
            cursor.execute(insert_query, data)
        except Exception as e:
            logger.error(e)
        conn.commit()


def query_income(conn, cursor, symbol):
    """Query and upload data for the requested symbol."""
    # Parameterize and send the request.
    URL = "https://financialmodelingprep.com/api/v3/income-statement/{}".format(symbol)
    query_params = {
        "limit": 120,
        "apikey": FMP_KEY,
    }
    response = requests.get(url=URL, params=query_params)
    records = response.json()

    if "Error Message" in records:
        logger.error(records["Error Message"])
        return
        raise ValueError(records["Error Message"])

    for record in records:
        # Execute and commit insert
        data = [record[name] for name in INCOME_COLUMNS]
        insert_query = (
            "INSERT INTO income_table ({columns}) VALUES ("
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s);").format(columns=", ".join(INCOME_COLUMNS))
        try:
            cursor.execute(insert_query, data)
        except Exception as e:
            logger.error(e)
        conn.commit()


def query_balance(conn, cursor, symbol):
    """Query and upload data for the requested symbol."""
    # Parameterize and send the request.
    URL = "https://financialmodelingprep.com/api/v3/balance-sheet-statement/{}".format(symbol)
    query_params = {
        "limit": 120,
        "apikey": FMP_KEY,
    }
    response = requests.get(url=URL, params=query_params)
    records = response.json()

    if "Error Message" in records:
        logger.error(records["Error Message"])
        return
        raise ValueError(records["Error Message"])

    for record in records:
        # Execute and commit insert
        data = [record[name] for name in BALANCE_COLUMNS]
        insert_query = (
            "INSERT INTO balance ({columns}) VALUES ("
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s);").format(columns=", ".join(BALANCE_COLUMNS))
        try:
            cursor.execute(insert_query, data)
        except Exception as e:
            logger.error(e)
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