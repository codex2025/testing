from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

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

    return jsonify({'status': 'received'})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
