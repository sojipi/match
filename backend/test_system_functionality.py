#!/usr/bin/env python3
"""
系统功能测试脚本
测试 Task 9 实现的关键功能
"""
import asyncio
import sys
import json
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine, get_db
from app.services.compatibility_service import CompatibilityService
from app.models.scenario import ScenarioTemplate, SimulationSession, ScenarioCategory, ScenarioDifficulty
from app.models.user import User, PersonalityProfile
from app.models.conversation import ConversationMessage, ConversationSession

async def create_test_data():
    """创建测试数据"""
    print("创建测试数据...")
    
    async with engine.begin() as conn:
        try:
            # 1. 创建测试用户 (使用UUID格式)
            user1_id = "11111111-1111-1111-1111-111111111111"
            user2_id = "22222222-2222-2222-2222-222222222222"
            
            # 检查用户是否已存在
            result = await conn.execute(text("SELECT id FROM users WHERE id = :user_id"), {"user_id": user1_id})
            if not result.fetchone():
                await conn.execute(text("""
                    INSERT INTO users (id, username, email, first_name, last_name, is_active, is_verified)
                    VALUES (:user_id, :username, :email, :first_name, :last_name, true, true)
                """), {
                    "user_id": user1_id,
                    "username": "testuser1",
                    "email": "test1@example.com",
                    "first_name": "Test",
                    "last_name": "User1"
                })
                print(f"   ✓ 创建测试用户1: {user1_id}")
            
            result = await conn.execute(text("SELECT id FROM users WHERE id = :user_id"), {"user_id": user2_id})
            if not result.fetchone():
                await conn.execute(text("""
                    INSERT INTO users (id, username, email, first_name, last_name, is_active, is_verified)
                    VALUES (:user_id, :username, :email, :first_name, :last_name, true, true)
                """), {
                    "user_id": user2_id,
                    "username": "testuser2",
                    "email": "test2@example.com",
                    "first_name": "Test",
                    "last_name": "User2"
                })
                print(f"   ✓ 创建测试用户2: {user2_id}")
            
            # 2. 创建测试场景模板
            scenario_result = await conn.execute(text("SELECT id FROM scenario_templates LIMIT 1"))
            if not scenario_result.fetchone():
                await conn.execute(text("""
                    INSERT INTO scenario_templates 
                    (id, name, category, difficulty_level, title, description, context, setup_prompt, 
                     estimated_duration_minutes, is_active, is_approved)
                    VALUES 
                    (gen_random_uuid(), 'test_scenario', 'communication', 2, 
                     'Test Communication Scenario', 
                     'A test scenario for communication skills',
                     'Testing context',
                     'This is a test scenario setup',
                     15, true, true)
                """))
                print("   ✓ 创建测试场景模板")
            
            # 3. 创建测试对话会话
            session_result = await conn.execute(text("SELECT id FROM conversation_sessions LIMIT 1"))
            if not session_result.fetchone():
                await conn.execute(text("""
                    INSERT INTO conversation_sessions 
                    (id, user1_id, user2_id, session_type, status, title)
                    VALUES 
                    (gen_random_uuid(), :user1_id, :user2_id, 'matchmaking', 'active', 'Test Session')
                """), {"user1_id": user1_id, "user2_id": user2_id})
                print("   ✓ 创建测试对话会话")
            
            return user1_id, user2_id
            
        except Exception as e:
            print(f"❌ 创建测试数据失败: {e}")
            raise

async def test_conversation_message_insertion():
    """测试对话消息插入"""
    print("\n测试对话消息插入...")
    
    async with engine.begin() as conn:
        try:
            # 获取一个测试会话ID
            result = await conn.execute(text("SELECT id FROM conversation_sessions LIMIT 1"))
            session = result.fetchone()
            if not session:
                print("❌ 没有找到测试会话")
                return False
            
            session_id = session[0]
            
            # 插入测试消息
            await conn.execute(text("""
                INSERT INTO conversation_messages 
                (id, session_id, sender_id, sender_type, sender_name, content, message_type, timestamp)
                VALUES 
                (gen_random_uuid(), :session_id, '11111111-1111-1111-1111-111111111111', 'user_avatar', 'Test Avatar', 
                 'Hello! This is a test message from the avatar.', 'text', NOW())
            """), {"session_id": session_id})
            
            # 验证插入
            result = await conn.execute(text("""
                SELECT sender_type, message_type, content 
                FROM conversation_messages 
                WHERE session_id = :session_id
                ORDER BY timestamp DESC 
                LIMIT 1
            """), {"session_id": session_id})
            
            message = result.fetchone()
            if message:
                print(f"   ✅ 消息插入成功!")
                print(f"      发送者类型: {message[0]}")
                print(f"      消息类型: {message[1]}")
                print(f"      内容: {message[2][:50]}...")
                return True
            else:
                print("❌ 消息插入失败 - 无法找到插入的消息")
                return False
                
        except Exception as e:
            print(f"❌ 测试对话消息插入失败: {e}")
            return False

async def test_compatibility_service():
    """测试兼容性分析服务"""
    print("\n测试兼容性分析服务...")
    
    try:
        # 创建数据库会话
        async with AsyncSession(engine) as db:
            compatibility_service = CompatibilityService(db)
            
            # 获取测试用户
            user1_id = "11111111-1111-1111-1111-111111111111"
            user2_id = "22222222-2222-2222-2222-222222222222"
            
            # 测试获取用户资料
            users = await compatibility_service._get_user_profiles(user1_id, user2_id)
            if users:
                print("   ✅ 成功获取用户资料")
                user1, user2 = users
                print(f"      用户1: {user1.first_name} {user1.last_name}")
                print(f"      用户2: {user2.first_name} {user2.last_name}")
            else:
                print("   ⚠️ 无法获取用户资料")
                return False
            
            # 测试获取模拟历史
            simulation_history = await compatibility_service._get_simulation_history(user1_id, user2_id)
            print(f"   ✅ 获取模拟历史: {len(simulation_history)} 个会话")
            
            # 测试计算兼容性分数
            scores = await compatibility_service._calculate_compatibility_scores(user1, user2, simulation_history)
            print("   ✅ 计算兼容性分数:")
            for dimension, score in scores.items():
                print(f"      {dimension}: {score:.2f}")
            
            return True
            
    except Exception as e:
        print(f"❌ 测试兼容性分析服务失败: {e}")
        return False

async def test_scenario_data():
    """测试场景数据"""
    print("\n测试场景数据...")
    
    async with engine.begin() as conn:
        try:
            # 检查场景模板
            result = await conn.execute(text("SELECT COUNT(*) FROM scenario_templates"))
            count = result.scalar()
            print(f"   ✅ 场景模板数量: {count}")
            
            if count > 0:
                # 获取一个场景模板的详细信息
                result = await conn.execute(text("""
                    SELECT name, category, difficulty_level, title, description 
                    FROM scenario_templates 
                    LIMIT 1
                """))
                scenario = result.fetchone()
                if scenario:
                    print("   ✅ 场景模板示例:")
                    print(f"      名称: {scenario[0]}")
                    print(f"      类别: {scenario[1]}")
                    print(f"      难度: {scenario[2]}")
                    print(f"      标题: {scenario[3]}")
                    print(f"      描述: {scenario[4][:100]}...")
            
            # 检查模拟会话
            result = await conn.execute(text("SELECT COUNT(*) FROM simulation_sessions"))
            count = result.scalar()
            print(f"   ✅ 模拟会话数量: {count}")
            
            # 检查场景结果
            result = await conn.execute(text("SELECT COUNT(*) FROM scenario_results"))
            count = result.scalar()
            print(f"   ✅ 场景结果数量: {count}")
            
            return True
            
        except Exception as e:
            print(f"❌ 测试场景数据失败: {e}")
            return False

async def test_database_schema():
    """测试数据库架构"""
    print("\n测试数据库架构...")
    
    async with engine.begin() as conn:
        try:
            # 检查关键表是否存在
            required_tables = [
                'users', 'conversation_sessions', 'conversation_messages',
                'scenario_templates', 'simulation_sessions', 'simulation_messages',
                'scenario_results', 'scenario_libraries'
            ]
            
            for table in required_tables:
                result = await conn.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = '{table}'
                """))
                exists = result.scalar() > 0
                status = "✅" if exists else "❌"
                print(f"   {status} 表 {table}: {'存在' if exists else '不存在'}")
                
                if not exists:
                    return False
            
            # 检查 conversation_messages 表的关键列
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'conversation_messages'
                AND column_name IN ('sender_type', 'message_type', 'turn_number')
                ORDER BY column_name
            """))
            columns = result.fetchall()
            
            print("   ✅ conversation_messages 关键列:")
            for col in columns:
                print(f"      {col[0]}: {col[1]}")
            
            return True
            
        except Exception as e:
            print(f"❌ 测试数据库架构失败: {e}")
            return False

async def cleanup_test_data():
    """清理测试数据"""
    print("\n清理测试数据...")
    
    async with engine.begin() as conn:
        try:
            # 删除测试消息
            await conn.execute(text("DELETE FROM conversation_messages WHERE sender_id IN ('11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222')"))
            
            # 删除测试会话
            await conn.execute(text("DELETE FROM conversation_sessions WHERE user1_id IN ('11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222') OR user2_id IN ('11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222')"))
            
            # 删除测试用户
            await conn.execute(text("DELETE FROM users WHERE id IN ('11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222')"))
            
            print("   ✅ 测试数据清理完成")
            
        except Exception as e:
            print(f"❌ 清理测试数据失败: {e}")

async def main():
    """主测试函数"""
    print("=== Task 9 系统功能测试 ===")
    
    test_results = []
    
    try:
        # 1. 测试数据库架构
        result = await test_database_schema()
        test_results.append(("数据库架构", result))
        
        # 2. 创建测试数据
        user1_id, user2_id = await create_test_data()
        
        # 3. 测试对话消息插入
        result = await test_conversation_message_insertion()
        test_results.append(("对话消息插入", result))
        
        # 4. 测试兼容性分析服务
        result = await test_compatibility_service()
        test_results.append(("兼容性分析服务", result))
        
        # 5. 测试场景数据
        result = await test_scenario_data()
        test_results.append(("场景数据", result))
        
        # 6. 清理测试数据
        await cleanup_test_data()
        
        # 显示测试结果摘要
        print("\n=== 测试结果摘要 ===")
        all_passed = True
        for test_name, passed in test_results:
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{status} {test_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 所有测试通过! Task 9 系统功能正常")
        else:
            print("\n⚠️ 部分测试失败，请检查相关功能")
            
    except Exception as e:
        print(f"\n💥 测试执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())