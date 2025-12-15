import os
from flask import Flask, jsonify


app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello_world():


    return jsonify(message="Bonjour, monde du serverless!")

if __name__ == "__main__":

    port = int(os.environ.get('PORT', 8080))
    

    app.run(host='0.0.0.0', port=port, debug=True)
