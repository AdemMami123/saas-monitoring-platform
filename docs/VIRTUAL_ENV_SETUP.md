# Virtual Environment Setup Guide

## ✅ Setup Complete!

Your Python virtual environment has been successfully created and configured.

---

## 📁 What Was Created

```
saas-monitoring-platform/
├── venv/                          # Virtual environment folder
│   ├── bin/                       # Executables (python, pip)
│   ├── lib/                       # Installed packages
│   └── ...
├── run_generate_logs.sh           # Linux/WSL helper script
├── run_generate_logs.bat          # Windows helper script
├── generate_logs.py               # Log generator
└── uploads/
    ├── generated_logs.csv         # ✓ Generated (3.5 MB)
    └── generated_logs.json        # ✓ Generated (7.0 MB)
```

---

## 🚀 How to Run generate_logs.py

### Method 1: Using Helper Scripts (EASIEST)

#### On Linux/WSL:
```bash
./run_generate_logs.sh
```

#### On Windows PowerShell:
```powershell
.\run_generate_logs.bat
```

Or double-click `run_generate_logs.bat` in File Explorer.

---

### Method 2: Manual Activation (More Control)

#### On Linux/WSL:
```bash
# Navigate to project
cd /home/ademm/saas-monitoring-platform

# Activate virtual environment
source venv/bin/activate

# Run the script
python generate_logs.py

# Deactivate when done
deactivate
```

#### On Windows PowerShell (via WSL):
```powershell
# Activate and run in one command
wsl -d Ubuntu bash -c "cd /home/ademm/saas-monitoring-platform && source venv/bin/activate && python generate_logs.py"
```

---

### Method 3: Direct Python Call

```bash
# Use virtual environment Python directly
cd /home/ademm/saas-monitoring-platform
./venv/bin/python generate_logs.py
```

Or from Windows:
```powershell
wsl -d Ubuntu bash -c "cd /home/ademm/saas-monitoring-platform && ./venv/bin/python generate_logs.py"
```

---

## 📦 Installed Packages

Inside the virtual environment:
- **Faker 37.12.0** - For generating realistic fake data
- **tzdata 2025.2** - Timezone database (dependency)

---

## 🔧 Managing the Virtual Environment

### Install Additional Packages
```bash
# Activate first
source venv/bin/activate

# Install package
pip install package-name

# Or install from requirements.txt
pip install -r app/requirements.txt
```

### List Installed Packages
```bash
source venv/bin/activate
pip list
```

### Upgrade Packages
```bash
source venv/bin/activate
pip install --upgrade Faker
```

### Remove Virtual Environment
```bash
# If you need to start fresh
rm -rf venv

# Then recreate it
python3 -m venv venv
source venv/bin/activate
pip install Faker
```

---

## ✅ Verification

Check that everything is working:

```bash
# 1. Check virtual environment exists
ls -la venv/

# 2. Check Python version
./venv/bin/python --version

# 3. Check Faker is installed
./venv/bin/python -c "import faker; print(faker.__version__)"

# 4. Verify generated files
ls -lh uploads/generated_logs.*
```

**Expected output:**
```
-rw-r--r-- 1 ademm ademm 3.5M Nov  1 02:31 uploads/generated_logs.csv
-rw-r--r-- 1 ademm ademm 7.0M Nov  1 02:31 uploads/generated_logs.json
```

---

## 🎯 Why Use a Virtual Environment?

1. **Isolation**: Packages are isolated from system Python
2. **No Permission Issues**: No need for sudo/admin rights
3. **Version Control**: Different projects can use different package versions
4. **Clean**: Easy to delete and recreate
5. **No Conflicts**: Avoids "externally-managed-environment" errors

---

## 🔍 Troubleshooting

### "Virtual environment not found"
```bash
# Recreate it
cd /home/ademm/saas-monitoring-platform
python3 -m venv venv
source venv/bin/activate
pip install Faker
```

### "ImportError: No module named 'faker'"
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall Faker
pip install Faker
```

### "Permission denied" when running .sh script
```bash
# Make script executable
chmod +x run_generate_logs.sh
```

### Want to use a different Python version?
```bash
# Use specific version
python3.11 -m venv venv

# Or
python3.12 -m venv venv
```

---

## 📊 Current Generated Logs Statistics

From your last run:

- **Total Logs**: 10,000
- **Time Range**: Oct 25 - Nov 1, 2025 (7 days)
- **CSV File**: 3.5 MB
- **JSON File**: 7.0 MB

**Log Levels:**
- INFO: 70.18% (7,018 logs)
- WARNING: 14.80% (1,480 logs)
- ERROR: 10.10% (1,010 logs)
- DEBUG: 3.98% (398 logs)
- CRITICAL: 0.94% (94 logs)

**Status Codes:**
- 200: 64.44% (success)
- 201: 10.29% (created)
- 400: 8.32% (bad request)
- 404: 5.08% (not found)
- 401: 4.96% (unauthorized)
- Other: 6.91%

**Response Times:**
- Average: 806 ms
- Min: 50 ms
- Max: 9,997 ms

---

## 🚀 Next Steps

1. **Upload the generated logs:**
   ```
   Open: http://localhost:5000/upload
   Upload: uploads/generated_logs.csv
   ```

2. **View in Kibana:**
   ```
   Open: http://localhost:5601
   Follow: docs/KIBANA_SETUP.md
   ```

3. **Search logs:**
   ```
   Open: http://localhost:5000/search
   ```

---

## 📚 Additional Resources

- **Python venv docs**: https://docs.python.org/3/library/venv.html
- **Faker docs**: https://faker.readthedocs.io/
- **Project docs**: See `docs/` folder

---

**🎉 You're all set! No more "externally-managed-environment" errors!**
