const form = document.getElementById('tracker-form');
const productList = document.getElementById('products');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData(form);

  // Set defaults for empty fields
  if (!formData.get('product-name')) formData.set('product-name', '');
  if (!formData.get('initial-price')) formData.set('initial-price', 0);
  if (!formData.get('current-price')) formData.set('current-price', 0);
  if (!formData.get('ad-value')) formData.set('ad-value', 0);
  if (!formData.get('active-until')) formData.set('active-until', '');
  if (!formData.get('product-image')) formData.delete('product-image'); // optional, send nothing if no image

  const response = await fetch('/upload', {
    method: 'POST',
    body: formData
  });

  await response.json();
  loadProducts();
  form.reset();
});

async function loadProducts() {
  productList.innerHTML = '';
  const res = await fetch('/products');
  const products = await res.json();
  products.forEach(displayProduct);
}

function displayProduct(product) {
  const div = document.createElement('div');
  div.classList.add('product-item');

  const profit = (product.current_price - product.initial_price - (product.ad_value || 0)).toFixed(2);

  div.innerHTML = `
    ${product.image ? `<img src="/uploads/${product.image}" alt="${product.name}">` : ''}
    <h3>${product.name || 'Unnamed Product'}</h3>
    <p>Initial: $${product.initial_price || 0}</p>
    <p>Current: $${product.current_price || 0}</p>
    <p>Ad Value: $${product.ad_value || 0}</p>
    <p>Active Until: ${product.active_until || 'N/A'}</p>
    <p><strong>Profit:</strong> 
      <span style="color:${profit >= 0 ? 'green' : 'red'};">$${profit}</span>
    </p>
    <input type="number" id="edit-${product.id}" placeholder="New current price" step="0.01" />
    <input type="number" id="ad-${product.id}" placeholder="New ad value" step="0.01" />
    <input type="date" id="date-${product.id}" />
    <button onclick="updateProduct(${product.id})">Update</button>
    <button onclick="deleteProduct(${product.id})" style="background-color:red;">Delete</button>
  `;

  productList.appendChild(div);
}

async function updateProduct(id) {
  const newPrice = document.getElementById(`edit-${id}`).value;
  const newAd = document.getElementById(`ad-${id}`).value;
  const newDate = document.getElementById(`date-${id}`).value;

  const formData = new FormData();
  formData.append('current-price', newPrice || 0);
  formData.append('ad-value', newAd || 0);
  formData.append('active-until', newDate || '');

  await fetch(`/update/${id}`, { method: 'POST', body: formData });
  loadProducts();
}

async function deleteProduct(id) {
  await fetch(`/delete/${id}`, { method: 'POST' });
  loadProducts();
}

loadProducts();
