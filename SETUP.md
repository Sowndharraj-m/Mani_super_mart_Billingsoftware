# Mani Super Mart - POS Billing Software

A complete point-of-sale (POS) billing system for supermarkets with Python Flask backend and modern HTML/CSS/JavaScript frontend.

## Features

### 🛒 Fast Billing
- Barcode scanning
- Product search by name or barcode
- Quick quantity adjustment
- Add/remove items from bill
- Real-time bill calculation

### 💳 Payment Modes
- Cash
- UPI
- Credit/Debit Card
- Wallet
- Split Payment

### 🏷️ Discounts & Offers
- Coupon management with validation
- Item-wise discounts
- Bill-wise discounts
- BOGO (Buy One Get One) offers
- Happy hour discounts
- Category-wise discounts
- Min/max purchase validation

### 👥 Customer Management
- Customer database with mobile number
- Purchase history tracking
- Loyalty points system
- Points redemption

### 📦 Inventory Management
- Product management
- Stock tracking
- Low stock alerts
- Inventory adjustments
- Stock logs

### 📋 Bill Operations
- Hold/resume bills
- Bill reprinting
- Duplicate invoices
- Bill returns with stock adjustment
- Daily sales summary

### 📊 Reports & Analytics
- Daily sales dashboard
- Top selling products
- Low stock reports
- Customer purchase history
- Transaction reports

## Project Structure

```
Mani_super_mart_Billingsoftware/
├── backend/
│   ├── models/
│   │   └── database.py          # Database models
│   ├── routes/
│   │   ├── products.py          # Product API endpoints
│   │   ├── bills.py             # Billing API endpoints
│   │   ├── customers.py         # Customer API endpoints
│   │   └── discounts.py         # Discounts API endpoints
│   ├── app.py                   # Main Flask application
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── index.html               # Main UI
│   ├── styles.css               # Styling
│   └── app.js                   # Frontend logic
└── SETUP.md                     # Setup instructions
```

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:5000`

### Frontend Setup

Simply open `frontend/index.html` in your browser, or use:

```bash
cd frontend
python -m http.server 8000
# Visit http://localhost:8000
```

## API Endpoints

### Products
- `GET /api/products/` - Get all products
- `GET /api/products/search?q=<query>` - Search products
- `GET /api/products/barcode/<barcode>` - Get product by barcode
- `POST /api/products/` - Create product
- `PUT /api/products/<id>` - Update product

### Bills
- `POST /api/bills/` - Create bill
- `GET /api/bills/<id>` - Get bill details
- `POST /api/bills/<id>/hold` - Hold bill
- `POST /api/bills/<id>/resume` - Resume held bill
- `POST /api/bills/<id>/return` - Return bill
- `POST /api/bills/<id>/duplicate` - Duplicate bill

### Customers
- `GET /api/customers/` - Get all customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/mobile/<mobile>` - Get customer by mobile

### Discounts
- `POST /api/discounts/coupons` - Create coupon
- `GET /api/discounts/coupons` - Get all coupons
- `POST /api/discounts/offers` - Create offer

## Features

### Billing
- Real-time product search and barcode scanning
- Dynamic bill calculation
- Customer identification via mobile number
- Quick category filtering

### Payment
- Multiple payment modes (Cash, UPI, Card, Wallet, Split)
- Payment reference tracking
- Transaction history

### Discounts
- Coupon validation with conditions
- Category and item-wise discounts
- BOGO and seasonal offers
- Loyalty points system

### Customer Management
- Mobile-based customer identification
- Purchase history
- Loyalty points accumulation and redemption

### Inventory
- Product stock management
- Low stock alerts
- Stock adjustment logs
- Return processing with stock restoration

### Reports
- Daily sales summary
- Top products
- Customer analytics
- Inventory status

## Database Schema

- **Products** - Inventory with barcode, name, price, stock
- **Customers** - Customer info with mobile, name, points
- **Bills** - Bill records with items and totals
- **Bill Items** - Line items in each bill
- **Transactions** - Payment records
- **Coupons** - Coupon codes and validity
- **Offers** - Promotional offers
- **Inventory Logs** - Stock change audit trail

## Usage

1. **Initialize Database** - Click "Initialize Database" in Settings
2. **Add Products** - Go to Products tab and add items
3. **Create Bill** - Search/scan products, adjust quantities
4. **Apply Offers** - Enter coupon code for discounts
5. **Select Payment** - Choose payment method
6. **Complete** - Finalize and print bill

## System Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- SQLite (included with Python)

## Configuration

Default tax rate: **5%**

To modify, go to Settings tab and update the tax rate.

## Troubleshooting

**Backend not connecting?**
- Ensure Flask is running on port 5000
- Check CORS is enabled
- Verify API_BASE_URL in app.js

**Database errors?**
- Delete `supermart.db` and reinitialize
- Check file permissions
- Verify SQLite installation

## Future Enhancements

- Email/SMS receipts
- Barcode generation
- Multi-location support
- User authentication & roles
- Advanced analytics & reports
- Offline mode
- Payment gateway integration
- GST compliance

## License

Educational & Commercial Use

## Version

1.0.0
