# 🧪 SMITE 2 Divine Arsenal - Manual Test Guide

## 🚀 Quick Start Testing

### **Option 1: Automated Testing (Recommended)**
```powershell
# Run the comprehensive test suite
./run_tests.ps1
```

### **Option 2: Manual Testing**

#### **Step 1: Start the Server**
```powershell
# With SQLite (local)
cd divine_arsenal/backend
python app_with_migrations.py

# With PostgreSQL (production)
$env:DATABASE_URL = 'postgresql://divine_arsenal_db_user:PHc5f6cz2mPKBlfhZhe6mRgvxDNsRkmH@dpg-d1op9jbipnbc73fa7gg0-a.oregon-postgres.render.com/divine_arsenal_db'
cd divine_arsenal/backend
python app_with_migrations.py
```

#### **Step 2: Test Core Endpoints**

##### **Health Check**
```bash
curl http://localhost:5000/health
```
**Expected**: `{"status": "healthy", "database": "connected"}`

##### **Database Integrity**
```bash
# Test gods
curl http://localhost:5000/api/gods
# Expected: {"gods": [...], "count": 62}

# Test items
curl http://localhost:5000/api/items
# Expected: {"items": [...], "count": 150}
```

##### **Basic Build Optimization**
```bash
curl -X POST http://localhost:5000/api/optimize-build \
  -H "Content-Type: application/json" \
  -d '{"god": "Zeus", "role": "Mid", "budget": 15000}'
```

**Expected Response Format**:
```json
{
  "success": true,
  "build": {
    "god": "Zeus",
    "role": "Mid",
    "score": 85,
    "items": [
      {"item_name": "Book of Thoth", "category": "Magical", "cost": 2500},
      {"item_name": "Rod of Tahuti", "category": "Magical", "cost": 3000},
      // ... more items
    ],
    "total_cost": 15000,
    "explanation": "Optimized Mid build for Zeus..."
  }
}
```

##### **Enhanced Build Optimization**
```bash
curl -X POST http://localhost:5000/api/optimize-build/enhanced \
  -H "Content-Type: application/json" \
  -d '{"god": "Zeus", "role": "Mid", "mode": "Conquest", "player_name": "TestPlayer"}'
```

##### **Build Explanation**
```bash
curl -X POST http://localhost:5000/api/explain-build \
  -H "Content-Type: application/json" \
  -d '{"god": "Zeus", "role": "Mid", "budget": 15000}'
```

## 🎯 **Test Scenarios**

### **Scenario 1: Different Gods & Roles**
Test various combinations:
- **Zeus (Mid)**: Expect magical power items
- **Loki (Jungle)**: Expect physical power + penetration items
- **Athena (Support)**: Expect protection + utility items
- **Neith (Carry)**: Expect physical power + attack speed items

### **Scenario 2: Different Game Modes**
- **Conquest**: Balanced builds
- **Arena**: More sustain-focused
- **Joust**: Burst damage focus
- **Assault**: Heavy sustain builds

### **Scenario 3: Error Handling**
```bash
# Invalid god
curl -X POST http://localhost:5000/api/optimize-build \
  -H "Content-Type: application/json" \
  -d '{"god": "InvalidGod", "role": "Mid"}'
# Expected: {"error": "God 'InvalidGod' not found"}

# Missing required fields
curl -X POST http://localhost:5000/api/optimize-build \
  -H "Content-Type: application/json" \
  -d '{"role": "Mid"}'
# Expected: {"error": "God is required"}
```

## 📊 **Success Criteria**

### **Critical Tests (Must Pass)**
- ✅ Health check returns 200 OK
- ✅ Database contains 60+ gods and 150+ items
- ✅ Basic build optimization generates 4-6 items
- ✅ Build scores are > 0 and < 100
- ✅ Item costs are reasonable (500-4000 gold each)

### **Advanced Tests (Should Pass)**
- ✅ Enhanced optimization works
- ✅ Build explanations generate text
- ✅ Statistical analysis completes
- ✅ Real-time optimization handles enemy composition

### **Performance Tests**
- ✅ Build optimization completes in < 5 seconds
- ✅ Multiple concurrent requests don't crash server
- ✅ Database queries are efficient

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```
ImportError: attempted relative import with no known parent package
```
**Solution**: Run from correct directory and use absolute imports

#### **Database Issues**
```
sqlite3.OperationalError: no such column: gods.health_per_level
```
**Solution**: Use PostgreSQL instead of SQLite for full schema

#### **Missing Dependencies**
```
ModuleNotFoundError: No module named 'requests'
```
**Solution**: `pip install requests`

#### **Server Not Starting**
- Check if port 5000 is available
- Verify Python path and imports
- Check database connection

### **Debug Commands**
```bash
# Check database contents
python -c "from divine_arsenal.backend.database import Database; db = Database(); print(f'Gods: {len(db.get_all_gods())}, Items: {len(db.get_all_items())}')"

# Test imports
python -c "from divine_arsenal.backend.working_build_optimizer import ProfessionalBuildOptimizer; print('✅ Optimizer imports work')"

# Check server logs
tail -f divine_arsenal/backend/divine_arsenal.log
```

## 🎯 **Next Steps After Testing**

### **If Tests Pass (6+ out of 8)**
1. **Proceed with Render deployment**
2. **Test community features (Phase 2)**
3. **Invite beta users for feedback**
4. **Monitor performance in production**

### **If Tests Fail (< 6 out of 8)**
1. **Review failed test details**
2. **Fix database/import issues**
3. **Verify all dependencies installed**
4. **Re-run tests until passing**

## 📈 **Performance Benchmarks**

### **Expected Performance**
- **Health Check**: < 100ms
- **Database Queries**: < 500ms
- **Build Optimization**: < 3 seconds
- **Enhanced Optimization**: < 5 seconds
- **Statistical Analysis**: < 10 seconds

### **Resource Usage**
- **Memory**: < 500MB
- **CPU**: < 50% during optimization
- **Database**: < 100 concurrent connections

---

## 🎮 **Ready for Launch?**

Once you achieve:
- ✅ **6+ tests passing**
- ✅ **Core build optimizer working**
- ✅ **Database integrity confirmed**
- ✅ **Performance within benchmarks**

**You're ready to deploy to Render and launch the SMITE 2 Divine Arsenal!** 🚀 