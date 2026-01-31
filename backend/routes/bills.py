from flask import Blueprint, request, jsonify
from models.database import db, Bill, BillItem, Product, Customer, Transaction, InventoryLog, Coupon, Offer
from datetime import datetime
import uuid

bills_bp = Blueprint('bills', __name__, url_prefix='/api/bills')

def calculate_bill_total(items, discount=0, coupon_code=None):
    """Calculate bill total with discounts"""
    subtotal = 0
    
    for item in items:
        product = Product.query.get(item['product_id'])
        if product:
            item_total = product.price * item['quantity'] - item.get('discount', 0)
            subtotal += item_total
    
    discount_amount = 0
    
    # Apply coupon if provided
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code, active=True).first()
        if coupon and coupon.current_uses < (coupon.max_uses or float('inf')):
            if coupon.discount_type == 'percentage':
                discount_amount = (subtotal * coupon.discount_value) / 100
            else:
                discount_amount = coupon.discount_value
    
    # Apply additional discount
    discount_amount += discount
    
    tax = (subtotal - discount_amount) * 0.05  # 5% tax
    total = subtotal - discount_amount + tax
    
    return {
        'subtotal': subtotal,
        'discount': discount_amount,
        'tax': tax,
        'total': total
    }

@bills_bp.route('/', methods=['POST'])
def create_bill():
    """Create a new bill"""
    data = request.json
    
    if not data or 'items' not in data:
        return jsonify({'error': 'Missing items'}), 400
    
    bill_number = f"BILL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    bill = Bill(
        bill_number=bill_number,
        customer_id=data.get('customer_id'),
        payment_mode=data.get('payment_mode', 'cash'),
        status='hold' if data.get('hold') else 'completed'
    )
    
    # Calculate totals
    totals = calculate_bill_total(
        data['items'],
        data.get('discount', 0),
        data.get('coupon_code')
    )
    
    bill.subtotal = totals['subtotal']
    bill.discount = totals['discount']
    bill.tax = totals['tax']
    bill.total = totals['total']
    
    # Add items to bill
    for item in data['items']:
        product = Product.query.get(item['product_id'])
        
        if not product:
            return jsonify({'error': f"Product {item['product_id']} not found"}), 404
        
        if product.quantity < item['quantity']:
            return jsonify({'error': f"Insufficient stock for {product.name}"}), 400
        
        bill_item = BillItem(
            product_id=item['product_id'],
            quantity=item['quantity'],
            unit_price=product.price,
            discount=item.get('discount', 0),
            total=product.price * item['quantity'] - item.get('discount', 0)
        )
        
        bill.items.append(bill_item)
        
        # Update stock
        product.quantity -= item['quantity']
        
        # Log inventory change
        log = InventoryLog(
            product_id=item['product_id'],
            quantity_change=-item['quantity'],
            reason='sale',
            bill_id=bill.id
        )
        db.session.add(log)
    
    # Update coupon usage
    if data.get('coupon_code'):
        coupon = Coupon.query.filter_by(code=data.get('coupon_code')).first()
        if coupon:
            coupon.current_uses += 1
    
    db.session.add(bill)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Bill created',
        'data': {
            'bill_id': bill.id,
            'bill_number': bill.bill_number,
            'subtotal': bill.subtotal,
            'discount': bill.discount,
            'tax': bill.tax,
            'total': bill.total,
            'status': bill.status
        }
    }), 201

@bills_bp.route('/<bill_id>', methods=['GET'])
def get_bill(bill_id):
    """Get bill details"""
    bill = Bill.query.get(bill_id)
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': bill.id,
            'bill_number': bill.bill_number,
            'customer_id': bill.customer_id,
            'subtotal': bill.subtotal,
            'discount': bill.discount,
            'tax': bill.tax,
            'total': bill.total,
            'payment_mode': bill.payment_mode,
            'status': bill.status,
            'created_at': bill.created_at.isoformat(),
            'items': [{
                'product_id': item.product_id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'discount': item.discount,
                'total': item.total
            } for item in bill.items]
        }
    })

@bills_bp.route('/<bill_id>/hold', methods=['POST'])
def hold_bill(bill_id):
    """Hold/suspend a bill"""
    bill = Bill.query.get(bill_id)
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    bill.status = 'hold'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Bill held successfully'
    })

@bills_bp.route('/<bill_id>/resume', methods=['POST'])
def resume_bill(bill_id):
    """Resume a held bill"""
    bill = Bill.query.get(bill_id)
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    if bill.status != 'hold':
        return jsonify({'error': 'Bill is not on hold'}), 400
    
    bill.status = 'completed'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Bill resumed successfully'
    })

@bills_bp.route('/hold-list', methods=['GET'])
def get_hold_bills():
    """Get all held bills"""
    bills = Bill.query.filter_by(status='hold').all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': b.id,
            'bill_number': b.bill_number,
            'customer_id': b.customer_id,
            'total': b.total,
            'created_at': b.created_at.isoformat()
        } for b in bills]
    })

@bills_bp.route('/<bill_id>/return', methods=['POST'])
def return_bill(bill_id):
    """Return/exchange a bill"""
    bill = Bill.query.get(bill_id)
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    # Restore stock for all items
    for item in bill.items:
        product = Product.query.get(item.product_id)
        product.quantity += item.quantity
        
        log = InventoryLog(
            product_id=item.product_id,
            quantity_change=item.quantity,
            reason='return',
            bill_id=bill_id
        )
        db.session.add(log)
    
    bill.status = 'returned'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Bill returned successfully'
    })

@bills_bp.route('/<bill_id>/duplicate', methods=['POST'])
def duplicate_bill(bill_id):
    """Create duplicate/reprint of a bill"""
    original_bill = Bill.query.get(bill_id)
    
    if not original_bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    new_bill = Bill(
        bill_number=f"DUP-{original_bill.bill_number}",
        customer_id=original_bill.customer_id,
        subtotal=original_bill.subtotal,
        discount=original_bill.discount,
        tax=original_bill.tax,
        total=original_bill.total,
        payment_mode=original_bill.payment_mode,
        status='completed'
    )
    
    # Copy items
    for item in original_bill.items:
        bill_item = BillItem(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount=item.discount,
            total=item.total
        )
        new_bill.items.append(bill_item)
    
    db.session.add(new_bill)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Bill duplicated',
        'data': {
            'bill_id': new_bill.id,
            'bill_number': new_bill.bill_number
        }
    }), 201

@bills_bp.route('/<bill_id>/payment', methods=['POST'])
def process_payment(bill_id):
    """Process payment for a bill"""
    bill = Bill.query.get(bill_id)
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    data = request.json
    payment_mode = data.get('payment_mode', 'cash')
    
    transaction = Transaction(
        bill_id=bill_id,
        payment_mode=payment_mode,
        amount=bill.total,
        reference_number=data.get('reference_number')
    )
    
    db.session.add(transaction)
    bill.payment_mode = payment_mode
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Payment processed',
        'data': {
            'transaction_id': transaction.id,
            'amount': transaction.amount,
            'status': transaction.status
        }
    })

@bills_bp.route('/summary/<date>', methods=['GET'])
def get_daily_summary(date):
    """Get daily sales summary"""
    from sqlalchemy import func
    
    bills = Bill.query.filter(
        func.date(Bill.created_at) == date,
        Bill.status == 'completed'
    ).all()
    
    total_sales = sum(b.total for b in bills)
    total_discount = sum(b.discount for b in bills)
    total_items = sum(len(b.items) for b in bills)
    
    return jsonify({
        'success': True,
        'data': {
            'date': date,
            'total_bills': len(bills),
            'total_sales': total_sales,
            'total_discount': total_discount,
            'total_items': total_items,
            'average_bill': total_sales / len(bills) if bills else 0
        }
    })
