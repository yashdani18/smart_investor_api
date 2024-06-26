
# Smart Investor (Rest API using Flask)

The motivation for this project was to develop stock 
analysis engine that would aggregate data from multiple web 
sources and present it in an easy-to-understand way.


## Features

- Track Equities
- Visualize Growth Numbers
- Compare Industry Peers

With intelligent commentary powered by gpt-4

## Installation and Setup

Clone repository from GitHub:

```
  git clone https://github.com/yashdani18/smart_investor_api.git
```

Install dependencies:

```
  cd smart_investor_api
  pip install --no-cache-dir -r requirements.txt
```


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`MONGODB`

`DB_NAME`

`COLLECTION_RATIOS`

`COLLECTION_RESULTS`

`COLLECTION_CONCALL_ANALYSIS`

`COLLECTION_FINANCIALS_ANALYSIS`


## Run Locally

Start the development server: 

```bash
  python app.py
```

Make sure to pass `debug=True` as an argument when invoking app.run() in app.py


## API Reference

#### Get all tickers

```http
  GET /api/ticker
```

#### Get one ticker

```http
  GET /api/ticker/<ticker_id>
```

#### Get fundamental ratios for ticker

```http
  GET /api/ticker/ratios/<ticker_id>
```

#### Get financial results for ticker

```http
  GET /api/ticker/results/<ticker_id>
```

#### Get conference call analysis for ticker

```http
  GET /api/ticker/analysis/<ticker_id>
```


#### Get financial score for ticker

```http
  GET /api/ticker/score/<ticker_id>
```


## 🔗 Links
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/yashdani27/)



## Acknowledgements

 - [Screener - Stock Analysis and Screening Tool](https://www.screener.in/)
 - [OpenAI API (model: GPT-4 Turbo)](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4)

