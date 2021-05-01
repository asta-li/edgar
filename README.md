# Ask Edgar

Ask Edgar English-language questions about public company financial data.

For example:
- What were the top 5 companies with the highest EBITDA?
- Plot the revenue over time of AAPL over the last 8 years.
- How much revenue did Facebook have in the last 2 years?

![screenshot](https://github.com/asta-li/edgar/blob/main/screenshot1.png?raw=true)

## Setup

### Enter the conda environment
```
conda activate edgar
```
To exit, run `conda deactivate`.

### Requirements
- Install miniconda: https://docs.conda.io/en/latest/miniconda.html
- Set up the conda and pip environments.
```
conda env create -f environment.yml
```

### Setup database
Load the following variables into your environment:
```
POSTGRES_ADDRESS
POSTGRES_PORT
POSTGRES_USERNAME
POSTGRES_PASSWORD
POSTGRES_DBNAME
FMP_KEY
OPENAI_KEY
```
Run the jupyter notebook to set up and inspect the database.
```
jupyter notebook setup_db.ipynb
```
Then run `populate_db.py` to fill the postgres database with data.
```
python populate_db.py
```

### Set up the AWS Elastic Beanstalk project
If the project does not yet exist, follow these instructions:
https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html
```
cd server
eb init -p python-3.6 flask-edgar --region us-west-1
eb create flask-env
eb setenv POSTGRES_ADDRESS=...
```

## Run the code

### Run the Python Flask server
Build the static React frontend.
```
cd client
npm run build
cd ..
```
Then enter the `server` directory.
```
cd server
```
Run the server locally:
```
python application.py
```

### Run in React development mode
Run the client code in development mode.

From project root:
```
cd client
npm start
```

## Deploy

To deploy to production (AWS Elastic Beanstalk), run:
```
cd client
npm run build
cd ../server
eb deploy flask-env
```

## Test the API locally

### Test `/api`

Query the fax status endpoint for the given Fax ID.
```
curl -X GET hhttp://127.0.0.1:5000/api?query=${USER_QUERY}
```