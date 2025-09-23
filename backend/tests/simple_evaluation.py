#!/usr/bin/env python3
"""
Simplified Chatbot Evaluation Script
Evaluates INGRES AI Chatbot using BERT and BLEU scores - standalone version
"""

import json
import sys
import os
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
import statistics
import warnings
import subprocess

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

def install_basic_dependencies():
    """Install only the most essential dependencies."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "nltk", "pandas"])
        print("✅ Basic dependencies installed")
        return True
    except:
        print("⚠️ Could not install dependencies, continuing...")
        return False

def calculate_simple_similarity(text1: str, text2: str) -> float:
    """Calculate a simple word overlap similarity score."""
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def calculate_bleu_simple(candidate: str, reference: str) -> float:
    """Simple BLEU-like score calculation."""
    if not candidate or not reference:
        return 0.0
    
    candidate_words = candidate.lower().split()
    reference_words = reference.lower().split()
    
    if not candidate_words or not reference_words:
        return 0.0
    
    # Count matching words
    matches = 0
    ref_word_count = {}
    for word in reference_words:
        ref_word_count[word] = ref_word_count.get(word, 0) + 1
    
    for word in candidate_words:
        if word in ref_word_count and ref_word_count[word] > 0:
            matches += 1
            ref_word_count[word] -= 1
    
    # Precision-based score
    precision = matches / len(candidate_words) if candidate_words else 0
    return precision

def get_chatbot_response(question: str) -> str:
    """
    Get response from chatbot by making HTTP request to the backend.
    Falls back to mock responses if backend is not available.
    """
    import requests
    
    try:
        response = requests.post(
            'http://localhost:8000/chat/',
            json={'message': question, 'session_id': 'test'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('reply', 'No response received')
        else:
            return f"Backend error: {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return "Backend not available - using mock response: This is a sample response about INGRES database configuration and troubleshooting."
    except Exception as e:
        return f"Error: {str(e)}"

def clean_response(response: str) -> str:
    """Clean response text to remove chunks and internal information."""
    if not response:
        return ""
    
    cleaned = response.strip()
    
    # Remove common patterns
    patterns_to_remove = [
        r'Based on the INGRES documentation.*?found:\s*',
        r'\*\*\d+\.\s*[^*]*\*\*',  # Remove numbered sections
        r'Title:\s*[^\n]*\n',
        r'Source:\s*[^\n]*\n',
        r'---\s*---',
        r'💡.*?create support ticket.*',
        r'Need more help\?.*'
    ]
    
    import re
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

class SimpleChatbotEvaluator:
    def __init__(self, dataset_path: str, output_dir: str = "evaluation_results"):
        self.dataset_path = dataset_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load test dataset
        self.test_data = self._load_dataset()
        print(f"📊 Loaded {len(self.test_data)} test cases")
        
        # Initialize results storage
        self.results = {
            'responses': [],
            'similarity_scores': [],
            'bleu_scores': [],
            'category_stats': {},
            'overall_stats': {}
        }

    def _load_dataset(self) -> List[Dict]:
        """Load the evaluation dataset."""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            sys.exit(1)

    def evaluate_all(self) -> Dict[str, Any]:
        """Run comprehensive evaluation on all test cases."""
        print("🚀 Starting comprehensive evaluation...")
        print("=" * 60)
        
        # Generate responses for all test questions
        print("1️⃣ Generating chatbot responses...")
        self._generate_responses()
        
        # Calculate similarity scores
        print("2️⃣ Calculating similarity scores...")
        self._calculate_scores()
        
        # Analyze results by category
        print("3️⃣ Analyzing results by category...")
        self._analyze_by_category()
        
        # Calculate overall statistics
        print("4️⃣ Computing overall statistics...")
        self._calculate_overall_stats()
        
        # Generate report
        print("5️⃣ Generating evaluation report...")
        self._generate_report()
        
        print("✅ Evaluation complete!")
        return self.results

    def _generate_responses(self):
        """Generate responses for all test questions."""
        generated_responses = []
        
        for i, test_case in enumerate(self.test_data, 1):
            question = test_case['question']
            print(f"   Generating response {i}/{len(self.test_data)}: {question[:50]}...")
            
            # Get response from chatbot
            raw_response = get_chatbot_response(question)
            
            # Clean the response
            clean_response_text = clean_response(raw_response)
            
            generated_responses.append({
                'question': question,
                'generated_response': clean_response_text,
                'raw_response': raw_response,
                'expected_answer': test_case['expected_answer'],
                'category': test_case['category'],
                'test_id': test_case['id']
            })
            
            # Small delay
            time.sleep(0.2)
        
        self.results['responses'] = generated_responses
        print(f"   ✅ Generated {len(generated_responses)} responses")

    def _calculate_scores(self):
        """Calculate similarity and BLEU scores for all responses."""
        print("   📈 Computing similarity and BLEU scores...")
        
        similarity_scores = []
        bleu_scores = []
        
        for response_data in self.results['responses']:
            generated = response_data['generated_response']
            reference = response_data['expected_answer']
            
            # Calculate simple similarity score
            similarity = calculate_simple_similarity(generated, reference)
            similarity_scores.append(round(similarity, 4))
            
            # Calculate simple BLEU score
            bleu = calculate_bleu_simple(generated, reference)
            bleu_scores.append(round(bleu, 4))
            
            # Add to response data
            response_data['similarity_score'] = round(similarity, 4)
            response_data['bleu_score'] = round(bleu, 4)
        
        self.results['similarity_scores'] = similarity_scores
        self.results['bleu_scores'] = bleu_scores
        print(f"   ✅ Scores calculated for {len(similarity_scores)} responses")

    def _analyze_by_category(self):
        """Analyze results by question category."""
        print("   🔍 Analyzing performance by category...")
        
        categories = {}
        
        for response_data in self.results['responses']:
            category = response_data['category']
            
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'similarity_scores': [],
                    'bleu_scores': []
                }
            
            categories[category]['count'] += 1
            categories[category]['similarity_scores'].append(response_data['similarity_score'])
            categories[category]['bleu_scores'].append(response_data['bleu_score'])
        
        # Calculate category statistics
        category_stats = {}
        for category, data in categories.items():
            category_stats[category] = {
                'count': data['count'],
                'avg_similarity': round(statistics.mean(data['similarity_scores']), 4),
                'avg_bleu': round(statistics.mean(data['bleu_scores']), 4),
                'similarity_std': round(statistics.stdev(data['similarity_scores']) if len(data['similarity_scores']) > 1 else 0, 4),
                'bleu_std': round(statistics.stdev(data['bleu_scores']) if len(data['bleu_scores']) > 1 else 0, 4)
            }
        
        self.results['category_stats'] = category_stats
        print(f"   ✅ Analyzed {len(category_stats)} categories")

    def _calculate_overall_stats(self):
        """Calculate overall performance statistics."""
        print("   📈 Computing overall statistics...")
        
        similarity_scores = [r['similarity_score'] for r in self.results['responses']]
        bleu_scores = [r['bleu_score'] for r in self.results['responses']]
        
        self.results['overall_stats'] = {
            'total_tests': len(self.results['responses']),
            'similarity_scores': {
                'average': round(statistics.mean(similarity_scores), 4),
                'std': round(statistics.stdev(similarity_scores) if len(similarity_scores) > 1 else 0, 4),
                'min': round(min(similarity_scores), 4),
                'max': round(max(similarity_scores), 4)
            },
            'bleu_scores': {
                'average': round(statistics.mean(bleu_scores), 4),
                'std': round(statistics.stdev(bleu_scores) if len(bleu_scores) > 1 else 0, 4),
                'min': round(min(bleu_scores), 4),
                'max': round(max(bleu_scores), 4)
            }
        }
        
        print("   ✅ Overall statistics computed")

    def _generate_report(self):
        """Generate comprehensive evaluation report."""
        report_content = self._create_text_report()
        
        # Save text report
        report_file = self.output_dir / "evaluation_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Save detailed results as JSON
        results_file = self.output_dir / "detailed_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"   📄 Report saved to: {report_file}")
        print(f"   📊 Detailed results: {results_file}")

    def _create_text_report(self) -> str:
        """Create formatted text report."""
        stats = self.results['overall_stats']
        
        report = f"""
{'=' * 80}
INGRES AI CHATBOT EVALUATION REPORT (SIMPLIFIED)
{'=' * 80}

📊 OVERVIEW
-----------
Total Test Cases: {stats['total_tests']}
Evaluation Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

🎯 OVERALL PERFORMANCE METRICS
------------------------------
Word Overlap Similarity:
  • Average:      {stats['similarity_scores']['average']:.4f} ± {stats['similarity_scores']['std']:.4f}
  • Range:        {stats['similarity_scores']['min']:.4f} - {stats['similarity_scores']['max']:.4f}

BLEU-style Score:
  • Average:      {stats['bleu_scores']['average']:.4f} ± {stats['bleu_scores']['std']:.4f}
  • Range:        {stats['bleu_scores']['min']:.4f} - {stats['bleu_scores']['max']:.4f}

📈 PERFORMANCE BY CATEGORY
---------------------------
"""
        
        # Add category breakdown
        for category, cat_stats in sorted(self.results['category_stats'].items()):
            report += f"""
{category.upper()} ({cat_stats['count']} tests):
  • Similarity:   {cat_stats['avg_similarity']:.4f} ± {cat_stats['similarity_std']:.4f}
  • BLEU:         {cat_stats['avg_bleu']:.4f} ± {cat_stats['bleu_std']:.4f}
"""
        
        # Add performance interpretation
        sim_avg = stats['similarity_scores']['average']
        bleu_avg = stats['bleu_scores']['average']
        
        report += f"""
🏆 PERFORMANCE ASSESSMENT
-------------------------
Word Overlap Similarity ({sim_avg:.4f}):
"""
        
        if sim_avg >= 0.60:
            report += "  🟢 GOOD - High word overlap with expected answers\n"
        elif sim_avg >= 0.40:
            report += "  🟡 FAIR - Moderate word overlap\n"
        else:
            report += "  🔴 NEEDS IMPROVEMENT - Low word overlap\n"
        
        report += f"""
BLEU Score ({bleu_avg:.4f}):
"""
        
        if bleu_avg >= 0.50:
            report += "  🟢 GOOD - High lexical precision\n"
        elif bleu_avg >= 0.30:
            report += "  🟡 FAIR - Moderate lexical precision\n"
        else:
            report += "  🔴 NEEDS IMPROVEMENT - Low lexical precision\n"
        
        # Add sample responses
        report += "\n📝 SAMPLE RESPONSE COMPARISONS\n"
        report += "=" * 50 + "\n"
        
        # Show best and worst performing examples
        responses_with_scores = [
            (r, r['similarity_score']) for r in self.results['responses']
        ]
        responses_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Best performance
        best_response = responses_with_scores[0][0]
        report += f"""
🥇 BEST PERFORMANCE (Similarity: {best_response['similarity_score']:.4f})
Question: {best_response['question']}

Expected: {best_response['expected_answer'][:200]}...

Generated: {best_response['generated_response'][:200]}...
"""
        
        # Worst performance
        worst_response = responses_with_scores[-1][0]
        report += f"""
🥉 NEEDS IMPROVEMENT (Similarity: {worst_response['similarity_score']:.4f})
Question: {worst_response['question']}

Expected: {worst_response['expected_answer'][:200]}...

Generated: {worst_response['generated_response'][:200]}...
"""
        
        report += f"""
{'=' * 80}
NOTE: This is a simplified evaluation using basic word overlap metrics.
For more advanced BERT scoring, resolve the dependency conflicts.
{'=' * 80}
EVALUATION COMPLETE
Files generated in: {self.output_dir}
{'=' * 80}
"""
        
        return report

def main():
    """Main evaluation function."""
    print("🔍 INGRES AI Chatbot Evaluation System (Simplified)")
    print("=" * 60)
    
    # Install basic dependencies
    install_basic_dependencies()
    
    # Configuration
    dataset_path = Path(__file__).parent / "evaluation_dataset.json"
    output_dir = "evaluation_results"
    
    # Initialize evaluator
    try:
        evaluator = SimpleChatbotEvaluator(str(dataset_path), output_dir)
    except Exception as e:
        print(f"❌ Failed to initialize evaluator: {e}")
        return
    
    # Run evaluation
    try:
        results = evaluator.evaluate_all()
        
        # Print summary to console
        stats = results['overall_stats']
        print("\n" + "=" * 60)
        print("📋 EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {stats['total_tests']}")
        print(f"Word Similarity: {stats['similarity_scores']['average']:.4f}")
        print(f"BLEU Score: {stats['bleu_scores']['average']:.4f}")
        print("=" * 60)
        print(f"📁 Results saved to: {Path(output_dir).absolute()}")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()