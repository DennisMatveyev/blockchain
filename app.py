from uuid import uuid4
from flask import Flask

from blockchain import Blockchain
from routes import init_routes


app = Flask(__name__)

blockchain = Blockchain()
node_identifier = str(uuid4()).replace('-', '')

init_routes(app, blockchain, node_identifier)


app.run(host='0.0.0.0', port=5000)
