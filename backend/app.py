from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from db_operations import init_db, insert_request

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit_request', methods=['POST'])
def submit_request():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    subject = data.get('subject', '').strip()
    description = data.get('description', '').strip()

    # Simple server-side logging for now
    print('Received support request:')
    print('Subject:', subject)
    print('Description:', description)

    try:
        inserted_id = insert_request(subject, description)
        print(f"Stored request id={inserted_id}")
    except Exception as e:
        print(f"Failed to store request: {e}")

    return jsonify({'status': 'received'})


if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print('Database initialization failed:', e)
    app.run(port=5000, debug=True)
