import os
from dotenv import load_dotenv
from flask import Blueprint
import pymongo
from bson import json_util
import json
from flask import jsonify

load_dotenv()

blueprint_ticker = Blueprint("ticker", __name__)

db_client = pymongo.MongoClient(os.getenv('MONGODB'))
db = db_client[os.getenv('DB_NAME')]
collection_ratios = db[os.getenv('COLLECTION_RATIOS')]
collection_results = db[os.getenv('COLLECTION_RESULTS')]
collection_concall_analysis = db[os.getenv('COLLECTION_CONCALL_ANALYSIS')]
collection_financials_analysis = db[os.getenv('COLLECTION_FINANCIALS_ANALYSIS')]


@blueprint_ticker.route("/api/ticker", methods=['GET'])
def get_all_tickers():
    col_tickers = db['col_tickers']
    results = list(col_tickers.find())
    json_string = json.dumps(results, default=json_util.default)
    return jsonify(json.loads(json_string))


@blueprint_ticker.route("/api/ticker/<ticker_id>", methods=['GET'])
def get_one_ticker(ticker_id):
    return "Hello from one ticker: " + ticker_id


@blueprint_ticker.route('/api/ticker/ratios/<ticker>', methods=['GET'])
def get_ticker_ratios(ticker):
    documents = collection_ratios.find_one({'ticker': ticker})
    json_string = json.dumps(documents, default=json_util.default)
    return jsonify(json.loads(json_string))


@blueprint_ticker.route('/api/ticker/results/<ticker>', methods=['GET'])
def get_ticker_results(ticker):
    documents = collection_results.find_one({'ticker': ticker})
    json_string = json.dumps(documents, default=json_util.default)
    return jsonify(json.loads(json_string))


@blueprint_ticker.route('/api/ticker/analysis/<ticker>', methods=['GET'])
def get_gpt_analysis(ticker):
    documents = collection_concall_analysis.find_one({'ticker': ticker})
    json_string = json.dumps(documents, default=json_util.default)
    return jsonify(json.loads(json_string))


@blueprint_ticker.route('/api/ticker/score/<ticker>', methods=['GET'])
def get_gpt_score(ticker):
    documents = collection_financials_analysis.find_one({'ticker': ticker})
    json_string = json.dumps(documents, default=json_util.default)
    return jsonify(json.loads(json_string))

