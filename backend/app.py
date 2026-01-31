from flask import Flask, jsonify
from flask_cors import CORS
from models.database import db, Product, Customer, Bill, BillItem, Coupon, Offer, Transaction, InventoryLog
from routes.products import products_bp
from routes.bills import bills_bp
from routes.customers import customers_bp
from routes.discounts import discounts_bp
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'supermart.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Initialize extensions
db.init_app(app)
CORS(app)

# Register blueprints
app.register_blueprint(products_bp)
app.register_blueprint(bills_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(discounts_bp)

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

# Initialize database
@app.before_request
def init_db():
    """Initialize database on first request"""
    pass

@app.route('/api/init-db', methods=['POST'])
def initialize_database():
    """Initialize database with sample data"""
    try:
        db.create_all()
        
        # Check if data already exists
        if Product.query.first():
            return jsonify({'success': True, 'message': 'Database already initialized'}), 200
        
        # Add sample products
        products = [
            Product(barcode='1001', name='Milk', category='Dairy', price=50, quantity=100),
            Product(barcode='1002', name='Bread', category='Bakery', price=30, quantity=80),
            Product(barcode='1003', name='Butter', category='Dairy', price=150, quantity=50),
            Product(barcode='1004', name='Rice', category='Grains', price=60, quantity=200),
            Product(barcode='1005', name='Chicken', category='Meat', price=250, quantity=30),
            Product(barcode='1006', name='Eggs', category='Dairy', price=80, quantity=100),
            Product(barcode='1007', name='Vegetables Mix', category='Vegetables', price=40, quantity=150),
            Product(barcode='1008', name='Apple', category='Fruits', price=100, quantity=50),
            Product(barcode='1009', name='Banana', category='Fruits', price=30, quantity=200),
            Product(barcode='1010', name='Salt', category='Spices', price=20, quantity=100),
        ]
        
        for product in products:
            db.session.add(product)
        
        # Add sample customers
        customers = [
            Customer(mobile='9876543210', name='John Doe', email='john@example.com'),
            Customer(mobile='9876543211', name='Jane Smith', email='jane@example.com'),
            Customer(mobile='9876543212', name='Ram Kumar', email='ram@example.com'),
        ]
        
        for customer in customers:
            db.session.add(customer)
        
        # Add sample coupon
        coupon = Coupon(
            code='SAVE10',
            discount_type='percentage',
            discount_value=10,
            min_purchase=500,
            max_uses=100,
            valid_from=datetime(2024, 1, 1),
            valid_till=datetime(2026, 12, 31),
            active=True
        )
        db.session.add(coupon)
        
        # Add sample offers
        offer = Offer(
            name='Buy 2 Get 1 Free - Bread',
            offer_type='bogo',
            discount_value=50,
            min_quantity=2,
            valid_from=datetime(2024, 1, 1),
            valid_till=datetime(2026, 12, 31),
            active=True
        )
        db.session.add(offer)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Database initialized successfully',
            'data': {
                'products': len(products),
                'customers': len(customers)
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Dashboard stats
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    today = datetime.utcnow().date()
    
    # Today's stats
    today_bills = Bill.query.filter(
        func.date(Bill.created_at) == today,
        Bill.status == 'completed'
    ).all()
    
    today_sales = sum(b.total for b in today_bills)
    today_transactions = len(today_bills)
    
    # Get total products and customers
    total_products = Product.query.count()
    total_customers = Customer.query.count()
    
    # Get top selling products
    top_products = db.session.query(
        Product.name,
        func.sum(BillItem.quantity).label('total_qty')
    ).join(BillItem).group_by(Product.id).order_by(func.sum(BillItem.quantity).desc()).limit(5).all()
    
    return jsonify({
        'success': True,
        'data': {
            'today': {
                'sales': today_sales,
                'transactions': today_transactions,
                'average_bill': today_sales / today_transactions if today_transactions > 0 else 0
            },
            'total_products': total_products,
            'total_customers': total_customers,
            'top_products': [{'name': p[0], 'quantity': p[1]} for p in top_products]
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
