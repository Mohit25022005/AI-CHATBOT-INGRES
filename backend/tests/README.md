# INGRES AI Chatbot Evaluation System

This comprehensive evaluation system tests your INGRES AI chatbot using industry-standard metrics: **BERT scores** for semantic similarity and **BLEU scores** for lexical overlap.

## 🚀 Quick Start

### Option 1: Run from Backend Directory
```bash
cd backend
python run_evaluation.py
```

### Option 2: Run Directly
```bash
cd backend/tests
python evaluate_chatbot.py
```

## 📊 What Gets Evaluated

The system evaluates your chatbot on 10 carefully crafted test cases covering:

- **Connection issues** - Database connectivity problems
- **Configuration** - Port settings and server configuration  
- **Troubleshooting** - Error diagnosis and resolution
- **Transactions** - Isolation levels and transaction management
- **Performance** - Query optimization and performance tuning
- **Error Handling** - Specific error codes and solutions
- **Backup** - Database backup procedures
- **Data Types** - INGRES data type usage
- **Monitoring** - Performance monitoring techniques
- **Maintenance** - Database upgrade procedures

## 🎯 Evaluation Metrics

### BERT Scores (Semantic Similarity)
- **Precision**: How relevant the generated response is
- **Recall**: How much of the expected content is covered
- **F1 Score**: Overall semantic similarity (0-1 scale)

### BLEU Scores (Lexical Overlap)
- Measures exact word/phrase matching with expected answers
- Scale: 0-1 (higher is better)

## 📋 Output Files

After evaluation, you'll find these files in `evaluation_results/`:

1. **`evaluation_report.txt`** - Human-readable summary with performance assessment
2. **`detailed_results.json`** - Complete results data for analysis
3. **`evaluation_results.csv`** - Spreadsheet format for further analysis
4. **`evaluation_charts.png`** - Visual performance charts

## 🏆 Performance Interpretation

### BERT F1 Scores
- **0.85+**: 🟢 EXCELLENT - Very high semantic similarity
- **0.75-0.84**: 🟡 GOOD - Good similarity with room for improvement  
- **0.65-0.74**: 🟠 FAIR - Moderate similarity, needs improvement
- **<0.65**: 🔴 POOR - Low similarity, significant improvement needed

### BLEU Scores
- **0.40+**: 🟢 EXCELLENT - High lexical overlap
- **0.25-0.39**: 🟡 GOOD - Reasonable lexical overlap
- **0.15-0.24**: 🟠 FAIR - Some overlap, could be better
- **<0.15**: 🔴 POOR - Low overlap, needs improvement

## 🔧 Key Features

### Clean Response Processing
- Automatically removes chunk indicators and technical metadata
- Eliminates internal processing information
- Formats responses as coherent single paragraphs
- No "Based on documentation..." prefixes or section numbers

### Comprehensive Analysis
- Category-wise performance breakdown
- Statistical analysis with means and standard deviations
- Best/worst performing example comparisons
- Visual charts and correlation analysis

### Professional Reporting
- Clean, emoji-enhanced reports
- Multiple output formats (TXT, JSON, CSV, PNG)
- Performance assessment with actionable insights

## 📁 File Structure

```
backend/tests/
├── README.md                 # This file
├── evaluation_dataset.json   # Test questions and expected answers
├── response_formatter.py     # Clean response processing
├── evaluate_chatbot.py       # Main evaluation script
└── evaluation_results/       # Generated results directory
    ├── evaluation_report.txt
    ├── detailed_results.json
    ├── evaluation_results.csv
    └── evaluation_charts.png
```

## 🛠️ Dependencies

The evaluation system automatically installs these required packages:
- `bert-score` - For BERT similarity scoring
- `nltk` - Natural language processing
- `sacrebleu` - BLEU score calculation
- `pandas` - Data analysis
- `matplotlib`, `seaborn` - Visualizations
- `evaluate`, `datasets` - Hugging Face evaluation tools

## 🎨 Sample Output

```
🔍 INGRES AI Chatbot Evaluation System
==================================================
🔧 Initializing evaluation components...
📊 Loaded 10 test cases
🚀 Starting comprehensive evaluation...

1️⃣ Generating chatbot responses...
2️⃣ Calculating BERT scores...
3️⃣ Calculating BLEU scores...
4️⃣ Analyzing results by category...
5️⃣ Computing overall statistics...
6️⃣ Generating evaluation report...

==================================================
📋 EVALUATION SUMMARY
==================================================
Total Tests: 10
BERT F1 Score: 0.7842
BLEU Score: 0.2156
==================================================
📁 Results saved to: /path/to/evaluation_results
```

## 💡 Tips for Better Scores

1. **For Higher BERT Scores**: Focus on semantic accuracy and comprehensive coverage of the topic
2. **For Higher BLEU Scores**: Use similar terminology and phrasing as expected answers
3. **Clean Responses**: The system automatically removes chunks and technical info for fair evaluation
4. **Consistent Formatting**: Responses are normalized to single paragraphs for consistent scoring

---

**Ready to evaluate your chatbot?** Run `python run_evaluation.py` from the backend directory!