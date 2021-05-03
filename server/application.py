import datetime
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

    gpt.add_instruction("Given an input question, respond with syntactically correct PostgreSQL. "
                        "Only use the tables 'income_table', 'profile_table', and 'balance'. "
                        "The 'income_table' table has columns: symbol, date, revenue, "
                        "grossProfit, costAndExpenses, researchAndDevelopmentExpenses. "
                        "The 'profile_table' table has columns: "
                        "symbol, mktCap, price, description, ceo, address, ipoDate. "
                        "The 'balance' table has columns: symbol, date, cashAndCashEquivalents, "
                        "totalCurrentAssets, goodwill, totalInvestments, totalDebt.")

    gpt.add_example(Example("Who is Facebook's CEO?", 
                            "SELECT ceo FROM profile_table WHERE symbol = 'FB'"))

    gpt.add_example(Example("What are the 5 companies that have the most cash?", 
                            "SELECT symbol, cashAndCashEquivalents from balance WHERE EXTRACT(YEAR FROM date) = 2020 ORDER BY cashAndCashEquivalents desc LIMIT 5;"))

    gpt.add_example(Example("How much money did Amazon make in 2017?", 
                            "SELECT grossProfit FROM income_table WHERE symbol = 'AMZN' AND"
                            " EXTRACT(YEAR FROM date) = 2017;")) 

    gpt.add_example(Example("What were the top 7 companies with the highest revenue?", 
                            "SELECT symbol, revenue from income_table "
                            "WHERE EXTRACT(YEAR FROM date) = 2020 ORDER BY revenue desc LIMIT 7;"))

    gpt.add_example(Example("Show me how Netflix's profit has changed over the last 6 years.", 
                            "SELECT date, grossProfit FROM income_table WHERE symbol = 'NFLX'"
                            " AND date >= now() - interval '6 years';"))

    gpt.add_example(Example("How has Facebook's cost to revenue ratio changed over the last 17 years?", 
                            "SELECT date, CAST(costAndExpenses AS float) / NULLIF(revenue, 0) "
                            "FROM income_table WHERE symbol = 'FB' AND date >= now() - interval '17 years';"))
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
            "debug_message": "",
        },
        "data": {
            "type": "error",
            "value": -1,
        },
    }

    # Short-circuit if the user query looks fishy.
    if len(user_input) < 10:
        response["status"]["debug_message"] = "Invalid user input."
        return package_response(response)

    def input_to_query(user_input):
        # Get the GPT3-generated SQL query. 
        output = gpt.submit_request(user_input)
        openai_result = output['choices'][0].text
        sql_query = openai_result.split('output:')[1]
        sql_query = clean_query(sql_query)

        # Some straight-up hacks for things that GPT-3 is bad at:
        # Switch descending to ascending order for top-least type of questions. 
        if "least" in user_input and "desc" in sql_query:
            sql_query = sql_query.replace("desc", "asc")
        # Looking for data sooner than now() never makes sense.
        if "WHERE date >= now() AND" in sql_query:
            sql_query = sql_query.replace("WHERE date >= now() AND", "WHERE")
        # Divide-by-zero handling is hard to learn.
        if "researchAndDevelopmentExpenses" in sql_query and "CAST(researchAndDevelopmentExpenses" not in sql_query:
            sql_query = sql_query.replace("researchAndDevelopmentExpenses", "CAST(researchAndDevelopmentExpenses AS float)")
        if "/ revenue" in sql_query:
            sql_query = sql_query.replace("revenue", "NULLIF(revenue, 0)")
        response["metadata"]["sql_query"] = sql_query
        return sql_query

    # Run the SQL query and grab the result.
    sql_query = input_to_query(user_input)
    conn.commit()
    try:
        cur.execute(sql_query)
    except Exception as err:
        # If it fails, try one more time:
        try:
            sql_query = input_to_query(user_input)
            conn.commit()
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
    response["status"]["error_message"] = ""
    response["data"]["value"] = result

    # These results are a list of values we should put into a table.
    try:
        if len(result) == 1 and len(cur.description) > 1:
            column_names = [desc[0] for desc in cur.description]
            value = {}
            for id, v in enumerate(result[0]):
                value[column_names[id]] = v
            response["data"]["type"] = "table"
            response["data"]["value"] = [value]
            return package_response(response)
    except TypeError:
        pass

    # Split the results into (x, y) data for plotting.
    try:
        if len(result) >= 1 and len(result[0]) == 2:
            # Sort if x values are datetimes.
            if isinstance(result[0][0], datetime.datetime):
                result = sorted(result)
                response["data"]["type"] = "plot"
            else:
                response["data"]["type"] = "bar"
            x, y = zip(*result)
            response["data"]["value"] = { "x": x, "y": y }
            return package_response(response)
    except TypeError:
        pass

    # Return all numberic responses explicitly as a number.
    try:
        float(result)
        response["data"]["type"] = "number"
        response["data"]["value"] = result
        return package_response(response)
    except ValueError:
        pass
    except TypeError:
        pass

    # Return the raw values.
    response["data"]["type"] = "string"
    response["data"]["value"] = str(result)
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
    # Setting debug to True enables debug output.
    # TODO: Remove before deploying to production.
    application.debug = True
    application.run()
