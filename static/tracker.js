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
  if (!formData.get('product-image')) formData.delete('product-image');

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
    ${product.image ? `<img src="${product.image}" alt="${product.name}" />` : ''}
    <h3>${product.name || 'Unnamed Product'}</h3>
    <p>Initial: ${product.initial_price || 0} lei</p>
    <p>Current: ${product.current_price || 0} lei</p>
    <p>Ad Value: ${product.ad_value || 0} lei</p>
    <p>Active Until: ${product.active_until || 'N/A'}</p>
    <p><strong>Profit:</strong> 
      <span style="color:${profit >= 0 ? 'green' : 'red'};">${profit} lei</span>
    </p>
    <input type="number" id="edit-${product.id}" placeholder="New current price" step="0.01" />
    <input type="number" id="ad-${product.id}" placeholder="New ad value" step="0.01" />
    <input type="date" id="date-${product.id}" />
    <br/>
    <input type="file" id="img-${product.id}" accept="image/*" style="margin-top:5px;" />
    <button onclick="reuploadImage(${product.id})">Reupload Image</button>
    <br/>
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

async function reuploadImage(id) {
  const fileInput = document.getElementById(`img-${id}`);
  if (!fileInput.files.length) {
    alert("Please choose an image first.");
    return;
  }

  const formData = new FormData();
  formData.append('product-image', fileInput.files[0]);

  const res = await fetch(`/update_image/${id}`, { method: 'POST', body: formData });
  if (res.ok) {
    alert("Image updated successfully!");
    loadProducts();
  } else {
    alert("Error updating image.");
  }
}

async function deleteProduct(id) {
  await fetch(`/delete/${id}`, { method: 'POST' });
  loadProducts();
}

loadProducts();
