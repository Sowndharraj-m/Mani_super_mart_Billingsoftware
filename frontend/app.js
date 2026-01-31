// Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State Management
let currentBill = {
    items: [],
    customerId: null,
    customerName: 'Walk-in Customer',
    paymentMode: 'cash',
    discount: 0,
    couponCode: null
};

let allProducts = [];
let allCustomers = [];
let allCoupons = [];
let allOffers = [];
let heldBills = [];

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    updateClock();
    setInterval(updateClock, 1000);
    
    // Load initial data
    loadProducts();
    loadCustomers();
    loadCoupons();
    loadOffers();
    loadDashboardStats();
    initializeDatabase();
});

// Clock Update
function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    document.getElementById('current-time').textContent = timeStr;
}

// Tab Management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Add active class to clicked button
    event.target.closest('.nav-btn').classList.add('active');
    
    // Load data when tab changes
    if (tabName === 'customers') {
        loadAllCustomers();
    } else if (tabName === 'products') {
        loadAllProducts();
    } else if (tabName === 'discounts') {
        loadAllCoupons();
        loadAllOffers();
    } else if (tabName === 'reports') {
        loadDashboardStats();
        loadHeldBills();
        loadLowStockProducts();
    }
}

// ==================== BILLING FUNCTIONS ====================

// Search Products
function searchProducts() {
    const query = document.getElementById('product-search').value;
    
    if (query.length < 1) {
        document.getElementById('search-results').innerHTML = '';
        return;
    }
    
    const filtered = allProducts.filter(p =>
        p.name.toLowerCase().includes(query.toLowerCase()) ||
        p.barcode.includes(query)
    );
    
    displaySearchResults(filtered);
}

function displaySearchResults(products) {
    const resultsDiv = document.getElementById('search-results');
    
    if (products.length === 0) {
        resultsDiv.innerHTML = '<div class="product-item" style="text-align: center; color: #9ca3af;">No products found</div>';
        return;
    }
    
    resultsDiv.innerHTML = products.map(p => `
        <div class="product-item" onclick="addProductToBill('${p.id}', '${p.name}', ${p.price}, ${p.quantity})">
            <div class="product-info">
                <div>
                    <div class="product-name">${p.name}</div>
                    <div class="product-qty">Stock: ${p.quantity}</div>
                </div>
                <div class="product-price">₹${p.price.toFixed(2)}</div>
            </div>
        </div>
    `).join('');
}

// Filter by Category
function filterByCategory(category) {
    const filtered = allProducts.filter(p => p.category === category);
    displaySearchResults(filtered);
}

// Handle Barcode Input
function handleBarcodeInput(event) {
    if (event.key === 'Enter') {
        const barcode = event.target.value;
        const product = allProducts.find(p => p.barcode === barcode);
        
        if (product) {
            addProductToBill(product.id, product.name, product.price, product.quantity);
            event.target.value = '';
        } else {
            showToast('Product not found', 'error');
        }
    }
}

// Add Product to Bill
function addProductToBill(productId, productName, price, stock) {
    if (stock <= 0) {
        showToast('Product out of stock', 'error');
        return;
    }
    
    const existingItem = currentBill.items.find(item => item.product_id === productId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        currentBill.items.push({
            product_id: productId,
            product_name: productName,
            quantity: 1,
            unit_price: price,
            discount: 0,
            total: price
        });
    }
    
    updateBillDisplay();
    document.getElementById('product-search').value = '';
    document.getElementById('search-results').innerHTML = '';
}

// Update Bill Display
function updateBillDisplay() {
    const itemsBody = document.getElementById('bill-items-body');
    
    if (currentBill.items.length === 0) {
        itemsBody.innerHTML = '<tr class="empty-row"><td colspan="6" class="empty-message">No items added yet</td></tr>';
        updateBillSummary();
        return;
    }
    
    itemsBody.innerHTML = currentBill.items.map((item, index) => `
        <tr>
            <td>${item.product_name}</td>
            <td>
                <input type="number" class="qty-input" value="${item.quantity}" 
                       onchange="updateQuantity(${index}, this.value)">
            </td>
            <td>₹${item.unit_price.toFixed(2)}</td>
            <td>
                <input type="number" style="width: 50px; padding: 4px;" value="${item.discount}" 
                       onchange="updateItemDiscount(${index}, this.value)">
            </td>
            <td>₹${(item.unit_price * item.quantity - item.discount).toFixed(2)}</td>
            <td>
                <button class="remove-btn" onclick="removeItemFromBill(${index})">Remove</button>
            </td>
        </tr>
    `).join('');
    
    updateBillSummary();
}

function updateQuantity(index, newQuantity) {
    currentBill.items[index].quantity = parseInt(newQuantity) || 1;
    updateBillDisplay();
}

function updateItemDiscount(index, discount) {
    currentBill.items[index].discount = parseFloat(discount) || 0;
    updateBillDisplay();
}

function removeItemFromBill(index) {
    currentBill.items.splice(index, 1);
    updateBillDisplay();
}

// Update Bill Summary
function updateBillSummary() {
    let subtotal = 0;
    currentBill.items.forEach(item => {
        subtotal += (item.unit_price * item.quantity) - item.discount;
    });
    
    let discount = currentBill.discount;
    let tax = (subtotal - discount) * 0.05;
    let total = subtotal - discount + tax;
    
    document.getElementById('subtotal').textContent = '₹' + subtotal.toFixed(2);
    document.getElementById('tax').textContent = '₹' + tax.toFixed(2);
    document.getElementById('total').textContent = '₹' + total.toFixed(2);
    
    if (discount > 0) {
        document.getElementById('discount-row').style.display = 'flex';
        document.getElementById('discount').textContent = '-₹' + discount.toFixed(2);
    } else {
        document.getElementById('discount-row').style.display = 'none';
    }
}

// Search Customer
function searchCustomer() {
    const mobile = document.getElementById('customer-mobile').value;
    
    if (mobile.length < 10) {
        document.getElementById('customer-name').textContent = 'Walk-in Customer';
        currentBill.customerId = null;
        return;
    }
    
    fetch(`${API_BASE_URL}/customers/mobile/${mobile}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                currentBill.customerId = data.data.id;
                document.getElementById('customer-name').textContent = data.data.name;
            }
        })
        .catch(err => console.error(err));
}

// Apply Coupon
function applyCoupon() {
    const couponCode = document.getElementById('coupon-code').value;
    
    if (!couponCode) {
        showToast('Please enter coupon code', 'warning');
        return;
    }
    
    let subtotal = 0;
    currentBill.items.forEach(item => {
        subtotal += (item.unit_price * item.quantity) - item.discount;
    });
    
    fetch(`${API_BASE_URL}/discounts/validate-coupon/${couponCode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ purchase_amount: subtotal })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                currentBill.discount = data.data.discount_amount;
                currentBill.couponCode = couponCode;
                updateBillSummary();
                showToast(`Coupon applied! Discount: ₹${data.data.discount_amount.toFixed(2)}`, 'success');
            } else {
                showToast(data.error, 'error');
            }
        })
        .catch(err => {
            showToast('Invalid coupon code', 'error');
        });
}

// Select Payment Mode
function selectPayment(mode) {
    currentBill.paymentMode = mode;
    
    document.querySelectorAll('.payment-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('.payment-details').forEach(div => div.style.display = 'none');
    
    if (mode === 'upi') {
        document.getElementById('upi-details').style.display = 'block';
    } else if (mode === 'card') {
        document.getElementById('card-details').style.display = 'block';
    } else if (mode === 'wallet') {
        document.getElementById('wallet-details').style.display = 'block';
    } else if (mode === 'split') {
        document.getElementById('split-details').style.display = 'block';
    }
}

// Complete Bill
function completeBill() {
    if (currentBill.items.length === 0) {
        showToast('Add items to bill first', 'warning');
        return;
    }
    
    const billData = {
        customer_id: currentBill.customerId,
        items: currentBill.items,
        discount: currentBill.discount,
        coupon_code: currentBill.couponCode,
        payment_mode: currentBill.paymentMode
    };
    
    fetch(`${API_BASE_URL}/bills/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(billData)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast('Bill completed successfully!', 'success');
                printBill(data.data);
                clearBill();
            } else {
                showToast(data.error, 'error');
            }
        })
        .catch(err => {
            showToast('Error creating bill', 'error');
            console.error(err);
        });
}

function printBill(billData) {
    const printContent = `
        <div style="text-align: center; font-family: monospace; width: 80mm;">
            <h2>MANI SUPER MART</h2>
            <p>Bill #: ${billData.bill_number}</p>
            <p>Date: ${new Date().toLocaleString()}</p>
            <hr>
            <p>Items:</p>
            <table style="width: 100%;">
                ${currentBill.items.map(item => `
                    <tr>
                        <td>${item.product_name}</td>
                        <td>${item.quantity} x ₹${item.unit_price.toFixed(2)}</td>
                        <td>₹${(item.unit_price * item.quantity - item.discount).toFixed(2)}</td>
                    </tr>
                `).join('')}
            </table>
            <hr>
            <p>Subtotal: ₹${billData.subtotal.toFixed(2)}</p>
            <p>Discount: ₹${billData.discount.toFixed(2)}</p>
            <p>Tax: ₹${billData.tax.toFixed(2)}</p>
            <h3>Total: ₹${billData.total.toFixed(2)}</h3>
            <p>Payment Mode: ${currentBill.paymentMode.toUpperCase()}</p>
            <hr>
            <p>Thank you for shopping!</p>
        </div>
    `;
    
    const printWindow = window.open('', '', 'height=400,width=600');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
}

// Hold Bill
function holdBill() {
    if (currentBill.items.length === 0) {
        showToast('Add items to bill first', 'warning');
        return;
    }
    
    const billData = {
        customer_id: currentBill.customerId,
        items: currentBill.items,
        discount: currentBill.discount,
        coupon_code: currentBill.couponCode,
        hold: true
    };
    
    fetch(`${API_BASE_URL}/bills/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(billData)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast('Bill held successfully!', 'success');
                clearBill();
            } else {
                showToast(data.error, 'error');
            }
        })
        .catch(err => {
            showToast('Error holding bill', 'error');
            console.error(err);
        });
}

// Clear Bill
function clearBill() {
    currentBill = {
        items: [],
        customerId: null,
        customerName: 'Walk-in Customer',
        paymentMode: 'cash',
        discount: 0,
        couponCode: null
    };
    
    document.getElementById('bill-number').textContent = 'NEW';
    document.getElementById('customer-mobile').value = '';
    document.getElementById('customer-name').textContent = 'Walk-in Customer';
    document.getElementById('coupon-code').value = '';
    updateBillDisplay();
}

// ==================== CUSTOMER FUNCTIONS ====================

function showAddCustomerForm() {
    document.getElementById('customer-modal').style.display = 'block';
}

function closeCustomerModal() {
    document.getElementById('customer-modal').style.display = 'none';
    document.getElementById('cust-name').value = '';
    document.getElementById('cust-mobile').value = '';
    document.getElementById('cust-email').value = '';
}

function saveCustomer(event) {
    event.preventDefault();
    
    const customerData = {
        name: document.getElementById('cust-name').value,
        mobile: document.getElementById('cust-mobile').value,
        email: document.getElementById('cust-email').value
    };
    
    fetch(`${API_BASE_URL}/customers/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customerData)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast('Customer created successfully!', 'success');
                closeCustomerModal();
                loadAllCustomers();
            } else {
                showToast(data.error || 'Error creating customer', 'error');
            }
        })
        .catch(err => {
            showToast('Error creating customer', 'error');
            console.error(err);
        });
}

function loadCustomers() {
    fetch(`${API_BASE_URL}/customers/`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                allCustomers = data.data;
            }
        })
        .catch(err => console.error(err));
}

function loadAllCustomers() {
    fetch(`${API_BASE_URL}/customers/`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayCustomers(data.data);
            }
        })
        .catch(err => console.error(err));
}

function displayCustomers(customers) {
    const tbody = document.getElementById('customers-body');
    
    if (customers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-message">No customers found</td></tr>';
        return;
    }
    
    tbody.innerHTML = customers.map(customer => `
        <tr>
            <td>${customer.name}</td>
            <td>${customer.mobile}</td>
            <td>₹${customer.total_purchases.toFixed(2)}</td>
            <td>${customer.points} points</td>
            <td>
                <button class="btn btn-primary" style="padding: 6px 10px; font-size: 12px;" 
                        onclick="viewCustomerHistory('${customer.id}')">History</button>
            </td>
        </tr>
    `).join('');
}

function searchAllCustomers() {
    const query = document.getElementById('customer-search').value;
    
    fetch(`${API_BASE_URL}/customers/search?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayCustomers(data.data);
            }
        })
        .catch(err => console.error(err));
}

// ==================== PRODUCT FUNCTIONS ====================

function showAddProductForm() {
    document.getElementById('product-modal').style.display = 'block';
}

function closeProductModal() {
    document.getElementById('product-modal').style.display = 'none';
    document.getElementById('prod-barcode').value = '';
    document.getElementById('prod-name').value = '';
    document.getElementById('prod-category').value = '';
    document.getElementById('prod-price').value = '';
    document.getElementById('prod-quantity').value = '';
    document.getElementById('prod-reorder').value = '';
}

function saveProduct(event) {
    event.preventDefault();
    
    const productData = {
        barcode: document.getElementById('prod-barcode').value,
        name: document.getElementById('prod-name').value,
        category: document.getElementById('prod-category').value,
        price: parseFloat(document.getElementById('prod-price').value),
        quantity: parseInt(document.getElementById('prod-quantity').value),
        reorder_level: parseInt(document.getElementById('prod-reorder').value)
    };
    
    fetch(`${API_BASE_URL}/products/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast('Product created successfully!', 'success');
                closeProductModal();
                loadAllProducts();
            } else {
                showToast(data.error || 'Error creating product', 'error');
            }
        })
        .catch(err => {
            showToast('Error creating product', 'error');
            console.error(err);
        });
}

function loadProducts() {
    fetch(`${API_BASE_URL}/products/`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                allProducts = data.data;
            }
        })
        .catch(err => console.error(err));
}

function loadAllProducts() {
    fetch(`${API_BASE_URL}/products/`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayProducts(data.data);
            }
        })
        .catch(err => console.error(err));
}

function displayProducts(products) {
    const tbody = document.getElementById('products-body');
    
    if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-message">No products found</td></tr>';
        return;
    }
    
    tbody.innerHTML = products.map(product => {
        const status = product.quantity <= product.reorder_level ? 
            '<span class="status-badge status-low">Low Stock</span>' : 
            '<span class="status-badge status-ok">OK</span>';
        
        return `
            <tr>
                <td>${product.barcode}</td>
                <td>${product.name}</td>
                <td>${product.category}</td>
                <td>₹${product.price.toFixed(2)}</td>
                <td>${product.quantity}</td>
                <td>${status}</td>
                <td>
                    <button class="btn btn-primary" style="padding: 6px 10px; font-size: 12px;">Edit</button>
                </td>
            </tr>
        `;
    }).join('');
}

function searchProductsTab() {
    const query = document.getElementById('product-search-tab').value;
    
    fetch(`${API_BASE_URL}/products/search?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayProducts(data.data);
            }
        })
        .catch(err => console.error(err));
}

// ==================== DISCOUNT FUNCTIONS ====================

function loadCoupons() {
    fetch(`${API_BASE_URL}/discounts/coupons`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                allCoupons = data.data;
            }
        })
        .catch(err => console.error(err));
}

function loadOffers() {
    fetch(`${API_BASE_URL}/discounts/offers`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                allOffers = data.data;
            }
        })
        .catch(err => console.error(err));
}

function showAddCouponForm() {
    document.getElementById('coupon-modal').style.display = 'block';
}

function closeCouponModal() {
    document.getElementById('coupon-modal').style.display = 'none';
}

function saveCoupon(event) {
    event.preventDefault();
    
    const couponData = {
        code: document.getElementById('coup-code').value,
        discount_type: document.getElementById('coup-type').value,
        discount_value: parseFloat(document.getElementById('coup-value').value),
        min_purchase: parseFloat(document.getElementById('coup-min').value) || 0,
        max_uses: parseInt(document.getElementById('coup-max').value) || null,
        valid_from: document.getElementById('coup-from').value,
        valid_till: document.getElementById('coup-till').value,
        active: true
    };
    
    fetch(`${API_BASE_URL}/discounts/coupons`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(couponData)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast('Coupon created successfully!', 'success');
                closeCouponModal();
                loadAllCoupons();
            } else {
                showToast(data.error || 'Error creating coupon', 'error');
            }
        })
        .catch(err => {
            showToast('Error creating coupon', 'error');
            console.error(err);
        });
}

function loadAllCoupons() {
    fetch(`${API_BASE_URL}/discounts/coupons`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayCoupons(data.data);
            }
        })
        .catch(err => console.error(err));
}

function displayCoupons(coupons) {
    const tbody = document.getElementById('coupons-body');
    
    if (coupons.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-message">No coupons found</td></tr>';
        return;
    }
    
    tbody.innerHTML = coupons.map(coupon => {
        const validTill = new Date(coupon.valid_till);
        const isExpired = validTill < new Date();
        
        return `
            <tr>
                <td><strong>${coupon.code}</strong></td>
                <td>${coupon.discount_type === 'percentage' ? coupon.discount_value + '%' : '₹' + coupon.discount_value}</td>
                <td>₹${coupon.min_purchase}</td>
                <td>${coupon.current_uses}/${coupon.max_uses || '∞'}</td>
                <td>${validTill.toLocaleDateString()}</td>
                <td>${isExpired ? '<span class="status-badge status-low">Expired</span>' : '<span class="status-badge status-ok">Active</span>'}</td>
            </tr>
        `;
    }).join('');
}

function showAddOfferForm() {
    document.getElementById('offer-modal').style.display = 'block';
}

function closeOfferModal() {
    document.getElementById('offer-modal').style.display = 'none';
}

function saveOffer(event) {
    event.preventDefault();
    
    const offerData = {
        name: document.getElementById('off-name').value,
        offer_type: document.getElementById('off-type').value,
        discount_value: parseFloat(document.getElementById('off-discount').value),
        min_quantity: parseInt(document.getElementById('off-min-qty').value) || 1,
        valid_from: document.getElementById('off-from').value,
        valid_till: document.getElementById('off-till').value,
        active: true
    };
    
    fetch(`${API_BASE_URL}/discounts/offers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(offerData)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast('Offer created successfully!', 'success');
                closeOfferModal();
                loadAllOffers();
            } else {
                showToast(data.error || 'Error creating offer', 'error');
            }
        })
        .catch(err => {
            showToast('Error creating offer', 'error');
            console.error(err);
        });
}

function loadAllOffers() {
    fetch(`${API_BASE_URL}/discounts/offers`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayOffers(data.data);
            }
        })
        .catch(err => console.error(err));
}

function displayOffers(offers) {
    const tbody = document.getElementById('offers-body');
    
    if (offers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-message">No offers found</td></tr>';
        return;
    }
    
    tbody.innerHTML = offers.map(offer => {
        const validFrom = new Date(offer.valid_from);
        const validTill = new Date(offer.valid_till);
        
        return `
            <tr>
                <td>${offer.name}</td>
                <td>${offer.offer_type}</td>
                <td>₹${offer.discount_value}</td>
                <td>${validFrom.toLocaleDateString()}</td>
                <td>${validTill.toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-primary" style="padding: 6px 10px; font-size: 12px;">Edit</button>
                </td>
            </tr>
        `;
    }).join('');
}

// ==================== REPORTS FUNCTIONS ====================

function loadDashboardStats() {
    fetch(`${API_BASE_URL}/dashboard/stats`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const stats = data.data;
                document.getElementById('today-sales').textContent = '₹' + stats.today.sales.toFixed(2);
                document.getElementById('today-count').textContent = stats.today.transactions;
                document.getElementById('avg-bill').textContent = '₹' + stats.today.average_bill.toFixed(2);
                document.getElementById('total-customers').textContent = stats.total_customers;
                document.getElementById('total-products').textContent = stats.total_products;
            }
        })
        .catch(err => console.error(err));
}

function loadHeldBills() {
    fetch(`${API_BASE_URL}/bills/hold-list`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayHeldBills(data.data);
            }
        })
        .catch(err => console.error(err));
}

function displayHeldBills(bills) {
    const tbody = document.getElementById('held-bills-body');
    
    if (bills.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-message">No held bills</td></tr>';
        return;
    }
    
    tbody.innerHTML = bills.map(bill => {
        const date = new Date(bill.created_at);
        return `
            <tr>
                <td>${bill.bill_number}</td>
                <td>${bill.customer_id ? 'Customer' : 'Walk-in'}</td>
                <td>₹${bill.total.toFixed(2)}</td>
                <td>${date.toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-primary" style="padding: 6px 10px; font-size: 12px;">Resume</button>
                </td>
            </tr>
        `;
    }).join('');
}

function loadLowStockProducts() {
    fetch(`${API_BASE_URL}/products/low-stock`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayLowStock(data.data);
            }
        })
        .catch(err => console.error(err));
}

function displayLowStock(products) {
    const tbody = document.getElementById('low-stock-body');
    
    if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-message">All products in stock</td></tr>';
        return;
    }
    
    tbody.innerHTML = products.map(product => `
        <tr>
            <td>${product.name}</td>
            <td>${product.quantity}</td>
            <td>${product.reorder_level}</td>
            <td><span class="status-badge status-low">Low Stock</span></td>
        </tr>
    `).join('');
}

// ==================== RETURN DIALOG ====================

function showReturnDialog() {
    document.getElementById('return-modal').style.display = 'block';
}

function closeReturnDialog() {
    document.getElementById('return-modal').style.display = 'none';
}

function searchBillsForReturn() {
    const query = document.getElementById('return-bill-search').value;
    // Search bills implementation
}

// ==================== SETTINGS ====================

function initializeDatabase() {
    fetch(`${API_BASE_URL}/init-db`, {
        method: 'POST'
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                loadProducts();
                loadCustomers();
                loadCoupons();
                loadOffers();
            }
        })
        .catch(err => console.error(err));
}

function saveSettings() {
    // Implement settings save
    showToast('Settings saved successfully!', 'success');
}

// ==================== UTILITY FUNCTIONS ====================

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast show ' + type;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function confirmReset() {
    if (confirm('Are you sure you want to reset all data? This cannot be undone.')) {
        // Implement reset
        showToast('Database reset', 'warning');
    }
}

// Close modals when clicking outside
window.onclick = function(event) {
    const customerModal = document.getElementById('customer-modal');
    const productModal = document.getElementById('product-modal');
    const couponModal = document.getElementById('coupon-modal');
    const offerModal = document.getElementById('offer-modal');
    const returnModal = document.getElementById('return-modal');
    
    if (event.target === customerModal) customerModal.style.display = 'none';
    if (event.target === productModal) productModal.style.display = 'none';
    if (event.target === couponModal) couponModal.style.display = 'none';
    if (event.target === offerModal) offerModal.style.display = 'none';
    if (event.target === returnModal) returnModal.style.display = 'none';
}
