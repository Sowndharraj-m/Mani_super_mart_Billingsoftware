from flask import Blueprint, request, jsonify
from models.database import db, Customer, Bill
from datetime import datetime

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')

@customers_bp.route('/', methods=['POST'])
def create_customer():
    """Create a new customer"""
    data = request.json
    
    if not data or not all(k in data for k in ('mobile', 'name')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if Customer.query.filter_by(mobile=data['mobile']).first():
        return jsonify({'error': 'Customer with this mobile already exists'}), 400
    
    customer = Customer(
        mobile=data['mobile'],
        name=data['name'],
        email=data.get('email')
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Customer created',
        'data': {
            'id': customer.id,
            'mobile': customer.mobile,
            'name': customer.name,
            'email': customer.email,
            'points': customer.points,
            'total_purchases': customer.total_purchases
        }
    }), 201

@customers_bp.route('/mobile/<mobile>', methods=['GET'])
def get_customer_by_mobile(mobile):
    """Get customer by mobile number"""
    customer = Customer.query.filter_by(mobile=mobile).first()
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': customer.id,
            'mobile': customer.mobile,
            'name': customer.name,
            'email': customer.email,
            'points': customer.points,
            'total_purchases': customer.total_purchases,
            'created_at': customer.created_at.isoformat()
        }
    })

@customers_bp.route('/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer details"""
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': customer.id,
            'mobile': customer.mobile,
            'name': customer.name,
            'email': customer.email,
            'points': customer.points,
            'total_purchases': customer.total_purchases,
            'created_at': customer.created_at.isoformat()
        }
    })

@customers_bp.route('/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer"""
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.json
    
    if 'name' in data:
        customer.name = data['name']
    if 'email' in data:
        customer.email = data['email']
    if 'points' in data:
        customer.points = data['points']
    
    customer.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Customer updated'
    })

@customers_bp.route('/', methods=['GET'])
def get_all_customers():
    """Get all customers with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    paginated = Customer.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'success': True,
        'data': [{
            'id': c.id,
            'mobile': c.mobile,
            'name': c.name,
            'email': c.email,
            'points': c.points,
            'total_purchases': c.total_purchases
        } for c in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    })

@customers_bp.route('/<customer_id>/purchase-history', methods=['GET'])
def get_purchase_history(customer_id):
    """Get customer purchase history"""
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    bills = Bill.query.filter_by(customer_id=customer_id).order_by(Bill.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'data': {
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'mobile': customer.mobile
            },
            'purchases': [{
                'bill_id': b.id,
                'bill_number': b.bill_number,
                'total': b.total,
                'items_count': len(b.items),
                'created_at': b.created_at.isoformat()
            } for b in bills],
            'total_purchases': customer.total_purchases,
            'loyalty_points': customer.points
        }
    })

@customers_bp.route('/<customer_id>/add-points', methods=['POST'])
def add_loyalty_points(customer_id):
    """Add loyalty points to customer"""
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.json
    points = data.get('points', 0)
    
    customer.points += points
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Points added',
        'data': {
            'customer_id': customer.id,
            'total_points': customer.points
        }
    })

@customers_bp.route('/<customer_id>/redeem-points', methods=['POST'])
def redeem_points(customer_id):
    """Redeem loyalty points"""
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.json
    points_to_redeem = data.get('points', 0)
    
    if customer.points < points_to_redeem:
        return jsonify({'error': 'Insufficient points'}), 400
    
    customer.points -= points_to_redeem
    discount = points_to_redeem / 10  # 1 point = 1 rupee discount
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Points redeemed',
        'data': {
            'customer_id': customer.id,
            'points_redeemed': points_to_redeem,
            'discount_amount': discount,
            'remaining_points': customer.points
        }
    })

@customers_bp.route('/search', methods=['GET'])
def search_customers():
    """Search customers by name or mobile"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 1:
        return jsonify({'error': 'Query too short'}), 400
    
    customers = Customer.query.filter(
        (Customer.mobile.ilike(f'%{query}%')) |
        (Customer.name.ilike(f'%{query}%'))
    ).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': c.id,
            'mobile': c.mobile,
            'name': c.name,
            'email': c.email,
            'total_purchases': c.total_purchases
        } for c in customers]
    })
