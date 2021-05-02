import json
import os
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

from gpt_api import set_openai_key, GPT, Example

application = Flask(__name__)
CORS(application)
application.config["DEBUG"] = True


def get_db_connection():
    # Load credentials from environment. 
    POSTGRES_ADDRESS = os.environ.get('POSTGRES_ADDRESS')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
    POSTGRES_USERNAME = os.environ.get('POSTGRES_USERNAME')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME')

    # Create connection and cursor.
    conn = psycopg2.connect(host=POSTGRES_ADDRESS,
                    database=POSTGRES_DBNAME,
                    user=POSTGRES_USERNAME,
                    password=POSTGRES_PASSWORD,
                    port=POSTGRES_PORT)
    cur = conn.cursor()

    return conn, cur


def setup_openai():
    # Load credentials from environment. 
    OPENAI_KEY = os.environ.get('OPENAI_KEY')
    set_openai_key(OPENAI_KEY)

    # Construct GPT-3-instruct instance, add instruction and examples
    gpt = GPT(engine="davinci-instruct-beta",
            temperature=0.3,
            max_tokens=200)
    
    gpt.add_instruction("Given an input question, respond with syntactically correct SQL. "
                        "Only use the table called 'income_table', 'profile_table', and 'balance'. "
                        "The 'income_table' table has columns: "
                        "symbol, date, revenue, grossProfit, costAndExpenses, ebitda. "
                        "The 'profile_table' table has columns: "
                        "symbol, mktCap, price, description, ceo, address, ipoDate. "
                        "The 'balance' table has columns: symbol, date, cashAndCashEquivalents, "
                        "totalCurrentAssets, goodwill, totalInvestments, totalDebt.")

    gpt.add_example(Example("What is the market cap of Google?", 
                            "SELECT mktCap FROM profile_table WHERE symbol = 'GOOGL'"))

    gpt.add_example(Example("Who is Facebook's CEO?", 
                            "SELECT ceo FROM profile_table WHERE symbol = 'FB'"))

    gpt.add_example(Example("What are the 5 companies that have the most assets?", 
                            "SELECT symbol, totalCurrentAssets from balance WHERE EXTRACT(YEAR FROM date) = 2020 ORDER BY totalCurrentAssets desc LIMIT 5;"))
    
    gpt.add_example(Example("What are the 3 companies that have the least debt?", 
                            "SELECT symbol, totalDebt from balance WHERE EXTRACT(YEAR FROM date) = 2020 ORDER BY totalDebt asc LIMIT 3;"))
    
    gpt.add_example(Example("How have Nvidia's investments changed over the past 10 years?", 
                            "SELECT date, totalInvestments FROM balance WHERE symbol = 'NVDA'"
                            " AND date >= now() - interval '10 years'"))
    
    gpt.add_example(Example("How much money did Tesla make in 2019?", 
                            "SELECT SUM(grossProfit) FROM income_table WHERE symbol = 'TSLA' AND"
                            " EXTRACT(YEAR FROM date) = 2019")) 

    gpt.add_example(Example("What was the total revenue that Microsoft had over the last 3 years?", 
                            "SELECT SUM(revenue) FROM income_table WHERE symbol = 'MSFT'"
                            " AND date >= now() - interval '3 years'"))
    
    gpt.add_example(Example("What were the top 7 companies with the highest EBITDA?", 
                            "SELECT symbol, ebitda from income_table WHERE EXTRACT(YEAR FROM date) = 2020 ORDER BY ebitda desc LIMIT 7"))
    
    gpt.add_example(Example("What was the EBITDA of Amazon in 2016?", 
                            "SELECT ebitda from income_table WHERE symbol = 'AMZN' AND EXTRACT(YEAR FROM date) = 2016"))
    
    gpt.add_example(Example("Plot the expenses over time of Apple over the last 8 years", 
                            "SELECT date, costAndExpenses FROM income_table WHERE symbol = 'AAPL'"
                            " AND date >= now() - interval '8 years'"))

    return gpt

# Set up global vars. 
conn, cur = get_db_connection()
gpt = setup_openai()


@application.route('/', methods=['GET'])
def home():
    return '''<h1>Hello World!</h1>'''


def clean_query(query):
    query = query.strip().strip('"')
    return query


def package_response(response):
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response


@application.route('/api', methods=['GET'])
def api():
    # Get the user input parameter.
    user_input = request.args.get("query", default="")

    # Default invalid response. This is the schema of the response.
    response = {
        "metadata": {
            "user_input": user_input,
            "sql_query": "",
        },
        "status": {
            "valid": False,
            "error_message": "Sorry, Edgar couldn't understand your question! He's still learning...",
            "debug_message": "",
        },
        "data": {
            "type": "error",
            "value": -1,
            "plot": {},  # When valid, this is a dict of plot values: {"x": x, "y": y}
        },
    }

    # Short-circuit if the user query looks fishy.
    if len(user_input) < 15:
        response["status"]["debug_message"] = "Invalid user input."
        return package_response(response)

    # Get the GPT3-generated SQL query. 
    output = gpt.submit_request(user_input)
    openai_result = output['choices'][0].text
    sql_query = openai_result.split('output:')[1]
    sql_query = clean_query(sql_query)
    response["metadata"]["sql_query"] = sql_query

    # Short-circuit if the SQL query looks fishy.
    if "SELECT" not in sql_query or "income" not in sql_query:
        response["status"]["debug_message"] = "Invalid SQL query."
        return package_response(response)

    # Run the SQL query and grab the result.
    conn.commit()
    try:
        cur.execute(sql_query)
    except Exception as err:
        response["status"]["debug_message"] = str(err)
        return package_response(response)
    result = cur.fetchall()

    # Process the different kinds of results. From here on out, we know the result is valid.
    # Unnest single values.
    try:
        if len(result) == 1 and len(result[0]) == 1:
            result = result[0][0]
    except TypeError:
        pass
    response["status"]["valid"] = True
    response["data"]["value"] = result
    response["status"]["error_message"] = ""

    # Split the results into (x, y) data for plotting.
    try:
        if len(result) >= 1 and len(result[0]) == 2:
            x, y = zip(*result)
            response["data"]["type"] = "plot"
            response["data"]["plot"] = { "x": x, "y": y }
            return package_response(response)
    except TypeError:
        pass
    
    # Return the raw values.
    response["data"]["type"] = "value"
    response["data"]["value"] = result
    return package_response(response)
    
@application.route('/teach', methods=['POST'])
def teach():
    query = request.args.get("query", default=None)
    sql = request.args.get("sql", default=None)

    if not query:
        response["status"]["debug_message"] = "Required query param missing."
        return package_response(response)
    if not sql:
        response["status"]["debug_message"] = "Required sql param missing."
        return package_response(response)

    gpt.add_example(Example(query, sql))
    response = {
        "status": {
            "valid": True,
            "error_message": "",
            "debug_message": "",
            "query" : query,
            "sql" : sql,
        },
    }
    return package_response(response)
                    

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production application.
    application.debug = True
    application.run()
