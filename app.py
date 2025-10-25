import os
from flask import Flask, render_template, request, jsonify
import psycopg2
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# --- PostgreSQL setup ---
DATABASE_URL = os.environ.get("DATABASE_URL")  # Set this in Render Environment Variables
def get_conn():
    return psycopg2.connect(DATABASE_URL)

# --- Cloudinary setup ---
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

# --- Initialize DB ---
def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                image TEXT NOT NULL,
                initial_price REAL NOT NULL,
                current_price REAL NOT NULL
            )
            """)
        conn.commit()

init_db()

# --- Routes ---
@app.route('/')
def home():
    return render_template('tracker.html')

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form['product-name']
    initial_price = float(request.form['initial-price'])
    current_price = float(request.form['current-price'])
    image = request.files['product-image']

    if image:
        # Upload image to Cloudinary
        result = cloudinary.uploader.upload(image)
        image_url = result['secure_url']

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO products (name, image, initial_price, current_price)
                    VALUES (%s, %s, %s, %s)
                """, (name, image_url, initial_price, current_price))
            conn.commit()

        return jsonify({
            'name': name,
            'image': image_url,
            'initial_price': initial_price,
            'current_price': current_price
        })
    return 'No image uploaded', 400

@app.route('/products')
def products():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, image, initial_price, current_price FROM products ORDER BY id DESC")
            rows = cur.fetchall()
    products = [{
        'id': r[0],
        'name': r[1],
        'image': r[2],
        'initial_price': r[3],
        'current_price': r[4]
    } for r in rows]
    return jsonify(products)

@app.route('/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    new_price = float(request.form['current-price'])
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE products SET current_price = %s WHERE id = %s", (new_price, product_id))
        conn.commit()
    return jsonify({'id': product_id, 'current_price': new_price})

@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
    return jsonify({'status': 'deleted', 'id': product_id})

# --- Run Flask ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
