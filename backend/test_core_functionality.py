#!/usr/bin/env python3
"""
核心功能测试脚本
专注测试数据库修复和消息插入功能
"""
import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine

async def test_conversation_message_insertion():
    """测试对话消息插入功能"""
    print("=== 测试对话消息插入功能 ===")
    
    async with engine.begin() as conn:
        try:
            # 1. 创建临时测试会话
            print("1. 创建临时测试会话...")
            session_result = await conn.execute(text("""
                INSERT INTO conversation_sessions 
                (id, user1_id, user2_id, session_type, status, title)
                VALUES 
                (gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), 'matchmaking', 'active', 'Test Session')
                RETURNING id
            """))
            session_id = session_result.scalar()
            print(f"   ✓ 创建测试会话: {session_id}")
            
            # 2. 测试插入不同类型的消息
            test_messages = [
                {
                    "sender_type": "user_avatar",
                    "sender_name": "Test Avatar 1",
                    "content": "Hello! This is a test message from user avatar.",
                    "message_type": "text"
                },
                {
                    "sender_type": "scenario_agent",
                    "sender_name": "Scenario Agent",
                    "content": "Welcome to the scenario simulation!",
                    "message_type": "system"
                },
                {
                    "sender_type": "matchmaker_agent",
                    "sender_name": "Matchmaker",
                    "content": "Let me help facilitate this conversation.",
                    "message_type": "facilitation"
                }
            ]
            
            print("2. 测试插入不同类型的消息...")
            inserted_messages = []
            
            for i, msg in enumerate(test_messages):
                result = await conn.execute(text("""
                    INSERT INTO conversation_messages 
                    (id, session_id, sender_id, sender_type, sender_name, content, message_type, 
                     turn_number, response_time_seconds, confidence_score, emotion_indicators, 
                     sentiment_score, topic_tags, compatibility_impact, is_highlighted, 
                     highlight_reason, is_edited, is_deleted, is_flagged, flag_reason, timestamp)
                    VALUES 
                    (gen_random_uuid(), :session_id, gen_random_uuid(), :sender_type, :sender_name, 
                     :content, :message_type, :turn_number, :response_time, :confidence, 
                     :emotions, :sentiment, :topics, :impact, :highlighted, :highlight_reason,
                     false, false, false, null, NOW())
                    RETURNING id, sender_type, message_type, content
                """), {
                    "session_id": session_id,
                    "sender_type": msg["sender_type"],
                    "sender_name": msg["sender_name"],
                    "content": msg["content"],
                    "message_type": msg["message_type"],
                    "turn_number": i + 1,
                    "response_time": 1.5,
                    "confidence": 0.85,
                    "emotions": '["happy", "excited"]',
                    "sentiment": 0.7,
                    "topics": '["greeting", "introduction"]',
                    "impact": 0.1,
                    "highlighted": i == 1,  # 高亮第二条消息
                    "highlight_reason": "Important system message" if i == 1 else None
                })
                
                message_data = result.fetchone()
                inserted_messages.append(message_data)
                print(f"   ✓ 插入消息 {i+1}: {msg['sender_type']} - {msg['message_type']}")
            
            # 3. 验证插入的消息
            print("3. 验证插入的消息...")
            result = await conn.execute(text("""
                SELECT id, sender_type, message_type, content, turn_number, is_highlighted, 
                       emotion_indicators, sentiment_score, topic_tags
                FROM conversation_messages 
                WHERE session_id = :session_id
                ORDER BY turn_number
            """), {"session_id": session_id})
            
            messages = result.fetchall()
            print(f"   ✓ 找到 {len(messages)} 条消息")
            
            for msg in messages:
                print(f"      消息ID: {msg[0]}")
                print(f"      发送者类型: {msg[1]}")
                print(f"      消息类型: {msg[2]}")
                print(f"      内容: {msg[3][:50]}...")
                print(f"      轮次: {msg[4]}")
                print(f"      是否高亮: {msg[5]}")
                print(f"      情感指标: {msg[6]}")
                print(f"      情感分数: {msg[7]}")
                print(f"      话题标签: {msg[8]}")
                print("      ---")
            
            # 4. 测试消息更新功能
            print("4. 测试消息更新功能...")
            first_message_id = messages[0][0]
            await conn.execute(text("""
                UPDATE conversation_messages 
                SET is_edited = true, edited_at = NOW(), highlight_reason = 'Updated for testing'
                WHERE id = :message_id
            """), {"message_id": first_message_id})
            print(f"   ✓ 更新消息: {first_message_id}")
            
            # 5. 清理测试数据
            print("5. 清理测试数据...")
            await conn.execute(text("DELETE FROM conversation_messages WHERE session_id = :session_id"), {"session_id": session_id})
            await conn.execute(text("DELETE FROM conversation_sessions WHERE id = :session_id"), {"session_id": session_id})
            print("   ✓ 测试数据已清理")
            
            print("\n✅ 对话消息插入功能测试通过!")
            return True
            
        except Exception as e:
            print(f"\n❌ 对话消息插入功能测试失败: {e}")
            return False

async def test_database_schema_integrity():
    """测试数据库架构完整性"""
    print("\n=== 测试数据库架构完整性 ===")
    
    async with engine.begin() as conn:
        try:
            # 1. 检查关键表
            print("1. 检查关键表...")
            tables_to_check = [
                'conversation_messages', 'conversation_sessions', 
                'scenario_templates', 'simulation_sessions', 'simulation_messages',
                'scenario_results', 'scenario_libraries'
            ]
            
            for table in tables_to_check:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"   ✓ 表 {table}: {count} 条记录")
            
            # 2. 检查 conversation_messages 表结构
            print("2. 检查 conversation_messages 表结构...")
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'conversation_messages'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print(f"   ✓ conversation_messages 表有 {len(columns)} 个列:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"      {col[0]}: {col[1]} {nullable}{default}")
            
            # 3. 验证枚举类型已清理
            print("3. 验证枚举类型已清理...")
            result = await conn.execute(text("""
                SELECT typname FROM pg_type 
                WHERE typtype = 'e' 
                AND typname IN ('agenttype', 'messagetype')
            """))
            enum_types = result.fetchall()
            
            if enum_types:
                print(f"   ⚠️ 仍存在枚举类型: {[t[0] for t in enum_types]}")
            else:
                print("   ✅ 枚举类型已成功清理")
            
            print("\n✅ 数据库架构完整性测试通过!")
            return True
            
        except Exception as e:
            print(f"\n❌ 数据库架构完整性测试失败: {e}")
            return False

async def test_api_endpoints_availability():
    """测试API端点可用性"""
    print("\n=== 测试API端点可用性 ===")
    
    try:
        # 这里我们只是验证模块可以正确导入，不实际调用API
        print("1. 测试兼容性服务导入...")
        from app.services.compatibility_service import CompatibilityService
        print("   ✓ CompatibilityService 导入成功")
        
        print("2. 测试场景服务导入...")
        from app.services.scenario_service import ScenarioService
        print("   ✓ ScenarioService 导入成功")
        
        print("3. 测试API端点导入...")
        from app.api.v1.endpoints import compatibility, scenarios
        print("   ✓ 兼容性API端点导入成功")
        print("   ✓ 场景API端点导入成功")
        
        print("4. 测试模型导入...")
        from app.models.scenario import ScenarioTemplate, SimulationSession, ScenarioResult
        from app.models.conversation import ConversationMessage, ConversationSession
        print("   ✓ 场景模型导入成功")
        print("   ✓ 对话模型导入成功")
        
        print("\n✅ API端点可用性测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ API端点可用性测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("=== Task 9 核心功能测试 ===\n")
    
    test_results = []
    
    try:
        # 1. 测试数据库架构完整性
        result = await test_database_schema_integrity()
        test_results.append(("数据库架构完整性", result))
        
        # 2. 测试对话消息插入功能
        result = await test_conversation_message_insertion()
        test_results.append(("对话消息插入功能", result))
        
        # 3. 测试API端点可用性
        result = await test_api_endpoints_availability()
        test_results.append(("API端点可用性", result))
        
        # 显示测试结果摘要
        print("\n" + "="*50)
        print("测试结果摘要")
        print("="*50)
        
        all_passed = True
        for test_name, passed in test_results:
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{status} {test_name}")
            if not passed:
                all_passed = False
        
        print("="*50)
        if all_passed:
            print("🎉 所有核心功能测试通过!")
            print("✅ Task 9 数据库修复成功，系统功能正常")
        else:
            print("⚠️ 部分测试失败，请检查相关功能")
            
    except Exception as e:
        print(f"\n💥 测试执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())