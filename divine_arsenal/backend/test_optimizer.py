#!/usr/bin/env python3
"""Test script for build optimizer."""

try:
    from divine_arsenal.backend.database import Database
    from divine_arsenal.backend.working_build_optimizer import WorkingBuildOptimizer

    print("✅ Imports successful")

    # Test database connection
    db = Database()
    print("✅ Database connection successful")

    # Test optimizer creation
    optimizer = WorkingBuildOptimizer(db)
    print("✅ Optimizer creation successful")

    # Test multiple scenarios
    test_cases = [
        ("Zeus", "Mid", 15000),
        ("Apollo", "Carry", 15000),
        ("Achilles", "Solo", 15000),
        ("Athena", "Support", 15000),
        ("Thor", "Jungle", 15000),
    ]

    for god, role, budget in test_cases:
        print(f"\n🔧 Testing {god} ({role}) with budget {budget}")
        print("-" * 50)

        result = optimizer.optimize_build(god, role, budget=budget)

        if result and "error" not in result:
            items = result.get("items", [])
            analysis = result.get("analysis")

            print(f"✅ Build generated successfully")
            print(
                f"📦 Items ({len(items)}): {[item.get('item_name', 'Unknown') for item in items]}"
            )

            if analysis:
                print(f"💪 Strengths: {analysis.strengths}")
                print(f"⚠️  Weaknesses: {analysis.weaknesses}")
                print(f"📊 Recommendation: {analysis.recommendation}")
                print(f"💰 Total Cost: {analysis.total_cost}")
                print(f"⚔️ Damage Potential: {analysis.damage_potential:.2f}")
                print(f"🛡️ Survivability: {analysis.survivability:.2f}")
                print(f"🔧 Utility Score: {analysis.utility_score:.2f}")
                print(f"📈 Synergy Score: {analysis.synergy_score:.2f}")
                print(f"🎯 Meta Rating: {analysis.meta_rating:.2f}")
            else:
                print("⚠️ No analysis available")
        else:
            print(f"❌ Build generation failed: {result}")

    print("\n🎉 All tests completed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
