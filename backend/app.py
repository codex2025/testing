from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from db_operations import init_db, insert_initial_request, update_request_with_ai_results

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit_request', methods=['POST'])
def submit_request():
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400

    data = request.get_json()
    subject = data.get('subject')
    description = data.get('description')

    print('Received support request (raw):', data)

    # Insert validated request into DB
    try:
        ok, result = insert_initial_request(subject, description)
    except Exception as e:
        print('Unexpected error during insert_initial_request:', e)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    if not ok:
        # Distinguish validation (client) errors vs DB/server errors
        msg = result or 'Invalid input'
        if isinstance(msg, str) and msg.lower().startswith('database error'):
            return jsonify({'status': 'error', 'message': msg}), 500
        return jsonify({'status': 'error', 'message': msg}), 400

    request_id = result

    # Simulate AI processing (placeholder)
    try:
        summary = (description or '')[:120] + '...'
        suggested = f"Thanks for your request about '{subject}'. We'll follow up shortly."

        upd_ok, upd_result = update_request_with_ai_results(
            request_id, summary=summary, suggested_response=suggested, agent_resolved=False, status='Analyzed'
        )
        if not upd_ok:
            print('AI update failed:', upd_result)
            # Treat update failures as server errors
            return jsonify({'status': 'error', 'message': upd_result, 'request_id': request_id}), 500
    except Exception as e:
        print('AI simulation/update error:', e)
        return jsonify({'status': 'error', 'message': 'Internal server error', 'request_id': request_id}), 500

    return jsonify({'status': 'success', 'message': 'Request received', 'request_id': request_id}), 200


if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print('Database initialization failed:', e)
    app.run(port=5000, debug=True)
