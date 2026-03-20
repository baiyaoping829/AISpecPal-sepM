import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Redis配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6380/0")

# 初始化Redis客户端
redis_client = redis.from_url(REDIS_URL)

class CacheManager:
    """缓存管理器"""
    
    @staticmethod
    def set(key, value, expire=3600):
        """设置缓存"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            redis_client.set(key, value, ex=expire)
            return True
        except Exception as e:
            print(f"Failed to set cache: {e}")
            return False
    
    @staticmethod
    def get(key):
        """获取缓存"""
        try:
            value = redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            print(f"Failed to get cache: {e}")
            return None
    
    @staticmethod
    def delete(key):
        """删除缓存"""
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Failed to delete cache: {e}")
            return False
    
    @staticmethod
    def delete_pattern(pattern):
        """删除匹配模式的缓存"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Failed to delete cache pattern: {e}")
            return False

# 缓存键前缀
CACHE_PREFIX = {
    "spec": "spec:",
    "spec_list": "specs:list",
    "version": "version:",
    "version_list": "versions:list:",
    "relation": "relation:",
    "relation_list": "relations:list:"
}
