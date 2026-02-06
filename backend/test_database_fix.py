#!/usr/bin/env python3
"""
数据库修复和测试脚本
修复 conversation_messages 表中的列类型不匹配问题
"""
import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine

async def fix_column_types():
    """修复列类型不匹配问题"""
    print("开始修复数据库列类型...")
    
    async with engine.begin() as conn:
        try:
            # 1. 检查当前列类型
            print("\n1. 检查当前列类型:")
            result = await conn.execute(text("""
                SELECT column_name, data_type, udt_name 
                FROM information_schema.columns 
                WHERE table_name = 'conversation_messages' 
                AND column_name IN ('sender_type', 'message_type')
                ORDER BY column_name
            """))
            columns = result.fetchall()
            for col in columns:
                print(f"   {col[0]}: {col[1]} ({col[2]})")
            
            # 2. 修改 sender_type 列类型为 VARCHAR
            print("\n2. 修改 sender_type 列类型为 VARCHAR...")
            await conn.execute(text("ALTER TABLE conversation_messages ALTER COLUMN sender_type TYPE VARCHAR(50)"))
            print("   ✓ sender_type 列类型已修改为 VARCHAR(50)")
            
            # 3. 修改 message_type 列类型为 VARCHAR  
            print("\n3. 修改 message_type 列类型为 VARCHAR...")
            await conn.execute(text("ALTER TABLE conversation_messages ALTER COLUMN message_type TYPE VARCHAR(50)"))
            print("   ✓ message_type 列类型已修改为 VARCHAR(50)")
            
            # 4. 验证修改结果
            print("\n4. 验证修改结果:")
            result = await conn.execute(text("""
                SELECT column_name, data_type, udt_name 
                FROM information_schema.columns 
                WHERE table_name = 'conversation_messages' 
                AND column_name IN ('sender_type', 'message_type')
                ORDER BY column_name
            """))
            columns = result.fetchall()
            for col in columns:
                print(f"   {col[0]}: {col[1]} ({col[2]})")
            
            print("\n✅ 数据库列类型修复完成!")
            
        except Exception as e:
            print(f"❌ 修复过程中出现错误: {e}")
            raise

async def test_message_insertion():
    """测试消息插入功能"""
    print("\n开始测试消息插入...")
    
    async with engine.begin() as conn:
        try:
            # 测试插入一条消息
            test_message_sql = text("""
                INSERT INTO conversation_messages 
                (id, session_id, sender_id, sender_type, sender_name, content, message_type, timestamp)
                VALUES 
                (gen_random_uuid(), gen_random_uuid(), 'test-user-id', 'user_avatar', 'Test User', 'Hello, this is a test message!', 'text', NOW())
                RETURNING id, sender_type, message_type
            """)
            
            result = await conn.execute(test_message_sql)
            row = result.fetchone()
            
            if row:
                print(f"✅ 测试消息插入成功!")
                print(f"   消息ID: {row[0]}")
                print(f"   发送者类型: {row[1]}")
                print(f"   消息类型: {row[2]}")
                
                # 清理测试数据
                await conn.execute(text(f"DELETE FROM conversation_messages WHERE id = '{row[0]}'"))
                print("   ✓ 测试数据已清理")
            else:
                print("❌ 测试消息插入失败 - 没有返回结果")
                
        except Exception as e:
            print(f"❌ 测试消息插入失败: {e}")
            raise

async def check_enum_types():
    """检查并清理不需要的枚举类型"""
    print("\n检查数据库中的枚举类型...")
    
    async with engine.begin() as conn:
        try:
            # 查看所有自定义类型
            result = await conn.execute(text("""
                SELECT typname, typtype 
                FROM pg_type 
                WHERE typtype = 'e' 
                AND typname IN ('agenttype', 'messagetype')
                ORDER BY typname
            """))
            types = result.fetchall()
            
            print("找到的枚举类型:")
            for type_info in types:
                print(f"   {type_info[0]} ({type_info[1]})")
            
            # 检查是否还有其他表在使用这些枚举类型
            for type_name in ['agenttype', 'messagetype']:
                result = await conn.execute(text(f"""
                    SELECT table_name, column_name 
                    FROM information_schema.columns 
                    WHERE udt_name = '{type_name}'
                """))
                usage = result.fetchall()
                
                if usage:
                    print(f"\n枚举类型 {type_name} 仍在使用中:")
                    for table, column in usage:
                        print(f"   {table}.{column}")
                else:
                    print(f"\n枚举类型 {type_name} 未被使用，可以安全删除")
                    try:
                        await conn.execute(text(f"DROP TYPE IF EXISTS {type_name}"))
                        print(f"   ✓ 已删除枚举类型 {type_name}")
                    except Exception as e:
                        print(f"   ⚠️ 删除枚举类型 {type_name} 失败: {e}")
                        
        except Exception as e:
            print(f"❌ 检查枚举类型时出错: {e}")

async def main():
    """主函数"""
    print("=== 数据库修复和测试脚本 ===")
    
    try:
        # 1. 修复列类型
        await fix_column_types()
        
        # 2. 测试消息插入
        await test_message_insertion()
        
        # 3. 检查和清理枚举类型
        await check_enum_types()
        
        print("\n🎉 所有操作完成!")
        
    except Exception as e:
        print(f"\n💥 脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())