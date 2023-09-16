from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid
import qrcode
import sqlite3

app = Flask(__name__)

# Initialize the SQLite database
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        prescription TEXT
    )
''')
conn.commit()
conn.close()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Generate a unique ID for the user
        user_id = str(uuid.uuid4())
        
        # Get user data from the form
        user_name = request.form.get('user_name')
        user_email = request.form.get('user_email')
        user_prescription = request.form.get('user_prescription')
        
        # Store user data in the SQLite database
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (id, name, email, prescription)
            VALUES (?, ?, ?, ?)
        ''', (user_id, user_name, user_email, user_prescription))
        conn.commit()
        conn.close()
        
        # Generate a QR code with a URL to retrieve user data
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = url_for('show_user_data', user_id=user_id, _external=True)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"static/qr_codes/{user_id}.png")
        
        return redirect(url_for('show_qrcode', user_id=user_id))
    
    return render_template('index.html')

@app.route('/qrcode/<string:user_id>', methods=['GET'])
def show_qrcode(user_id):
    # Check if the user_id exists in user_data
    if user_id:
        # Generate the URL of the QR code image
        qrcode_url = url_for('static', filename=f'qr_codes/{user_id}.png', _external=True)
        return render_template('qrcode.html', qrcode_url=qrcode_url)
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/user/<string:user_id>', methods=['GET'])
def show_user_data(user_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_info = cursor.fetchone()
    
    conn.close()
    
    if user_info:
        user_data_dict = {
            'id': user_info[0],
            'name': user_info[1],
            'email': user_info[2],
            'prescription': user_info[3]
        }
        return jsonify(user_data_dict)
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='192.168.0.119', port=5000, debug=True)