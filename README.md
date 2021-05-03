# Ask Edgar

Edgar is your AI investment assistant.
Ask Edgar English-language questions about public company financial data.

For example:
- What were the top 5 companies with the highest EBITDA?
- Show me the R&D expenses of Apple over the last 8 years.
- How much revenue did Tesla have in 2018?

Demo: https://www.loom.com/share/8e8735e38fb64e3ab6e53ddd9129cf1b
![demo](https://github.com/asta-li/edgar/blob/main/demo.gif?raw=true)

## Setup

### Requirements / Initial setup
- Install miniconda: https://docs.conda.io/en/latest/miniconda.html
- Set up the conda and pip environments.
```
conda env create -f tools/environment.yml
```

### Enter the conda environment
```
conda activate edgar
```
To exit, run `conda deactivate`.

### Set up environment
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

### Set up database
Run the following only if you are creating a new database instance!
Otherwise, stop and move on to the next section.

Run the jupyter notebook to set up and inspect the database.
```
cd tools
jupyter notebook setup_db.ipynb
```
Then run `populate_db.py` to fill the postgres database with data.
```
python populate_db.py
```

### Set up the AWS Elastic Beanstalk project
If the project does not yet exist, follow these instructions:
https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html

The following will require you to have Beanstalk CLI installed:
https://github.com/aws/aws-elastic-beanstalk-cli-setup

```
cd server
eb init -p python-3.6 flask-edgar --region us-west-1
eb create flask-env
# Set up the environment with the same variables listed above.
eb setenv POSTGRES_ADDRESS=...
```

## Run the code

### Run the Python Flask server
Build the static React frontend. Also install npm dependencies.
```
cd client
npm install
npm run build
cd ..
```
Then enter the `server` directory and run the server locally:
```
cd server
python application.py
```

### Run in React development mode
Run the client code in development mode.

From project root:
```
cd client
npm start
```
### Test the API

Query the api endpoint for the given user query.
```
# Local
curl -X GET http://127.0.0.1:5000/api?query=${USER_QUERY}
# Deployed
curl -X GET http://flask-env.eba-dwnhvhak.us-west-1.elasticbeanstalk.com/api?query=${USER_QUERY}
```

## Deploy

To deploy to production (S3 and AWS Elastic Beanstalk), run:
```
cd client
npm run build
aws s3 sync build/ s3://ask-edgar --acl public-read

cd ../server
eb deploy flask-env
```
Make sure to make the files public:
https://s3.console.aws.amazon.com/s3/buckets/ask-edgar?region=us-west-1&tab=objects

TODO: Update the web app setup:
https://adamraudonis.medium.com/how-to-deploy-a-website-on-aws-with-docker-flask-react-from-scratch-d0845ebd9da4