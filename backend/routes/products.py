from flask import Blueprint, request, jsonify
from models.database import db, Product, InventoryLog
from datetime import datetime

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('/search', methods=['GET'])
def search_products():
    """Search products by barcode or name"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 1:
        return jsonify({'error': 'Query too short'}), 400
    
    products = Product.query.filter(
        (Product.barcode.ilike(f'%{query}%')) |
        (Product.name.ilike(f'%{query}%'))
    ).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': p.id,
            'barcode': p.barcode,
            'name': p.name,
            'category': p.category,
            'price': p.price,
            'quantity': p.quantity
        } for p in products]
    })

@products_bp.route('/barcode/<barcode>', methods=['GET'])
def get_by_barcode(barcode):
    """Get product by barcode"""
    product = Product.query.filter_by(barcode=barcode).first()
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': product.id,
            'barcode': product.barcode,
            'name': product.name,
            'category': product.category,
            'price': product.price,
            'quantity': product.quantity
        }
    })

@products_bp.route('/', methods=['GET'])
def get_all_products():
    """Get all products with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    paginated = Product.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'success': True,
        'data': [{
            'id': p.id,
            'barcode': p.barcode,
            'name': p.name,
            'category': p.category,
            'price': p.price,
            'quantity': p.quantity
        } for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    })

@products_bp.route('/', methods=['POST'])
def create_product():
    """Create new product"""
    data = request.json
    
    if not data or not all(k in data for k in ('barcode', 'name', 'category', 'price')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if Product.query.filter_by(barcode=data['barcode']).first():
        return jsonify({'error': 'Barcode already exists'}), 400
    
    product = Product(
        barcode=data['barcode'],
        name=data['name'],
        category=data['category'],
        price=data['price'],
        quantity=data.get('quantity', 0),
        reorder_level=data.get('reorder_level', 10)
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Product created',
        'data': {
            'id': product.id,
            'barcode': product.barcode,
            'name': product.name,
            'category': product.category,
            'price': product.price,
            'quantity': product.quantity
        }
    }), 201

@products_bp.route('/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.json
    
    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'category' in data:
        product.category = data['category']
    if 'quantity' in data:
        product.quantity = data['quantity']
    if 'reorder_level' in data:
        product.reorder_level = data['reorder_level']
    
    product.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Product updated'
    })

@products_bp.route('/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Product deleted'
    })

@products_bp.route('/<product_id>/adjust-stock', methods=['POST'])
def adjust_stock(product_id):
    """Adjust product stock"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.json
    quantity_change = data.get('quantity_change', 0)
    reason = data.get('reason', 'adjustment')
    
    product.quantity += quantity_change
    
    log = InventoryLog(
        product_id=product_id,
        quantity_change=quantity_change,
        reason=reason
    )
    
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Stock adjusted',
        'new_quantity': product.quantity
    })

@products_bp.route('/low-stock', methods=['GET'])
def get_low_stock():
    """Get products with low stock"""
    products = Product.query.filter(Product.quantity <= Product.reorder_level).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': p.id,
            'name': p.name,
            'quantity': p.quantity,
            'reorder_level': p.reorder_level
        } for p in products]
    })
