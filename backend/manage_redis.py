"""
Redis management utility script.
Provides common Redis operations for development and maintenance.
"""
import asyncio
import sys
import json
from datetime import datetime
from app.models.redis_models import (
    redis_client,
    UserSession,
    UserOnlineStatus,
    LiveSessionData,
    MatchingQueue,
    CachedCompatibilityScore
)


def print_menu():
    """Print the main menu."""
    print("\n" + "=" * 80)
    print("REDIS MANAGEMENT UTILITY")
    print("=" * 80)
    print("\n1. Show all keys")
    print("2. Show key info")
    print("3. Delete key")
    print("4. Flush all data (WARNING: deletes everything)")
    print("5. Show Redis info")
    print("6. Show sessions")
    print("7. Show online users")
    print("8. Show matching queue")
    print("9. Show cached scores")
    print("10. Test Redis connection")
    print("11. Exit")
    print("\n" + "=" * 80)


def show_all_keys():
    """Show all keys in Redis."""
    print("\nAll Redis Keys:")
    print("-" * 80)

    keys = redis_client.keys("*")
    if not keys:
        print("No keys found")
        return

    # Group keys by prefix
    key_groups = {}
    for key in keys:
        prefix = key.split(":")[0] if ":" in key else "other"
        if prefix not in key_groups:
            key_groups[prefix] = []
        key_groups[prefix].append(key)

    for prefix, group_keys in sorted(key_groups.items()):
        print(f"\n{prefix.upper()} ({len(group_keys)} keys):")
        for key in sorted(group_keys)[:10]:  # Show first 10
            ttl = redis_client.ttl(key)
            ttl_str = f"{ttl}s" if ttl > 0 else "no expiry" if ttl == -1 else "expired"
            print(f"  - {key} (TTL: {ttl_str})")
        if len(group_keys) > 10:
            print(f"  ... and {len(group_keys) - 10} more")

    print("-" * 80)
    print(f"Total: {len(keys)} keys")


def show_key_info(key: str):
    """Show detailed information about a specific key."""
    print(f"\nKey: {key}")
    print("=" * 80)

    if not redis_client.exists(key):
        print("Key does not exist")
        return

    # Get key type
    key_type = redis_client.type(key)
    print(f"Type: {key_type}")

    # Get TTL
    ttl = redis_client.ttl(key)
    if ttl > 0:
        print(f"TTL: {ttl} seconds ({ttl // 60} minutes)")
    elif ttl == -1:
        print("TTL: No expiry")
    else:
        print("TTL: Expired")

    # Get value
    print("\nValue:")
    print("-" * 80)
    if key_type == "string":
        value = redis_client.get(key)
        try:
            # Try to parse as JSON
            parsed = json.loads(value)
            print(json.dumps(parsed, indent=2))
        except:
            print(value)
    elif key_type == "hash":
        value = redis_client.hgetall(key)
        for field, val in value.items():
            print(f"{field}: {val}")
    elif key_type == "list":
        value = redis_client.lrange(key, 0, -1)
        for i, item in enumerate(value):
            print(f"{i}: {item}")
    elif key_type == "set":
        value = redis_client.smembers(key)
        for item in value:
            print(f"- {item}")
    elif key_type == "zset":
        value = redis_client.zrange(key, 0, -1, withscores=True)
        for item, score in value:
            print(f"{item}: {score}")


def delete_key(key: str):
    """Delete a specific key."""
    if not redis_client.exists(key):
        print(f"Key '{key}' does not exist")
        return

    confirm = input(f"Are you sure you want to delete '{key}'? (yes/no): ")
    if confirm.lower() == 'yes':
        redis_client.delete(key)
        print(f"✓ Key '{key}' deleted successfully")
    else:
        print("Operation cancelled")


def flush_all():
    """Flush all data from Redis."""
    print("\nWARNING: This will delete ALL data from Redis!")
    confirm = input("Type 'DELETE ALL' to confirm: ")
    if confirm == 'DELETE ALL':
        redis_client.flushall()
        print("✓ All data flushed successfully")
    else:
        print("Operation cancelled")


def show_redis_info():
    """Show Redis server information."""
    print("\nRedis Server Information:")
    print("=" * 80)

    info = redis_client.info()

    # Server info
    print("\nServer:")
    print(f"  Version: {info.get('redis_version')}")
    print(f"  Mode: {info.get('redis_mode')}")
    print(f"  OS: {info.get('os')}")
    print(f"  Uptime: {info.get('uptime_in_seconds')} seconds ({info.get('uptime_in_days')} days)")

    # Memory info
    print("\nMemory:")
    print(f"  Used: {info.get('used_memory_human')}")
    print(f"  Peak: {info.get('used_memory_peak_human')}")
    print(f"  RSS: {info.get('used_memory_rss_human')}")

    # Stats
    print("\nStats:")
    print(f"  Total connections: {info.get('total_connections_received')}")
    print(f"  Total commands: {info.get('total_commands_processed')}")
    print(f"  Connected clients: {info.get('connected_clients')}")

    # Keyspace
    print("\nKeyspace:")
    for db_key, db_info in info.items():
        if db_key.startswith('db'):
            print(f"  {db_key}: {db_info}")


def show_sessions():
    """Show all active user sessions."""
    print("\nActive User Sessions:")
    print("-" * 80)

    session_keys = redis_client.keys("session:*")
    if not session_keys:
        print("No active sessions")
        return

    print(f"Found {len(session_keys)} active sessions\n")

    for key in session_keys[:20]:  # Show first 20
        session_token = key.split(":")[1]
        session = UserSession.get_session(session_token)
        if session:
            ttl = redis_client.ttl(key)
            print(f"Session: {session_token[:20]}...")
            print(f"  User ID: {session.user_id}")
            print(f"  Created: {session.created_at}")
            print(f"  Last Activity: {session.last_activity}")
            print(f"  IP: {session.ip_address}")
            print(f"  TTL: {ttl}s ({ttl // 60}m)")
            print()

    if len(session_keys) > 20:
        print(f"... and {len(session_keys) - 20} more sessions")


def show_online_users():
    """Show all online users."""
    print("\nOnline Users:")
    print("-" * 80)

    online_keys = redis_client.keys("online:*")
    if not online_keys:
        print("No users online")
        return

    print(f"Found {len(online_keys)} online users\n")

    for key in online_keys[:20]:  # Show first 20
        user_id = key.split(":")[1]
        status = UserOnlineStatus.get_online_status(user_id)
        if status:
            ttl = redis_client.ttl(key)
            print(f"User: {user_id}")
            print(f"  Status: {'Online' if status.is_online else 'Offline'}")
            print(f"  Activity: {status.current_activity}")
            print(f"  Device: {status.device_type}")
            print(f"  Last Seen: {status.last_seen}")
            print(f"  TTL: {ttl}s")
            print()

    if len(online_keys) > 20:
        print(f"... and {len(online_keys) - 20} more users")


def show_matching_queue():
    """Show users in the matching queue."""
    print("\nMatching Queue:")
    print("-" * 80)

    queue_keys = redis_client.keys("queue:*")
    if not queue_keys:
        print("Queue is empty")
        return

    print(f"Found {len(queue_keys)} users in queue\n")

    entries = []
    for key in queue_keys:
        user_id = key.split(":")[1]
        entry = MatchingQueue.get_queue_entry(user_id)
        if entry:
            entries.append(entry)

    # Sort by priority and join time
    entries.sort(key=lambda x: (x.queue_priority, x.joined_at), reverse=True)

    for entry in entries[:20]:  # Show first 20
        ttl = redis_client.ttl(f"queue:{entry.user_id}")
        print(f"User: {entry.user_id}")
        print(f"  Priority: {entry.queue_priority}")
        print(f"  Joined: {entry.joined_at}")
        print(f"  TTL: {ttl}s ({ttl // 60}m)")
        print()

    if len(entries) > 20:
        print(f"... and {len(entries) - 20} more users")


def show_cached_scores():
    """Show cached compatibility scores."""
    print("\nCached Compatibility Scores:")
    print("-" * 80)

    score_keys = redis_client.keys("compat:*")
    if not score_keys:
        print("No cached scores")
        return

    print(f"Found {len(score_keys)} cached scores\n")

    for key in score_keys[:20]:  # Show first 20
        parts = key.split(":")
        if len(parts) == 3:
            user1_id, user2_id = parts[1], parts[2]
            score = CachedCompatibilityScore.get_score(user1_id, user2_id)
            if score:
                ttl = redis_client.ttl(key)
                print(f"Users: {user1_id[:8]}... <-> {user2_id[:8]}...")
                print(f"  Score: {score.compatibility_score:.2f}")
                print(f"  Calculated: {score.calculated_at}")
                print(f"  TTL: {ttl}s ({ttl // 3600}h)")
                print()

    if len(score_keys) > 20:
        print(f"... and {len(score_keys) - 20} more scores")


def test_connection():
    """Test Redis connection."""
    print("\nTesting Redis Connection...")
    print("-" * 80)

    try:
        # Ping
        response = redis_client.ping()
        print(f"✓ Ping: {response}")

        # Set and get test
        test_key = "test:connection"
        test_value = f"test_{datetime.now().isoformat()}"
        redis_client.setex(test_key, 10, test_value)
        retrieved = redis_client.get(test_key)

        if retrieved == test_value:
            print(f"✓ Set/Get: OK")
        else:
            print(f"✗ Set/Get: Failed")

        # Clean up
        redis_client.delete(test_key)

        # Get info
        info = redis_client.info()
        print(f"✓ Server version: {info.get('redis_version')}")
        print(f"✓ Connected clients: {info.get('connected_clients')}")

        print("\n" + "=" * 80)
        print("Redis connection test passed!")

    except Exception as e:
        print(f"\n✗ Connection test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function."""
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-11): ").strip()

        try:
            if choice == '1':
                show_all_keys()
            elif choice == '2':
                key = input("Enter key name: ").strip()
                show_key_info(key)
            elif choice == '3':
                key = input("Enter key name to delete: ").strip()
                delete_key(key)
            elif choice == '4':
                flush_all()
            elif choice == '5':
                show_redis_info()
            elif choice == '6':
                show_sessions()
            elif choice == '7':
                show_online_users()
            elif choice == '8':
                show_matching_queue()
            elif choice == '9':
                show_cached_scores()
            elif choice == '10':
                test_connection()
            elif choice == '11':
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
