from flask import Blueprint, request, jsonify
import logging
from utils.backup import backup_database, list_backups, cleanup_old_backups, restore_database
import os

logger = logging.getLogger(__name__)

database_bp = Blueprint('database', __name__)

@database_bp.route('/database/backup', methods=['POST'])
def create_backup():
    """创建数据库备份"""
    try:
        logger.debug('create_backup called')
        backup_file = backup_database()
        if backup_file:
            return jsonify({
                'message': '数据库备份创建成功',
                'backup_file': backup_file
            })
        else:
            return jsonify({'error': '数据库备份创建失败'}), 500
    except Exception as e:
        logger.exception('Error creating backup: %s', e)
        return jsonify({'error': str(e)}), 500

@database_bp.route('/database/backups', methods=['GET'])
def get_backups():
    """获取备份列表"""
    try:
        logger.debug('get_backups called')
        backups = list_backups()
        return jsonify({'backups': backups})
    except Exception as e:
        logger.exception('Error listing backups: %s', e)
        return jsonify({'error': str(e)}), 500

@database_bp.route('/database/restore', methods=['POST'])
def restore_backup():
    """恢复数据库备份"""
    try:
        logger.debug('restore_backup called')
        data = request.get_json()
        backup_file = data.get('backup_file')
        
        if not backup_file:
            return jsonify({'error': '备份文件路径不能为空'}), 400
        
        if not os.path.exists(backup_file):
            return jsonify({'error': '备份文件不存在'}), 400
        
        if restore_database(backup_file):
            return jsonify({'message': '数据库恢复成功'})
        else:
            logger.error('restore_database returned False for file: %s', backup_file)
            return jsonify({'error': '数据库恢复失败'}), 500
    except Exception as e:
        logger.exception('Error restoring backup: %s', e)
        return jsonify({'error': str(e)}), 500

@database_bp.route('/database/cleanup', methods=['POST'])
def cleanup_backups():
    """清理旧备份"""
    try:
        logger.debug('cleanup_backups called')
        data = request.get_json()
        keep_count = data.get('keep_count', 10)

        cleanup_old_backups(keep_count)
        return jsonify({'message': f'备份清理完成，保留最近 {keep_count} 个备份'})
    except Exception as e:
        logger.exception('Error cleaning backups: %s', e)
        return jsonify({'error': str(e)}), 500