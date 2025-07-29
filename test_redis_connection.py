#!/usr/bin/env python3
import redis
import sys

def test_redis_connection():
    """Test connection to cloud Redis"""
    redis_url = "redis://default:iXLuANnT0BwPCF1YsL7Qh7FWMA4dGeTb@redis-12404.c274.us-east-1-3.ec2.redns.redis-cloud.com:12404"
    
    try:
        # Create Redis client
        r = redis.from_url(redis_url)
        
        # Test connection
        r.ping()
        print("✅ Redis connection successful!")
        
        # Test basic operations
        r.set("test_key", "test_value")
        value = r.get("test_key")
        print(f"✅ Redis set/get test: {value.decode() if value else 'None'}")
        
        # Clean up
        r.delete("test_key")
        
        # Get Redis info
        info = r.info()
        print(f"✅ Redis version: {info.get('redis_version', 'Unknown')}")
        print(f"✅ Connected clients: {info.get('connected_clients', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_redis_connection()
    sys.exit(0 if success else 1)