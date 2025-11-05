const form = document.getElementById('tracker-form');
const productList = document.getElementById('products');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(form);

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
  const profit = (product.current_price - product.initial_price).toFixed(2);
  div.innerHTML = `
    <img src="/uploads/${product.image}" alt="${product.name}" />
    <h3>${product.name}</h3>
    <p>Initial: $${product.initial_price}</p>
    <p>Current: $${product.current_price}</p>
    <p>Ad Value: $${product.ad_value ?? 0}</p>
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
  if (newPrice) formData.append('current-price', newPrice);
  if (newAd) formData.append('ad-value', newAd);
  if (newDate) formData.append('active-until', newDate);

  await fetch(`/update/${id}`, { method: 'POST', body: formData });
  loadProducts();
}

async function deleteProduct(id) {
  await fetch(`/delete/${id}`, { method: 'POST' });
  loadProducts();
}

loadProducts();
