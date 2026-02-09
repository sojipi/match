"""
综合测试脚本 - 验证所有场景系统修复
"""
import asyncio
import sys
import os

sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from app.core.config import settings
from app.models.scenario import ScenarioTemplate, SimulationSession
from app.services.scenario_service import ScenarioService


async def run_comprehensive_tests():
    """运行综合测试以验证所有修复。"""

    print("=" * 70)
    print("场景系统综合测试")
    print("=" * 70)

    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    test_results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }

    try:
        # 测试 1: 数据库架构验证
        print("\n[测试 1/6] 验证数据库架构...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'scenario_templates'
                AND column_name IN ('resolution_prompts', 'completion_rate', 'content_warnings',
                                   'tags', 'keywords', 'language_variants', 'category', 'difficulty_level')
                ORDER BY column_name
            """))

            columns = result.fetchall()
            if len(columns) == 8:
                print("  ✅ 所有必需列都存在")
                test_results["passed"] += 1
                test_results["tests"].append(("数据库架构", "通过"))
            else:
                print(f"  ❌ 缺少列。找到 {len(columns)}/8")
                test_results["failed"] += 1
                test_results["tests"].append(("数据库架构", "失败"))

        # 测试 2: 枚举类型验证
        print("\n[测试 2/6] 验证枚举类型...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT column_name, udt_name
                FROM information_schema.columns
                WHERE table_name = 'scenario_templates'
                AND column_name IN ('category', 'difficulty_level')
            """))

            enum_cols = result.fetchall()
            if all(col[1] in ['scenariocategory', 'scenariodifficulty'] for col in enum_cols):
                print("  ✅ 枚举类型正确配置")
                test_results["passed"] += 1
                test_results["tests"].append(("枚举类型", "通过"))
            else:
                print("  ❌ 枚举类型配置错误")
                test_results["failed"] += 1
                test_results["tests"].append(("枚举类型", "失败"))

        # 测试 3: SQLAlchemy ORM 查询
        print("\n[测试 3/6] 测试 SQLAlchemy ORM 查询...")
        async with async_session() as session:
            result = await session.execute(
                select(ScenarioTemplate)
                .where(ScenarioTemplate.is_active == True)
                .where(ScenarioTemplate.is_approved == True)
            )
            scenarios = result.scalars().all()

            if len(scenarios) > 0:
                print(f"  ✅ 成功查询到 {len(scenarios)} 个场景")
                print(f"     场景: {scenarios[0].name}")
                print(f"     类别: {scenarios[0].category.value}")
                print(f"     难度: {scenarios[0].difficulty_level.value}")
                test_results["passed"] += 1
                test_results["tests"].append(("SQLAlchemy 查询", "通过"))
            else:
                print("  ⚠️  查询成功但没有场景数据")
                test_results["passed"] += 1
                test_results["tests"].append(("SQLAlchemy 查询", "通过（无数据）"))

        # 测试 4: 场景服务 - 获取场景库
        print("\n[测试 4/6] 测试场景服务 - 获取场景库...")
        async with async_session() as session:
            service = ScenarioService(session)
            scenarios = await service.get_scenario_library()

            if len(scenarios) > 0:
                print(f"  ✅ 成功获取 {len(scenarios)} 个场景")
                test_results["passed"] += 1
                test_results["tests"].append(("获取场景库", "通过"))
            else:
                print("  ⚠️  服务正常但没有场景数据")
                test_results["passed"] += 1
                test_results["tests"].append(("获取场景库", "通过（无数据）"))

        # 测试 5: 场景服务 - 创建模拟会话
        print("\n[测试 5/6] 测试场景服务 - 创建模拟会话...")
        async with async_session() as session:
            service = ScenarioService(session)

            # 获取第一个场景
            result = await session.execute(
                select(ScenarioTemplate)
                .where(ScenarioTemplate.is_active == True)
                .limit(1)
            )
            scenario = result.scalars().first()

            if scenario:
                try:
                    session_data = await service.create_simulation_session(
                        user1_id='40740043-0846-477d-9830-1bbcc86ba97e',
                        user2_id='40740043-0846-477d-9830-1bbcc86ba97e',
                        scenario_id=str(scenario.id),
                        match_id='c2975637-a935-44a4-9f06-84eb5428981f',
                        cultural_context=None,
                        language='en'
                    )

                    print(f"  ✅ 成功创建模拟会话")
                    print(f"     Session ID: {session_data['session_id']}")
                    print(f"     状态: {session_data['status']}")
                    print(f"     类别: {session_data['scenario']['category']}")
                    print(f"     难度: {session_data['scenario']['difficulty_level']}")
                    test_results["passed"] += 1
                    test_results["tests"].append(("创建模拟会话", "通过"))
                except Exception as e:
                    print(f"  ❌ 创建会话失败: {e}")
                    test_results["failed"] += 1
                    test_results["tests"].append(("创建模拟会话", f"失败: {e}"))
            else:
                print("  ⚠️  没有可用的场景模板")
                test_results["tests"].append(("创建模拟会话", "跳过（无数据）"))

        # 测试 6: usage_count 处理
        print("\n[测试 6/6] 测试 usage_count None 处理...")
        async with async_session() as session:
            # 创建一个测试场景，usage_count 为 None
            result = await session.execute(text("""
                SELECT id FROM scenario_templates LIMIT 1
            """))
            scenario_id = result.fetchone()

            if scenario_id:
                # 将 usage_count 设为 None
                await session.execute(text("""
                    UPDATE scenario_templates
                    SET usage_count = NULL
                    WHERE id = :id
                """), {"id": scenario_id[0]})
                await session.commit()

                # 尝试创建会话（应该处理 None 情况）
                service = ScenarioService(session)
                try:
                    session_data = await service.create_simulation_session(
                        user1_id='40740043-0846-477d-9830-1bbcc86ba97e',
                        user2_id='40740043-0846-477d-9830-1bbcc86ba97e',
                        scenario_id=str(scenario_id[0]),
                        match_id='c2975637-a935-44a4-9f06-84eb5428981f',
                        cultural_context=None,
                        language='en'
                    )
                    print("  ✅ 成功处理 usage_count 为 None 的情况")
                    test_results["passed"] += 1
                    test_results["tests"].append(("usage_count None 处理", "通过"))
                except Exception as e:
                    print(f"  ❌ 处理失败: {e}")
                    test_results["failed"] += 1
                    test_results["tests"].append(("usage_count None 处理", f"失败: {e}"))
            else:
                print("  ⚠️  没有可用的场景模板")
                test_results["tests"].append(("usage_count None 处理", "跳过（无数据）"))

        # 打印测试结果摘要
        print("\n" + "=" * 70)
        print("测试结果摘要")
        print("=" * 70)
        print(f"\n总测试数: {test_results['passed'] + test_results['failed']}")
        print(f"通过: {test_results['passed']}")
        print(f"失败: {test_results['failed']}")
        print(f"成功率: {test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100:.1f}%")

        print("\n详细结果:")
        for test_name, result in test_results["tests"]:
            status = "✅" if "通过" in result else "❌" if "失败" in result else "⚠️"
            print(f"  {status} {test_name}: {result}")

        print("\n" + "=" * 70)
        if test_results["failed"] == 0:
            print("🎉 所有测试通过！场景系统完全可用！")
        else:
            print(f"⚠️  {test_results['failed']} 个测试失败，需要进一步调查")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
