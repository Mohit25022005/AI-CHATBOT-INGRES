# 🚀 How to Run INGRES AI Chatbot Evaluation

## 📋 Quick Start (3 Methods)

### Method 1: PowerShell Script (Recommended)
```powershell
# From backend directory
.\run_full_evaluation.ps1
```

### Method 2: Manual Process
1. **Start Backend Server** (in one terminal):
```powershell
cd C:\Users\mohit\ai-chatbot-ingres\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Run Evaluation** (in another terminal):
```powershell
cd C:\Users\mohit\ai-chatbot-ingres\backend\tests
python simple_evaluation.py
```

### Method 3: Evaluation Only (Mock Responses)
```powershell
cd C:\Users\mohit\ai-chatbot-ingres\backend\tests
python simple_evaluation.py
```
*Note: This will use mock responses if backend is not running*

## 📊 What You'll Get

After running the evaluation, check the `evaluation_results` folder:

- **`evaluation_report.txt`** - Human-readable summary
- **`detailed_results.json`** - Complete data for analysis

## 🎯 Understanding the Results

### Word Overlap Similarity Score (0.0 - 1.0)
- **0.6+**: 🟢 GOOD - High word overlap
- **0.4-0.6**: 🟡 FAIR - Moderate overlap  
- **<0.4**: 🔴 NEEDS IMPROVEMENT

### BLEU Score (0.0 - 1.0)
- **0.5+**: 🟢 GOOD - High precision
- **0.3-0.5**: 🟡 FAIR - Moderate precision
- **<0.3**: 🔴 NEEDS IMPROVEMENT

## 🔧 Troubleshooting

### Backend Won't Start
- Make sure you're in the backend directory
- Check if port 8000 is free: `netstat -an | findstr :8000`
- Install dependencies: `pip install -r requirements.txt`

### Evaluation Fails
- The script will use mock responses if backend isn't available
- Check Python dependencies are installed

## 📈 Sample Output

```
🔍 INGRES AI Chatbot Evaluation System (Simplified)
============================================================
📊 Loaded 10 test cases
🚀 Starting comprehensive evaluation...

1️⃣ Generating chatbot responses...
2️⃣ Calculating similarity scores...
3️⃣ Analyzing results by category...
4️⃣ Computing overall statistics...
5️⃣ Generating evaluation report...

============================================================
📋 EVALUATION SUMMARY
============================================================
Total Tests: 10
Word Similarity: 0.0711
BLEU Score: 0.2000
============================================================
📁 Results saved to: C:\...\evaluation_results
```

## ✨ Features

✅ **Clean Output**: No chunks, no internal metadata  
✅ **BERT & BLEU**: Industry-standard similarity metrics  
✅ **Category Analysis**: Performance by question type  
✅ **Mock Fallback**: Works with or without backend  
✅ **Professional Reports**: Multiple output formats  

---

**Ready to test your chatbot?** Run `.\run_full_evaluation.ps1` from the backend directory!