import { api, escapeHtml, showToast } from "./api.js";

const itemsEl = document.getElementById("items");
const basketEl = document.getElementById("basket-lines");
const quoteBtn = document.getElementById("quote-btn");
const totalEl = document.getElementById("total");

const basket = new Map(); // item_id -> quantity
let items = [];

function renderItems() {
  itemsEl.innerHTML = items.map((item) => {
    const out = item.availability === "out_of_stock";
    const usd = item.approx_usd ? `<small> (about ${escapeHtml(item.approx_usd)} USD)</small>` : "";
    return `
      <article class="card">
        <h3>${escapeHtml(item.name)}</h3>
        <div class="desc">${escapeHtml(item.description)}</div>
        <div class="meta">${escapeHtml(item.weight_kg)} kg</div>
        <div class="price">${escapeHtml(item.price)} ${escapeHtml(item.currency)}${usd}</div>
        <span class="badge ${item.availability}">${out ? "Out of stock" : `${item.quantity} in stock`}</span>
        <div class="row">
          <input type="number" min="1" max="1000" value="1" id="qty-${item.id}" ${out ? "disabled" : ""} aria-label="Quantity for ${escapeHtml(item.name)}">
          <button data-add="${item.id}" ${out ? "disabled" : ""}>Add</button>
        </div>
      </article>`;
  }).join("");
}

function renderBasket() {
  if (basket.size === 0) {
    basketEl.innerHTML = '<li class="empty">Your basket is empty</li>';
    quoteBtn.disabled = true;
    return;
  }
  basketEl.innerHTML = [...basket.entries()].map(([id, qty]) => {
    const item = items.find((i) => i.id === id);
    return `<li><span>${escapeHtml(item ? item.name : `#${id}`)} x ${qty}</span>
            <button class="secondary" data-remove="${id}" aria-label="Remove">x</button></li>`;
  }).join("");
  quoteBtn.disabled = false;
}

function renderQuote(quote) {
  const lines = quote.lines.map((l) =>
    `<li><span>${escapeHtml(l.name)} x ${l.quantity}</span><span>${l.line_total}</span></li>`
  ).join("");
  basketEl.innerHTML = lines;
  totalEl.textContent = `Total: ${quote.total} ${quote.currency}`;
}

async function loadItems() {
  try {
    items = await api("/api/catalog/items");
    renderItems();
  } catch (err) {
    itemsEl.innerHTML = `<p class="empty">Could not load the catalog: ${escapeHtml(err.message)}</p>`;
  }
}

itemsEl.addEventListener("click", (event) => {
  const id = Number(event.target.dataset.add);
  if (!id) return;
  const qty = Number(document.getElementById(`qty-${id}`).value) || 1;
  basket.set(id, (basket.get(id) || 0) + qty);
  totalEl.textContent = "";
  renderBasket();
});

basketEl.addEventListener("click", (event) => {
  const id = Number(event.target.dataset.remove);
  if (!id) return;
  basket.delete(id);
  totalEl.textContent = "";
  renderBasket();
});

quoteBtn.addEventListener("click", async () => {
  const payload = { items: [...basket.entries()].map(([item_id, quantity]) => ({ item_id, quantity })) };
  try {
    const quote = await api("/api/catalog/quote", { method: "POST", body: payload });
    renderQuote(quote);
  } catch (err) {
    showToast(err.message, true);
  }
});

renderBasket();
loadItems();
