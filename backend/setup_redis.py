#!/usr/bin/env python3
"""
Redis Setup Script for AI Blog Assistant
- Reads configuration from .env
- Validates Redis availability
- Generates redis.conf matching your password
- Tests basic cache/session/ratelimit ops
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# ---------------------------
# Load .env
# ---------------------------
def load_dotenv_if_present():
    try:
        from dotenv import load_dotenv, find_dotenv
        env_path = find_dotenv(filename=".env", usecwd=True)
        if not env_path:
            here = Path(__file__).resolve().parent
            candidate = here / ".env"
            backend_candidate = here / "backend" / ".env"
            if candidate.exists():
                load_dotenv(dotenv_path=candidate)
            elif backend_candidate.exists():
                load_dotenv(dotenv_path=backend_candidate)
        else:
            load_dotenv(env_path)
    except Exception:
        pass

load_dotenv_if_present()

# ---------------------------
# Resolve Redis config
# ---------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB   = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_URL  = os.getenv("REDIS_URL", f"redis://{':' + REDIS_PASSWORD + '@' if REDIS_PASSWORD else ''}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

def check_redis_installed():
    try:
        r = subprocess.run(["redis-server", "--version"], capture_output=True, text=True)
        if r.returncode == 0:
            print(f"✅ Redis found: {r.stdout.strip()}")
            return True
        print("❌ Redis not found in PATH")
        return False
    except FileNotFoundError:
        print("❌ Redis not installed or not in PATH")
        return False

def check_redis_running():
    try:
        r = subprocess.run(["redis-cli", "-h", REDIS_HOST, "-p", str(REDIS_PORT), "PING"], capture_output=True, text=True)
        ok = (r.returncode == 0 and "PONG" in r.stdout.upper())
        print("✅ Redis server is running" if ok else "❌ Redis server not responding")
        return ok
    except FileNotFoundError:
        print("❌ redis-cli not available")
        return False

def start_redis_server():
    """
    Attempt to start Redis. On Windows, redis-server must be installed.
    On macOS/Linux with redis installed, we can start a daemonized server.
    """
    try:
        print("🔄 Attempting to start Redis server...")
        if os.name == "nt":
            # Windows: start in a new console if available
            subprocess.Popen(["redis-server"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["redis-server", "--daemonize", "yes"])
        time.sleep(2)
        return check_redis_running()
    except Exception as e:
        print(f"❌ Could not start Redis automatically: {e}")
        return False

def create_redis_conf(path="redis.conf"):
    requirepass_line = f"requirepass {REDIS_PASSWORD}\n" if REDIS_PASSWORD else ""
    conf = f"""# Redis configuration for AI Blog Assistant
port {REDIS_PORT}
bind 127.0.0.1
protected-mode yes

# Memory
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Security
{requirepass_line}
loglevel notice
logfile ""

databases 16
timeout 300
tcp-keepalive 300

slowlog-log-slower-than 10000
slowlog-max-len 128
"""
    try:
        Path(path).write_text(conf, encoding="utf-8")
        print(f"✅ Wrote {path} (requirepass {'enabled' if REDIS_PASSWORD else 'disabled'})")
        return True
    except Exception as e:
        print(f"❌ Failed writing {path}: {e}")
        return False

def configure_and_test():
    try:
        import redis
    except ImportError:
        print("❌ redis-py not installed. Install with:  python -m pip install redis python-dotenv")
        return False

    # Connect with/without password
    def _client(pw):
        return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=pw, decode_responses=True)

    try:
        # Try with password if provided, else without
        client = _client(REDIS_PASSWORD if REDIS_PASSWORD else None)
        client.ping()
        print("✅ Connected to Redis")

        # Cache test
        client.set("ai_blog_assistant:test_cache", "hello", ex=30)
        assert client.get("ai_blog_assistant:test_cache") == "hello"
        print("✅ Cache set/get OK")

        # Session test
        client.hset("session:test", mapping={"user_id": "1", "username": "demo_user"})
        assert client.hgetall("session:test").get("username") == "demo_user"
        print("✅ Session hash OK")

        # Rate limit test
        pipe = client.pipeline()
        pipe.incr("rate:test_user")
        pipe.expire("rate:test_user", 60)
        count, _ = pipe.execute()
        assert count >= 1
        print("✅ Rate limit counter OK")

        # Cleanup
        client.delete("ai_blog_assistant:test_cache", "session:test", "rate:test_user")
        print("✅ Clean up OK")
        return True

    except redis.AuthenticationError:
        print("❌ Authentication failed. Ensure REDIS_PASSWORD matches server config.")
        return False
    except Exception as e:
        print(f"❌ Redis tests failed: {e}")
        return False

def main():
    print("🔴 AI Blog Assistant • Redis Setup")
    print("=" * 60)
    print(f"Host={REDIS_HOST} Port={REDIS_PORT} DB={REDIS_DB} Password={'SET' if REDIS_PASSWORD else 'NOT SET'}")
    print(f"URL: {REDIS_URL}")

    if not check_redis_installed():
        print("\n💡 Install Redis:")
        print("  Windows:   https://github.com/tporadowski/redis/releases  (community build)")
        print("  macOS:     brew install redis")
        print("  Ubuntu:    sudo apt-get install redis-server")
        print("  Docker:    docker run -d -p 6379:6379 redis:alpine")
        return False

    if not check_redis_running():
        print("\n🔄 Redis not running; attempting to start...")
        if not start_redis_server():
            print("\n💡 Start manually, e.g.:")
            print("  redis-server")
            print("  or  redis-server redis.conf")
            return False

    print("\n⚙️ Creating redis.conf based on .env...")
    create_redis_conf()

    print("\n🧪 Testing Redis functionality...")
    ok = configure_and_test()
    print("✅ Redis setup complete!" if ok else "⚠️ Redis setup completed with warnings")
    return ok

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
