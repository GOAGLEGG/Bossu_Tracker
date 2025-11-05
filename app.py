import os
import psycopg2
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# --- routes ---
@app.route('/')
def home():
    return render_template('tracker.html')

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form.get('product-name', '')
    initial_price = float(request.form.get('initial-price') or 0)
    current_price = float(request.form.get('current-price') or 0)
    ad_value = float(request.form.get('ad-value') or 0)
    active_until = request.form.get('active-until', or '1001-01-01')

    image = request.files.get('product-image')
    image_filename = None
    if image:
        image_filename = image.filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO products (name, image, initial_price, current_price, ad_value, active_until)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, image_filename, initial_price, current_price, ad_value, active_until))
        conn.commit()

    return jsonify({
        'name': name, 
        'image': image_filename,
        'initial_price': initial_price,
        'current_price': current_price,
        'ad_value': ad_value,
        'active_until': active_until
    })

@app.route('/products')
def products():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, image, initial_price, current_price, ad_value, active_until FROM products")
        rows = cur.fetchall()
    products = [
        {
            'id': r[0], 'name': r[1], 'image': r[2],
            'initial_price': r[3], 'current_price': r[4],
            'ad_value': r[5], 'active_until': r[6]
        } for r in rows
    ]
    return jsonify(products)

@app.route('/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    current_price = request.form.get('current-price')
    ad_value = request.form.get('ad-value')
    active_until = request.form.get('active-until')

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE products
            SET current_price = COALESCE(%s, current_price),
                ad_value = COALESCE(%s, ad_value),
                active_until = COALESCE(%s, active_until)
            WHERE id = %s
        """, (current_price, ad_value, active_until, product_id))
        conn.commit()

    return jsonify({'status': 'updated', 'id': product_id})

@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
    return jsonify({'status': 'deleted', 'id': product_id})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
