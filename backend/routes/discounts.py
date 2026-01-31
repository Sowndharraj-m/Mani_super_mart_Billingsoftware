from flask import Blueprint, request, jsonify
from models.database import db, Coupon, Offer
from datetime import datetime

discounts_bp = Blueprint('discounts', __name__, url_prefix='/api/discounts')

# Coupon Routes
@discounts_bp.route('/coupons', methods=['POST'])
def create_coupon():
    """Create a new coupon"""
    data = request.json
    
    if not data or not all(k in data for k in ('code', 'discount_type', 'discount_value', 'valid_from', 'valid_till')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if Coupon.query.filter_by(code=data['code']).first():
        return jsonify({'error': 'Coupon code already exists'}), 400
    
    coupon = Coupon(
        code=data['code'],
        discount_type=data['discount_type'],
        discount_value=data['discount_value'],
        min_purchase=data.get('min_purchase', 0),
        max_uses=data.get('max_uses'),
        valid_from=datetime.fromisoformat(data['valid_from']),
        valid_till=datetime.fromisoformat(data['valid_till']),
        active=data.get('active', True)
    )
    
    db.session.add(coupon)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Coupon created',
        'data': {
            'id': coupon.id,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value
        }
    }), 201

@discounts_bp.route('/coupons/<code>', methods=['GET'])
def get_coupon(code):
    """Get coupon details"""
    coupon = Coupon.query.filter_by(code=code).first()
    
    if not coupon:
        return jsonify({'error': 'Coupon not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': coupon.id,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'min_purchase': coupon.min_purchase,
            'max_uses': coupon.max_uses,
            'current_uses': coupon.current_uses,
            'valid_from': coupon.valid_from.isoformat(),
            'valid_till': coupon.valid_till.isoformat(),
            'active': coupon.active
        }
    })

@discounts_bp.route('/coupons', methods=['GET'])
def get_all_coupons():
    """Get all active coupons"""
    coupons = Coupon.query.filter_by(active=True).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': c.id,
            'code': c.code,
            'discount_type': c.discount_type,
            'discount_value': c.discount_value,
            'min_purchase': c.min_purchase,
            'current_uses': c.current_uses,
            'max_uses': c.max_uses,
            'valid_from': c.valid_from.isoformat(),
            'valid_till': c.valid_till.isoformat()
        } for c in coupons]
    })

@discounts_bp.route('/coupons/<coupon_id>', methods=['PUT'])
def update_coupon(coupon_id):
    """Update coupon"""
    coupon = Coupon.query.get(coupon_id)
    
    if not coupon:
        return jsonify({'error': 'Coupon not found'}), 404
    
    data = request.json
    
    if 'discount_value' in data:
        coupon.discount_value = data['discount_value']
    if 'active' in data:
        coupon.active = data['active']
    if 'max_uses' in data:
        coupon.max_uses = data['max_uses']
    if 'min_purchase' in data:
        coupon.min_purchase = data['min_purchase']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Coupon updated'
    })

# Offer Routes
@discounts_bp.route('/offers', methods=['POST'])
def create_offer():
    """Create a new offer"""
    data = request.json
    
    if not data or not all(k in data for k in ('name', 'offer_type', 'discount_value', 'valid_from', 'valid_till')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    offer = Offer(
        name=data['name'],
        offer_type=data['offer_type'],
        product_id=data.get('product_id'),
        category=data.get('category'),
        discount_value=data['discount_value'],
        min_quantity=data.get('min_quantity', 1),
        valid_from=datetime.fromisoformat(data['valid_from']),
        valid_till=datetime.fromisoformat(data['valid_till']),
        active=data.get('active', True)
    )
    
    db.session.add(offer)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Offer created',
        'data': {
            'id': offer.id,
            'name': offer.name,
            'offer_type': offer.offer_type,
            'discount_value': offer.discount_value
        }
    }), 201

@discounts_bp.route('/offers', methods=['GET'])
def get_all_offers():
    """Get all active offers"""
    offers = Offer.query.filter_by(active=True).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': o.id,
            'name': o.name,
            'offer_type': o.offer_type,
            'discount_value': o.discount_value,
            'min_quantity': o.min_quantity,
            'category': o.category,
            'product_id': o.product_id,
            'valid_from': o.valid_from.isoformat(),
            'valid_till': o.valid_till.isoformat()
        } for o in offers]
    })

@discounts_bp.route('/offers/<offer_id>', methods=['GET'])
def get_offer(offer_id):
    """Get offer details"""
    offer = Offer.query.get(offer_id)
    
    if not offer:
        return jsonify({'error': 'Offer not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': offer.id,
            'name': offer.name,
            'offer_type': offer.offer_type,
            'discount_value': offer.discount_value,
            'min_quantity': offer.min_quantity,
            'category': offer.category,
            'product_id': offer.product_id,
            'valid_from': offer.valid_from.isoformat(),
            'valid_till': offer.valid_till.isoformat(),
            'active': offer.active
        }
    })

@discounts_bp.route('/offers/<offer_id>', methods=['PUT'])
def update_offer(offer_id):
    """Update offer"""
    offer = Offer.query.get(offer_id)
    
    if not offer:
        return jsonify({'error': 'Offer not found'}), 404
    
    data = request.json
    
    if 'name' in data:
        offer.name = data['name']
    if 'discount_value' in data:
        offer.discount_value = data['discount_value']
    if 'active' in data:
        offer.active = data['active']
    if 'min_quantity' in data:
        offer.min_quantity = data['min_quantity']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Offer updated'
    })

@discounts_bp.route('/offers/<offer_id>', methods=['DELETE'])
def delete_offer(offer_id):
    """Delete offer"""
    offer = Offer.query.get(offer_id)
    
    if not offer:
        return jsonify({'error': 'Offer not found'}), 404
    
    db.session.delete(offer)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Offer deleted'
    })

@discounts_bp.route('/validate-coupon/<code>', methods=['POST'])
def validate_coupon(code):
    """Validate coupon"""
    data = request.json
    purchase_amount = data.get('purchase_amount', 0)
    
    coupon = Coupon.query.filter_by(code=code, active=True).first()
    
    if not coupon:
        return jsonify({'success': False, 'error': 'Invalid coupon code'}), 404
    
    if datetime.utcnow() < coupon.valid_from or datetime.utcnow() > coupon.valid_till:
        return jsonify({'success': False, 'error': 'Coupon expired'}), 400
    
    if coupon.current_uses >= (coupon.max_uses or float('inf')):
        return jsonify({'success': False, 'error': 'Coupon usage limit exceeded'}), 400
    
    if purchase_amount < coupon.min_purchase:
        return jsonify({'success': False, 'error': f'Minimum purchase amount is {coupon.min_purchase}'}), 400
    
    discount = 0
    if coupon.discount_type == 'percentage':
        discount = (purchase_amount * coupon.discount_value) / 100
    else:
        discount = coupon.discount_value
    
    return jsonify({
        'success': True,
        'data': {
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'discount_amount': discount,
            'original_amount': purchase_amount,
            'final_amount': purchase_amount - discount
        }
    })
