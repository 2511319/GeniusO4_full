# 🚀 ChartGenius - AI-Powered Cryptocurrency Analysis Platform

**Version:** v1.0.51-stable  
**Status:** ✅ Production Ready  
**Cost:** $1.50/month (98.6% optimized)  
**Last Updated:** 2025-06-25  

---

## 🎯 Quick Start

### 🚀 Production Deployment:
```bash
cd production/
./deploy-production.sh
```

### 🔧 Development:
```bash
cd development/
./start-dev.sh
```

### 🚨 Emergency Rollback:
```bash
cd stable/v1.0.51-stable/scripts/
./emergency_rollback.sh
```

---

## 📁 Project Structure

```
chartgenius/
├── production/          # 🏭 Stable production version (v1.0.51)
├── development/         # 🔬 Development environment (v1.1.0-dev)
├── stable/             # 🔒 Rollback versions and recovery tools
├── backend/            # ⚙️ Backend API service
├── frontend/           # 🌐 Frontend web application
├── bot/               # 🤖 Telegram bot service
├── docs/              # 📚 Documentation and reports
├── archive/           # 📦 Archived files and old versions
├── scripts/           # 🔧 Utility scripts
├── tests/             # 🧪 Test suites
└── configs/           # ⚙️ Configuration files
```

---

## 📚 Documentation

### 🔗 Quick Links:
- **[📋 Project Index](PROJECT_INDEX.md)** - Complete navigation
- **[🏭 Production Guide](production/README.md)** - Production deployment
- **[🔬 Development Guide](development/README.md)** - Development setup
- **[🔒 Rollback Procedures](stable/v1.0.51-stable/README.md)** - Emergency recovery

### 📊 Reports & Documentation:
- **[📁 All Reports](docs/reports/)** - Deployment, fixes, audits
- **[🗂️ Organization Docs](docs/organization/)** - Project organization
- **[📖 Technical Docs](docs/)** - Technical documentation

---

## 🔧 Quick Commands

### 📊 System Status:
```bash
# Check Cloud Run services
gcloud run services list --region=europe-west1

# Check Telegram bot
curl https://api.telegram.org/bot7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0/getWebhookInfo
```

### 💰 Cost Monitoring:
```bash
# Monitor GCP costs
python archive/optimization_scripts/gcp_cost_monitor.py

# Check budget alerts
gcloud billing budgets list --billing-account=01FF05-287B67-1F223D
```

---

## 🏗️ Current Architecture

### ☁️ Cloud Run Services:
| Service | CPU | Memory | Status | Cost/Month |
|---------|-----|--------|--------|------------|
| chartgenius-api-working | 0.25 | 256Mi | ✅ Active | ~$0.50 |
| chartgenius-bot-working | 0.125 | 128Mi | ✅ Active | ~$0.50 |
| chartgenius-frontend | 0.125 | 128Mi | ✅ Active | ~$0.50 |

### 💰 Cost Optimization:
- **Monthly Cost:** $1.50 (was $104.25)
- **Savings:** 98.6% ($102.75/month)
- **Free Tier Status:** ✅ Within limits
- **Budget Alerts:** $5/month threshold

---

## 🔄 Emergency Procedures

### 🚨 Critical Issues:
```bash
# Immediate rollback (< 2 minutes)
cd stable/v1.0.51-stable/scripts/
./emergency_rollback.sh
```

### 🔧 Performance Issues:
```bash
# Full restoration with backup (5-10 minutes)
cd stable/v1.0.51-stable/scripts/
./restore_stable_version.sh
```

---

## 📞 Support & Contacts

### 🆘 Emergency Support:
- **Critical Issues:** Use rollback scripts in `stable/v1.0.51-stable/scripts/`
- **Documentation:** Check `docs/` directory
- **Historical Issues:** Review reports in `docs/reports/`

### 📚 Resources:
- **Technical Documentation:** `docs/`
- **Development Plans:** `development/Chartgenius_r_tr.md`
- **Deployment Guides:** `production/`
- **Archived Materials:** `archive/`

---

**🎉 ChartGenius is production-ready with 98.6% cost optimization!**

*For detailed navigation, see [PROJECT_INDEX.md](PROJECT_INDEX.md)*
