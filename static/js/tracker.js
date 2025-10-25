const form = document.getElementById('tracker-form');
const productList = document.getElementById('products');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(form);

  const response = await fetch('/upload', {
    method: 'POST',
    body: formData
  });
  const product = await response.json();
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
    <img src="${product.image}" alt="${product.name}" />
    <h3>${product.name}</h3>
    <p>Initial: $${product.initial_price}</p>
    <p>Current: $<span id="curr-${product.id}">${product.current_price}</span></p>
    <p><strong>Profit:</strong> 
      <span id="profit-${product.id}" style="color:${profit >= 0 ? 'green' : 'red'};">
        $${profit}
      </span>
    </p>
    <input type="number" id="edit-${product.id}" placeholder="New current price" step="0.01" />
    <button onclick="updatePrice(${product.id})">Update</button>
    <button onclick="deleteProduct(${product.id})" style="background-color:red;">Delete</button>
  `;
  productList.appendChild(div);
}

async function updatePrice(id) {
  const newPrice = document.getElementById(`edit-${id}`).value;
  if (!newPrice) return alert('Enter a price first');

  const formData = new FormData();
  formData.append('current-price', newPrice);

  const res = await fetch(`/update/${id}`, {
    method: 'POST',
    body: formData
  });
  await res.json();
  loadProducts();
}

async function deleteProduct(id) {
  if (!confirm('Are you sure you want to delete this product?')) return;

  const res = await fetch(`/delete/${id}`, { method: 'POST' });
  await res.json();
  loadProducts();
}

// Initial load
loadProducts();
