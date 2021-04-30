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
pip install -r requirements.txt
```

## Run the code
Load the following variables into your environment:
```
POSTGRES_ADDRESS
POSTGRES_PORT
POSTGRES_USERNAME
POSTGRES_PASSWORD
POSTGRES_DBNAME
FMP_KEY
```

Then run `populate_db.py` to fill the postgres database with data.
```
python populate_db.py
```

## Exit the conda environment
```
conda deactivate
```