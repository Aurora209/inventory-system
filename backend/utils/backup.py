import os
import shutil
import datetime
import logging
from config import config

logger = logging.getLogger(__name__)

def backup_database():
    """备份数据库文件"""
    try:
        if not os.path.exists(config.DATABASE_PATH):
            logger.info("数据库文件不存在，无需备份")
            return None
        
        # 创建备份目录
        backup_dir = os.path.join(config.DATA_DIR, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # 生成备份文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'inventory_backup_{timestamp}.db')
        
        # 复制数据库文件
        shutil.copy2(config.DATABASE_PATH, backup_file)
        logger.info("数据库备份完成: %s", backup_file)
        return backup_file
    
    except Exception as e:
        logger.error("数据库备份失败: %s", e)
        return None

def restore_database(backup_file):
    """恢复数据库文件"""
    try:
        if not os.path.exists(backup_file):
            logger.warning("备份文件不存在: %s", backup_file)
            return False
        
        # 确保数据目录存在
        config.ensure_data_dir()
        
        # 恢复数据库文件
        shutil.copy2(backup_file, config.DATABASE_PATH)
        logger.info("数据库恢复完成: %s", config.DATABASE_PATH)
        return True
    
    except Exception as e:
        logger.error("数据库恢复失败: %s", e)
        return False

def list_backups():
    """列出所有备份文件"""
    backup_dir = os.path.join(config.DATA_DIR, 'backups')
    if not os.path.exists(backup_dir):
        return []
    
    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith('inventory_backup_') and file.endswith('.db'):
            file_path = os.path.join(backup_dir, file)
            file_time = os.path.getmtime(file_path)
            backups.append({
                'filename': file,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'created_time': datetime.datetime.fromtimestamp(file_time)
            })
    
    # 按创建时间排序
    backups.sort(key=lambda x: x['created_time'], reverse=True)
    return backups

def cleanup_old_backups(keep_count=10):
    """清理旧的备份文件，只保留指定数量的最新备份"""
    backups = list_backups()
    if len(backups) <= keep_count:
        return
    
    # 删除旧的备份文件
    for backup in backups[keep_count:]:
        for backup in backups[keep_count:]:
            try:
                os.remove(backup['path'])
                logger.info("删除旧备份: %s", backup['filename'])
            except Exception as e:
                logger.error("删除备份文件失败 %s: %s", backup['filename'], e)