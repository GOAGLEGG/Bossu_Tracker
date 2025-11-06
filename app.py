import os
import psycopg2

import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

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
    name = request.form.get('product-name')
    initial_price = request.form.get('initial-price') or None
    current_price = request.form.get('current-price') or None
    ad_value = request.form.get('ad-value') or None
    active_until = request.form.get('active-until') or None
    image = request.files.get('product-image')

    image_url = None
    if image:
        upload_result = cloudinary.uploader.upload(image)
        image_url = upload_result['secure_url']

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO products (name, image, initial_price, current_price, ad_value, active_until)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, image_url, initial_price, current_price, ad_value, active_until))
        conn.commit()

    return jsonify({
        'name': name, 'image': image_url,
        'initial_price': initial_price, 'current_price': current_price,
        'ad_value': ad_value, 'active_until': active_until
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
    fields = []
    values = []

    current_price = request.form.get('current-price')
    ad_value = request.form.get('ad-value')
    active_until = request.form.get('active-until')

    if current_price:
        fields.append("current_price = %s")
        values.append(current_price)
    if ad_value:
        fields.append("ad_value = ad_value + %s")
        values.append(ad_value)
    if active_until:
        fields.append("active_until = %s")
        values.append(active_until)

    if not fields:
        return jsonify({'status': 'no fields to update'}), 400

    query = f"UPDATE products SET {', '.join(fields)} WHERE id = %s"
    values.append(product_id)

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, tuple(values))
        conn.commit()

    return jsonify({'status': 'updated', 'id': product_id})

@app.route('/update_image/<int:product_id>', methods=['POST'])
def update_image(product_id):
    image = request.files.get('product-image')
    if not image:
        return jsonify({'error': 'No image uploaded'}), 400

    upload_result = cloudinary.uploader.upload(image)
    image_url = upload_result['secure_url']

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE products SET image = %s WHERE id = %s", (image_url, product_id))
        conn.commit()

    return jsonify({'status': 'image updated', 'id': product_id, 'image_url': image_url})

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
