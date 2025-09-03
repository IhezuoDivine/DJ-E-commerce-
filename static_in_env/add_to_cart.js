document.addEventListener("DOMContentLoaded", function () {
  // Selectors
  const addToCartButtons = document.querySelectorAll(".add-to-cart");
  const cartCount = document.getElementById("cart-count");
  const cartItems = document.getElementById("cart-items");
  const cartTotal = document.getElementById("cart-total");

  // Cart array to store items
  let cart = [];

  // Function: Add item to cart
  function addToCart(e) {
    const button = e.target;
    const item = {
      id: button.getAttribute("data-id"),
      name: button.getAttribute("data-name"),
      price: parseFloat(button.getAttribute("data-price")),
    };

    // Push item into cart
    cart.push(item);

    // Update cart
    updateCart();
  }

  // Function: Remove item from cart
  function removeFromCart(index) {
    cart.splice(index, 1); // remove 1 item at given index
    updateCart();
  }

  // Function: Update cart display
  function updateCart() {
    // Update count
    cartCount.textContent = cart.length;

    // Clear cart UI
    cartItems.innerHTML = "";

    // Re-render cart
    let total = 0;
    cart.forEach((item, index) => {
      const li = document.createElement("li");
      li.textContent = `${item.name} - $${item.price}`;

      // Add remove button
      const removeBtn = document.createElement("button");
      removeBtn.textContent = "Remove";
      removeBtn.style.marginLeft = "10px";
      removeBtn.addEventListener("click", () => removeFromCart(index));

      li.appendChild(removeBtn);
      cartItems.appendChild(li);

      total += item.price;
    });

    // Update total
    cartTotal.textContent = total.toFixed(2);
  }

  // Attach event listeners
  addToCartButtons.forEach((button) => {
    button.addEventListener("click", addToCart);
  });
});
