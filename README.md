# Fills a Postgres DB with public company financial data

## Enter the conda environment
```
conda activate edgar
```

## Requirements
- Install miniconda: https://docs.conda.io/en/latest/miniconda.html
- Set up the conda and pip environments.
```
conda env create -f environment.yml
```

## Setup
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

## Run server
Enter the `eb-flask` directory to run the server.
```
cd eb-flask
```
To run the server locally:
```
python application.py
```
To deploy to production, run:
```
eb deploy flask-env
```

## Exit the conda environment
```
conda deactivate
```
