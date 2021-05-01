import json
import os
import sys

from flask import Flask, request, jsonify
import psycopg2

from gpt_api import set_openai_key, GPT, Example

application = Flask(__name__)
application.config["DEBUG"] = True


def get_db_connection():
    # Load credentials from environment. 
    POSTGRES_ADDRESS = os.environ.get('POSTGRES_ADDRESS')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
    POSTGRES_USERNAME = os.environ.get('POSTGRES_USERNAME')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME')

    # Create connection and cursor.
    print("POSTGRES_PASSWORD", POSTGRES_PASSWORD)
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
    
    gpt.add_instruction("Given an input question, respond with syntactically correct SQL."
                        " Only use the table called 'income'. The 'income' table has columns:"
                        " symbol (varchar(5)), fillingDate (timestamp), revenue (bigint), grossProfit (bigint),"
                        " costAndExpenses (bigint), and ebitda (bigint)")
    
    gpt.add_example(Example("What are the columns from income table?", 
                            "SELECT symbol, fillingDate, revenue, grossProfit, costAndExpenses, ebitda FROM income"))
    
    gpt.add_example(Example("How many companies have a filing date in the past 90 days?", 
                            "SELECT COUNT(*) FROM income WHERE fillingDate >= now() - interval '90 days'"))
    
    gpt.add_example(Example("When did company with symbol AAPL file its financial statement?", 
                            "SELECT fillingDate FROM income WHERE symbol = 'AAPL'"))
    
    gpt.add_example(Example("How much money did Tesla make in 2019?", 
                            "SELECT SUM(revenue) FROM income WHERE symbol = 'TSLA' AND"
                            " EXTRACT(YEAR FROM fillingDate) = 2019")) 

    gpt.add_example(Example("How much revenue did Facebook have in the last 2 years?", 
                            "SELECT SUM(revenue) FROM income WHERE symbol = 'FB'"
                            " AND fillingDate >= now() - interval '2 years'"))
    
    gpt.add_example(Example("What was the maximum revenue GOOGL had in the last 5 years?", 
                            "SELECT MAX(revenue) from income WHERE symbol = 'GOOGL'"
                            " AND fillingDate >= now() - interval '5 years'"))
    
    gpt.add_example(Example("What were the top 5 companies with the highest EBITDA?", 
                            "SELECT ebitda, symbol from income ORDER BY ebitda desc LIMIT 5"))
    
    gpt.add_example(Example("What is the EBITDA of MSFT?", 
                            "SELECT ebitda from income WHERE symbol = 'MSFT'"
                            " AND fillingDate >= now() - interval '1 year'"))
    
    gpt.add_example(Example("Plot the revenue over time of AAPL over the last 8 years", 
                            "SELECT fillingDate, revenue FROM income WHERE symbol = 'AAPL'"
                            " AND fillingDate >= now() - interval '8 years'"))

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


@application.route('/api', methods=['GET'])
def api():
    # Get the user input parameter.
    user_input = request.args.get("query", default="")
    
    # Get the GPT3-generated SQL query. 
    output = gpt.submit_request(user_input)
    openai_result = output['choices'][0].text
    sql_query = openai_result.split('output:')[1]
    sql_query = clean_query(sql_query)

    # Default invalid response. This is the schema of the response.
    response = {
        "metadata": {
            "user_input": user_input,
            "sql_query": sql_query,
        },
        "status": {
            "valid": False,
            "error_message": "Sorry, Edgar couldn't understand your question! He's still learning :)",
            "debug_message": "",
        },
        "data": {
            "type": "error",
            "value": -1,
            "plot": {},  # When valid, this is a dict of plot values: {"x": x, "y": y}
        },
    }

    # Short-circuit if the SQL query looks fishy.
    if "SELECT" not in sql_query or "income" not in sql_query:
        response["status"]["debug_message"] = "Invalid SQL query."
        return jsonify(response)

    # Run the SQL query and grab the result.
    conn.commit()
    try:
        cur.execute(sql_query)
    except Exception as err:
        response["status"]["debug_message"] = str(err)
        return jsonify(response)
    result = cur.fetchall()

    # Process the different kinds of results. From here on out stuff is valid.
    response["status"]["valid"] = True
    response["status"]["error_message"] = ""

    # Split the results into (x, y) data for plotting.
    if len(result) >= 1 and len(result[0]) == 2:
        x, y = zip(*result)
        response["data"]["type"] = "plot"
        response["data"]["plot"] = { "x": x, "y": y }
        return jsonify(response)
        
    # Unnest single values.
    if len(result) == 1 and len(result[0]) == 1:
        result = result[0][0]

    # Return the raw values.
    response["data"]["type"] = "value"
    response["data"]["value"] = result
    return jsonify(response)
    

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production application.
    application.debug = True
    application.run()