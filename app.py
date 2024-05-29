from flask import Flask, jsonify
from flask_cors import CORS
from blueprints.ticker.ticker import blueprint_ticker
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.register_blueprint(blueprint_ticker)


@app.route('/', methods=['GET'])
def greeting():
    print('root endpoint')
    return jsonify(message="Hello from Flask!")


if __name__ == '__main__':
    # port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=4000)
