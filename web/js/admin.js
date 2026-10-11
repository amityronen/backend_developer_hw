import { api, escapeHtml, showToast } from "./api.js";

const loginPanel = document.getElementById("login-panel");
const appPanel = document.getElementById("app-panel");
const tableBody = document.getElementById("rows");
const sortSelect = document.getElementById("sort");
const halfOfSelect = document.getElementById("half-of");

let token = sessionStorage.getItem("melon_token");
let items = [];

function setLoggedIn(loggedIn) {
  loginPanel.classList.toggle("hidden", loggedIn);
  appPanel.classList.toggle("hidden", !loggedIn);
}

function handleError(err) {
  if (err.status === 401) {
    sessionStorage.removeItem("melon_token");
    token = null;
    setLoggedIn(false);
  }
  showToast(err.message, true);
}

function render() {
  tableBody.innerHTML = items.map((item) => `
    <tr class="${item.is_active ? "" : "removed"}">
      <td>${item.id}</td>
      <td>${escapeHtml(item.name)}${item.half_of ? ` <small>(half of #${item.half_of})</small>` : ""}</td>
      <td>${item.price}</td>
      <td>${item.quantity}</td>
      <td>${item.is_active ? '<span class="badge in_stock">active</span>' : '<span class="badge removed">removed</span>'}</td>
      <td>${item.is_active ? `
        <div class="row">
          <input type="number" step="0.01" min="0.01" placeholder="price" id="price-${item.id}" ${item.half_of ? "disabled" : ""}>
          <button class="secondary" data-price="${item.id}" ${item.half_of ? "disabled" : ""}>Set price</button>
        </div>
        <div class="row">
          <input type="number" step="1" placeholder="+/-" id="delta-${item.id}">
          <button class="secondary" data-delta="${item.id}">Adjust</button>
          <input type="number" step="1" min="0" placeholder="set" id="qty-${item.id}">
          <button class="secondary" data-set="${item.id}">Set</button>
        </div>
        <div class="row"><button class="danger" data-remove="${item.id}">Remove</button></div>` : ""}
      </td>
    </tr>`).join("");

  const wholes = items.filter((i) => i.is_active && !i.half_of);
  halfOfSelect.innerHTML = '<option value="">(whole item)</option>' +
    wholes.map((i) => `<option value="${i.id}">${escapeHtml(i.name)}</option>`).join("");
}

async function load() {
  try {
    items = await api(`/api/admin/items?sort=${encodeURIComponent(sortSelect.value)}`, { token });
    render();
  } catch (err) {
    handleError(err);
  }
}

async function run(action, successMessage) {
  try {
    await action();
    showToast(successMessage);
    await load();
  } catch (err) {
    handleError(err);
  }
}

document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  try {
    const data = await api("/api/admin/login", {
      method: "POST",
      body: { username: form.get("username"), password: form.get("password") },
    });
    token = data.access_token;
    sessionStorage.setItem("melon_token", token);
    setLoggedIn(true);
    await load();
  } catch (err) {
    showToast(err.message, true);
  }
});

document.getElementById("logout").addEventListener("click", () => {
  sessionStorage.removeItem("melon_token");
  token = null;
  setLoggedIn(false);
});

sortSelect.addEventListener("change", load);

document.getElementById("add-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const halfOf = form.get("half_of");
  const body = { quantity: Number(form.get("quantity") || 0) };
  if (halfOf) {
    body.half_of = Number(halfOf);
  } else {
    body.name = form.get("name");
    body.description = form.get("description") || "";
    body.weight_kg = form.get("weight_kg");
    body.price = form.get("price");
  }
  run(() => api("/api/admin/items", { method: "POST", body, token }), "Item added");
});

tableBody.addEventListener("click", (event) => {
  const { price, delta, set, remove } = event.target.dataset;
  if (price) {
    const value = document.getElementById(`price-${price}`).value;
    run(() => api(`/api/admin/items/${price}/price`, { method: "PATCH", body: { price: value }, token }), "Price updated");
  } else if (delta) {
    const value = Number(document.getElementById(`delta-${delta}`).value);
    run(() => api(`/api/admin/items/${delta}/quantity`, { method: "PATCH", body: { delta: value }, token }), "Quantity adjusted");
  } else if (set) {
    const value = Number(document.getElementById(`qty-${set}`).value);
    run(() => api(`/api/admin/items/${set}/quantity`, { method: "PATCH", body: { quantity: value }, token }), "Quantity set");
  } else if (remove) {
    if (window.confirm("Remove this item from the shop?")) {
      run(() => api(`/api/admin/items/${remove}`, { method: "DELETE", token }), "Item removed");
    }
  }
});

if (token) {
  setLoggedIn(true);
  load();
} else {
  setLoggedIn(false);
}
