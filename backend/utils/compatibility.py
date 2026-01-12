"""兼容性修复工具"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def ensure_pandas_compatibility():
    """确保pandas版本兼容性"""
    pandas_version = pd.__version__
    logger.info("当前pandas版本: %s", pandas_version)
    
    # 检查版本并应用必要的修复
    major, minor, patch = map(int, pandas_version.split('.'))
    
    if major >= 2 and minor >= 3:
        logger.debug("使用pandas 2.3+兼容模式")
        # 这里可以添加针对pandas 2.3+的特定修复
    
    return True

# 数据导出兼容性包装器
class PandasExporter:
    """pandas数据导出兼容性包装器"""
    
    @staticmethod
    def to_excel_compatible(df, filepath, **kwargs):
        """兼容的Excel导出方法"""
        try:
            # 尝试使用默认参数
            df.to_excel(filepath, **kwargs)
            return True
        except Exception as e:
            logger.warning("Excel导出失败，尝试兼容模式: %s", e)
            try:
                # 回退到更简单的参数
                df.to_excel(filepath, index=False, engine='openpyxl')
                return True
            except Exception as e2:
                logger.error("Excel导出完全失败: %s", e2)
                return False
    
    @staticmethod
    def safe_dataframe_creation(data, columns=None):
        """安全创建DataFrame"""
        try:
            if columns:
                return pd.DataFrame(data, columns=columns)
            else:
                return pd.DataFrame(data)
        except Exception as e:
            logger.error("DataFrame创建失败: %s", e)
            # 回退到更安全的方式
            return pd.DataFrame()