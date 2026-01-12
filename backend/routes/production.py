from flask import Blueprint, request, jsonify
import logging
from models.production import ProductionPlan

logger = logging.getLogger(__name__)

production_bp = Blueprint('production', __name__)

@production_bp.route('/production', methods=['GET'])
def get_production_plans():
    """获取生产计划列表"""
    try:
        logger.debug('get_production_plans called with args: %s', dict(request.args))
        status = request.args.get('status')

        plans = ProductionPlan.get_all(status=status if status else None)
        return jsonify(plans)
    except Exception as e:
        logger.exception('Error in get_production_plans: %s', e)
        return jsonify({'error': str(e)}), 500

@production_bp.route('/production', methods=['POST'])
def create_production_plan():
    """创建生产计划"""
    try:
        logger.debug('create_production_plan called')
        data = request.get_json()

        required_fields = ['product_id', 'quantity', 'scheduled_date']
        for field in required_fields:
            if not data.get(field):
                logger.warning('Missing required field for production plan: %s', field)
                return jsonify({'error': f'{field}不能为空'}), 400

        plan = ProductionPlan.create(
            product_id=data['product_id'],
            quantity=data['quantity'],
            scheduled_date=data['scheduled_date'],
            notes=data.get('notes')
        )

        return jsonify(plan), 201
    except Exception as e:
        logger.exception('Error in create_production_plan: %s', e)
        return jsonify({'error': str(e)}), 500

@production_bp.route('/production/<int:plan_id>', methods=['DELETE'])
def delete_production_plan(plan_id):
    """删除生产计划"""
    try:
        logger.debug('delete_production_plan called with id: %s', plan_id)
        result = ProductionPlan.delete(plan_id)
        return jsonify({'message': '生产计划删除成功', 'deleted_count': result})
    except ValueError as e:
        logger.warning('ValueError in delete_production_plan: %s', e)
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.exception('Error in delete_production_plan: %s', e)
        return jsonify({'error': str(e)}), 500

@production_bp.route('/production/<int:plan_id>', methods=['PUT'])
def update_production_plan(plan_id):
    """更新生产计划"""
    try:
        logger.debug('update_production_plan called with id: %s', plan_id)
        data = request.get_json()

        # 更新生产计划
        plan = ProductionPlan.update(
            plan_id=plan_id,
            product_id=data.get('product_id'),
            quantity=data.get('quantity'),
            scheduled_date=data.get('scheduled_date'),
            status=data.get('status'),
            notes=data.get('notes'),
            produced_quantity=data.get('produced_quantity')
        )

        return jsonify(plan)
    except ValueError as e:
        logger.warning('ValueError in update_production_plan: %s', e)
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.exception('Error in update_production_plan: %s', e)
        return jsonify({'error': str(e)}), 500
