"""优化后的产品路由"""
from flask import Blueprint, request
import logging
from models.product import Product
from services.category_service import CategoryService
from utils.api_response import APIResponse
from utils.error_handler import handle_api_errors, validate_required_fields
from utils.validators import DataValidator

logger = logging.getLogger(__name__)

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
@handle_api_errors
def get_products():
    """获取产品列表"""
    logger.debug("获取产品列表请求: %s", dict(request.args))
    
    # 获取查询参数
    search = request.args.get('search', '').strip() or None
    category_id = request.args.get('category_id', '').strip() or None
    page = DataValidator.validate_integer(request.args.get('page', 1), 'page', min_value=1)
    per_page = DataValidator.validate_integer(request.args.get('per_page', 50), 'per_page', min_value=1, max_value=100)
    
    # 处理分类过滤
    category_filter = None
    if category_id:
        try:
            category_filter = CategoryService.get_descendant_ids(category_id)
        except Exception as e:
            logger.warning("分类过滤处理失败: %s", e)
            # 回退为原始分类ID
            category_filter = DataValidator.validate_integer(category_id, 'category_id', min_value=1)
    
    # 获取产品数据
    result = Product.get_all(
        search=search,
        category_id=category_filter,
        page=page,
        per_page=per_page
    )
    
    return APIResponse.paginated(
        data=result['products'],
        total=result['pagination']['total'],
        page=page,
        per_page=per_page,
        message="获取产品列表成功"
    )

@products_bp.route('/products/categories', methods=['GET'])
@handle_api_errors
def get_product_categories():
    """获取产品分类"""
    logger.debug("获取产品分类请求")
    
    categories = CategoryService.get_categories_tree()
    
    # 为每个分类添加产品数量
    for category in categories:
        category['product_count'] = Product.count({'category_id': category['id']})
        for sub_category in category.get('children', []):
            sub_category['product_count'] = Product.count({'category_id': sub_category['id']})
    
    return APIResponse.success(
        data={'categories': categories},
        message="获取产品分类成功"
    )

@products_bp.route('/products', methods=['POST'])
@handle_api_errors
@validate_required_fields('sku', 'name')
def create_product():
    """创建产品"""
    logger.info("创建产品请求")
    data = request.get_json()
    
    # 使用验证器处理数据
    product = Product.create(**data)
    
    logger.info("产品创建成功: ID=%s, SKU=%s", product['id'], product['sku'])
    return APIResponse.created(
        data=product,
        message="产品创建成功",
        location=f"/api/products/{product['id']}"
    )

@products_bp.route('/products/<int:product_id>', methods=['GET'])
@handle_api_errors
def get_product(product_id):
    """获取单个产品"""
    logger.debug("获取产品详情: ID=%s", product_id)
    
    DataValidator.validate_integer(product_id, 'product_id', min_value=1)
    
    product = Product.get_by_id(product_id)
    if not product:
        return APIResponse.not_found("产品不存在")
    
    return APIResponse.success(
        data=product,
        message="获取产品详情成功"
    )

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@handle_api_errors
def update_product(product_id):
    """更新产品"""
    logger.info("更新产品请求: ID=%s", product_id)
    data = request.get_json()
    
    DataValidator.validate_integer(product_id, 'product_id', min_value=1)
    
    if not data:
        return APIResponse.error("请求数据不能为空")
    
    product = Product.update(product_id, **data)
    
    logger.info("产品更新成功: ID=%s", product_id)
    return APIResponse.success(
        data=product,
        message="产品更新成功"
    )

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@handle_api_errors
def delete_product(product_id):
    """删除产品"""
    logger.info("删除产品请求: ID=%s", product_id)
    
    DataValidator.validate_integer(product_id, 'product_id', min_value=1)
    
    result = Product.delete(product_id)
    
    logger.info("产品删除成功: ID=%s", product_id)
    return APIResponse.success(
        data={'deleted_count': result},
        message="产品删除成功"
    )

@products_bp.route('/products/search', methods=['GET'])
@handle_api_errors
def search_products():
    """搜索产品"""
    keyword = request.args.get('q', '').strip()
    limit = DataValidator.validate_integer(request.args.get('limit', 50), 'limit', min_value=1, max_value=100)
    
    if not keyword:
        return APIResponse.error("搜索关键词不能为空")
    
    products = Product.search_products(keyword, limit)
    
    return APIResponse.success(
        data=products,
        message=f"找到 {len(products)} 个相关产品"
    )

@products_bp.route('/products/low-stock', methods=['GET'])
@handle_api_errors
def get_low_stock_products():
    """获取低库存产品"""
    products = Product.get_low_stock_products()
    
    return APIResponse.success(
        data=products,
        message=f"找到 {len(products)} 个低库存产品"
    )

@products_bp.route('/products/zero-stock', methods=['GET'])
@handle_api_errors
def get_zero_stock_products():
    """获取零库存产品"""
    products = Product.get_zero_stock_products()
    
    return APIResponse.success(
        data=products,
        message=f"找到 {len(products)} 个零库存产品"
    )

@products_bp.route('/products/non-composite', methods=['GET'])
@handle_api_errors
def get_non_composite_products():
    """获取非复合产品（用于采购订单）"""
    keyword = request.args.get('q', '').strip()
    limit = DataValidator.validate_integer(request.args.get('limit', 50), 'limit', min_value=1, max_value=100)
    
    logger.info(f"🔍 get_non_composite_products - keyword: {keyword}, limit: {limit}")
    
    # 排除成品分类（一级分类ID=2）下的所有产品
    if keyword:
        # 使用JOIN排除成品分类
        query = '''
            SELECT p.* FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE (p.name LIKE ? OR p.sku LIKE ? OR p.description LIKE ?)
            AND (c.parent_id IS NULL OR c.parent_id != 2)
            AND (c.id IS NULL OR c.id != 2)
            ORDER BY 
                CASE 
                    WHEN p.name LIKE ? THEN 1
                    WHEN p.sku LIKE ? THEN 2
                    ELSE 3
                END,
                p.name ASC
            LIMIT ?
        '''
        search_pattern = f'%{keyword}%'
        params = [search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, limit]
        products = Product.execute_query(query, tuple(params))
    else:
        # 如果没有关键字，获取所有非成品分类的产品
        query = '''
            SELECT p.* FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE (c.parent_id IS NULL OR c.parent_id != 2)
            AND (c.id IS NULL OR c.id != 2)
            ORDER BY p.name 
            LIMIT ?
        '''
        products = Product.execute_query(query, (limit,))
    
    # 调试：检查返回的产品中是否有复合产品
    composite_products = [p for p in products if p.get('is_composite') == 1]
    if composite_products:
        logger.error(f"❌ get_non_composite_products - 返回的数据中包含复合产品: {len(composite_products)} 个")
        for p in composite_products:
            logger.error(f"  - {p.get('name')} (id: {p.get('id')}, is_composite: {p.get('is_composite')})")
    else:
        logger.info(f"✅ get_non_composite_products - 所有产品都是非复合产品")
    
    logger.info(f"🔍 get_non_composite_products - 返回 {len(products)} 个产品")
    
    return APIResponse.success(
        data=products,
        message=f"找到 {len(products)} 个非复合产品"
    )