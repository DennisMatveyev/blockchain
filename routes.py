from flask import jsonify, request


def init_routes(app, blockchain, node_identifier):
    @app.route('/mine', methods=['GET'])
    def mine():
        # We run the proof of work algorithm to get the next proof...
        last_block = blockchain.last_block
        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof)

        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        blockchain.new_transaction(
            sender="0",
            recipient=node_identifier,
            amount=1,
        )

        # Forge the new Block by adding it to the chain
        block = blockchain.new_block(proof)

        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }

        return jsonify(response), 200

    @app.route('/transactions/new', methods=['POST'])
    def new_transaction():
        """
        POST JSON:
        {
         "sender": "my address",
         "recipient": "someone else's address",
         "amount": 5
        }
        """
        data = request.get_json()

        # Check that the required fields are in the POST'ed data
        required = ['sender', 'recipient', 'amount']

        if not all(k in data for k in required):
            return jsonify({'error': 'Missing values in POST data'}), 400

        # Create a new Transaction
        index = blockchain.new_transaction(data['sender'], data['recipient'], data['amount'])
        response = {'message': f'Transaction will be added to Block {index}'}

        return jsonify(response), 201

    @app.route('/chain', methods=['GET'])
    def full_chain():
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain),
        }

        return jsonify(response), 200

    @app.route('/nodes/register', methods=['POST'])
    def register_nodes():
        data = request.get_json()

        nodes = data.get('nodes')

        if nodes is None:
            return "Error: Please supply a valid list of nodes", 400

        for node in nodes:
            blockchain.register_node(node)

        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(blockchain.nodes),
        }

        return jsonify(response), 201

    @app.route('/nodes/resolve_conflict', methods=['GET'])
    def consensus():
        replaced = blockchain.resolve_conflicts()

        if replaced:
            response = {
                'message': 'Our chain was replaced',
                'new_chain': blockchain.chain
            }
        else:
            response = {
                'message': 'Our chain is authoritative',
                'chain': blockchain.chain
            }

        return jsonify(response), 200
