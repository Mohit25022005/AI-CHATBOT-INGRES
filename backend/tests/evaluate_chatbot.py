#!/usr/bin/env python3
"""
Comprehensive Chatbot Evaluation Script
Evaluates INGRES AI Chatbot using BERT and BLEU scores with clean output formatting.
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

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

# Import evaluation libraries
try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from bert_score import score
    from sacrebleu import sentence_bleu
    import nltk
    # Skip transformers pipeline import to avoid dependency conflicts
    # from transformers import pipeline
    # import torch
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Please install missing dependencies with: pip install -r requirements.txt")
    sys.exit(1)

# Import local modules
from app.services.rag_pipeline import RAGPipeline
from response_formatter import ResponseFormatter

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class ChatbotEvaluator:
    def __init__(self, dataset_path: str, output_dir: str = "evaluation_results"):
        self.dataset_path = dataset_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        print("🔧 Initializing evaluation components...")
        self.rag_pipeline = RAGPipeline()
        self.response_formatter = ResponseFormatter()
        
        # Load test dataset
        self.test_data = self._load_dataset()
        print(f"📊 Loaded {len(self.test_data)} test cases")
        
        # Initialize results storage
        self.results = {
            'responses': [],
            'bert_scores': [],
            'bleu_scores': [],
            'individual_results': [],
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

    async def evaluate_all(self) -> Dict[str, Any]:
        """Run comprehensive evaluation on all test cases."""
        print("🚀 Starting comprehensive evaluation...")
        print("=" * 60)
        
        total_tests = len(self.test_data)
        
        # Generate responses for all test questions
        print("1️⃣ Generating chatbot responses...")
        await self._generate_responses()
        
        # Calculate BERT scores
        print("2️⃣ Calculating BERT scores...")
        self._calculate_bert_scores()
        
        # Calculate BLEU scores
        print("3️⃣ Calculating BLEU scores...")
        self._calculate_bleu_scores()
        
        # Analyze results by category
        print("4️⃣ Analyzing results by category...")
        self._analyze_by_category()
        
        # Calculate overall statistics
        print("5️⃣ Computing overall statistics...")
        self._calculate_overall_stats()
        
        # Generate report
        print("6️⃣ Generating evaluation report...")
        self._generate_report()
        
        print("✅ Evaluation complete!")
        return self.results

    async def _generate_responses(self):
        """Generate responses for all test questions."""
        generated_responses = []
        
        for i, test_case in enumerate(self.test_data, 1):
            question = test_case['question']
            print(f"   Generating response {i}/{len(self.test_data)}: {question[:50]}...")
            
            try:
                # Generate response using RAG pipeline
                raw_response, sources = self.rag_pipeline.generate_response(question)
                
                # Clean the response
                clean_response = self.response_formatter.format_for_evaluation(raw_response)
                
                generated_responses.append({
                    'question': question,
                    'generated_response': clean_response,
                    'raw_response': raw_response,
                    'expected_answer': test_case['expected_answer'],
                    'category': test_case['category'],
                    'test_id': test_case['id']
                })
                
                # Small delay to avoid overwhelming the system
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"   ⚠️ Error generating response for test {i}: {e}")
                generated_responses.append({
                    'question': question,
                    'generated_response': f"Error: {str(e)}",
                    'raw_response': f"Error: {str(e)}",
                    'expected_answer': test_case['expected_answer'],
                    'category': test_case['category'],
                    'test_id': test_case['id']
                })
        
        self.results['responses'] = generated_responses
        print(f"   ✅ Generated {len(generated_responses)} responses")

    def _calculate_bert_scores(self):
        """Calculate BERT scores for all responses."""
        print("   📈 Computing BERT similarity scores...")
        
        generated_texts = [r['generated_response'] for r in self.results['responses']]
        reference_texts = [r['expected_answer'] for r in self.results['responses']]
        
        try:
            # Calculate BERT scores
            P, R, F1 = score(generated_texts, reference_texts, lang='en', verbose=False)
            
            # Store individual scores
            bert_scores = []
            for i, (p, r, f1) in enumerate(zip(P.tolist(), R.tolist(), F1.tolist())):
                bert_scores.append({
                    'precision': round(p, 4),
                    'recall': round(r, 4),
                    'f1': round(f1, 4)
                })
                
                # Add to individual results
                self.results['responses'][i]['bert_score'] = bert_scores[-1]
            
            self.results['bert_scores'] = bert_scores
            print(f"   ✅ BERT scores calculated for {len(bert_scores)} responses")
            
        except Exception as e:
            print(f"   ⚠️ Error calculating BERT scores: {e}")
            self.results['bert_scores'] = [{'precision': 0, 'recall': 0, 'f1': 0}] * len(generated_texts)

    def _calculate_bleu_scores(self):
        """Calculate BLEU scores for all responses."""
        print("   📊 Computing BLEU scores...")
        
        bleu_scores = []
        
        for response_data in self.results['responses']:
            generated = response_data['generated_response']
            reference = response_data['expected_answer']
            
            try:
                # Calculate sentence BLEU score
                bleu_score = sentence_bleu(generated, [reference]).score / 100.0  # Convert to 0-1 scale
                bleu_scores.append(round(bleu_score, 4))
                
                # Add to response data
                response_data['bleu_score'] = round(bleu_score, 4)
                
            except Exception as e:
                print(f"   ⚠️ Error calculating BLEU for one response: {e}")
                bleu_scores.append(0.0)
                response_data['bleu_score'] = 0.0
        
        self.results['bleu_scores'] = bleu_scores
        print(f"   ✅ BLEU scores calculated for {len(bleu_scores)} responses")

    def _analyze_by_category(self):
        """Analyze results by question category."""
        print("   🔍 Analyzing performance by category...")
        
        categories = {}
        
        for response_data in self.results['responses']:
            category = response_data['category']
            
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'bert_f1_scores': [],
                    'bleu_scores': []
                }
            
            categories[category]['count'] += 1
            categories[category]['bert_f1_scores'].append(response_data['bert_score']['f1'])
            categories[category]['bleu_scores'].append(response_data['bleu_score'])
        
        # Calculate category statistics
        category_stats = {}
        for category, data in categories.items():
            category_stats[category] = {
                'count': data['count'],
                'avg_bert_f1': round(statistics.mean(data['bert_f1_scores']), 4),
                'avg_bleu': round(statistics.mean(data['bleu_scores']), 4),
                'bert_f1_std': round(statistics.stdev(data['bert_f1_scores']) if len(data['bert_f1_scores']) > 1 else 0, 4),
                'bleu_std': round(statistics.stdev(data['bleu_scores']) if len(data['bleu_scores']) > 1 else 0, 4)
            }
        
        self.results['category_stats'] = category_stats
        print(f"   ✅ Analyzed {len(category_stats)} categories")

    def _calculate_overall_stats(self):
        """Calculate overall performance statistics."""
        print("   📈 Computing overall statistics...")
        
        bert_f1_scores = [r['bert_score']['f1'] for r in self.results['responses']]
        bert_precision_scores = [r['bert_score']['precision'] for r in self.results['responses']]
        bert_recall_scores = [r['bert_score']['recall'] for r in self.results['responses']]
        bleu_scores = [r['bleu_score'] for r in self.results['responses']]
        
        self.results['overall_stats'] = {
            'total_tests': len(self.results['responses']),
            'bert_scores': {
                'avg_f1': round(statistics.mean(bert_f1_scores), 4),
                'avg_precision': round(statistics.mean(bert_precision_scores), 4),
                'avg_recall': round(statistics.mean(bert_recall_scores), 4),
                'f1_std': round(statistics.stdev(bert_f1_scores) if len(bert_f1_scores) > 1 else 0, 4),
                'f1_min': round(min(bert_f1_scores), 4),
                'f1_max': round(max(bert_f1_scores), 4)
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
        
        # Create CSV for analysis
        self._create_csv_export()
        
        # Create visualizations
        self._create_visualizations()
        
        print(f"   📄 Report saved to: {report_file}")
        print(f"   📊 Detailed results: {results_file}")

    def _create_text_report(self) -> str:
        """Create formatted text report."""
        stats = self.results['overall_stats']
        
        report = f"""
{'=' * 80}
INGRES AI CHATBOT EVALUATION REPORT
{'=' * 80}

📊 OVERVIEW
-----------
Total Test Cases: {stats['total_tests']}
Evaluation Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

🎯 OVERALL PERFORMANCE METRICS
------------------------------
BERT Scores:
  • F1 Score:     {stats['bert_scores']['avg_f1']:.4f} ± {stats['bert_scores']['f1_std']:.4f}
  • Precision:    {stats['bert_scores']['avg_precision']:.4f}
  • Recall:       {stats['bert_scores']['avg_recall']:.4f}
  • F1 Range:     {stats['bert_scores']['f1_min']:.4f} - {stats['bert_scores']['f1_max']:.4f}

BLEU Scores:
  • Average:      {stats['bleu_scores']['average']:.4f} ± {stats['bleu_scores']['std']:.4f}
  • Range:        {stats['bleu_scores']['min']:.4f} - {stats['bleu_scores']['max']:.4f}

📈 PERFORMANCE BY CATEGORY
---------------------------
"""
        
        # Add category breakdown
        for category, cat_stats in sorted(self.results['category_stats'].items()):
            report += f"""
{category.upper()} ({cat_stats['count']} tests):
  • BERT F1:      {cat_stats['avg_bert_f1']:.4f} ± {cat_stats['bert_f1_std']:.4f}
  • BLEU:         {cat_stats['avg_bleu']:.4f} ± {cat_stats['bleu_std']:.4f}
"""
        
        # Add performance interpretation
        bert_f1_avg = stats['bert_scores']['avg_f1']
        bleu_avg = stats['bleu_scores']['average']
        
        report += f"""
🏆 PERFORMANCE ASSESSMENT
-------------------------
BERT F1 Score ({bert_f1_avg:.4f}):
"""
        
        if bert_f1_avg >= 0.85:
            report += "  🟢 EXCELLENT - Very high semantic similarity to expected answers\n"
        elif bert_f1_avg >= 0.75:
            report += "  🟡 GOOD - Good semantic similarity with room for improvement\n"
        elif bert_f1_avg >= 0.65:
            report += "  🟠 FAIR - Moderate semantic similarity, needs improvement\n"
        else:
            report += "  🔴 POOR - Low semantic similarity, significant improvement needed\n"
        
        report += f"""
BLEU Score ({bleu_avg:.4f}):
"""
        
        if bleu_avg >= 0.40:
            report += "  🟢 EXCELLENT - High lexical overlap with expected answers\n"
        elif bleu_avg >= 0.25:
            report += "  🟡 GOOD - Reasonable lexical overlap\n"
        elif bleu_avg >= 0.15:
            report += "  🟠 FAIR - Some lexical overlap, could be better\n"
        else:
            report += "  🔴 POOR - Low lexical overlap, needs improvement\n"
        
        # Add sample responses
        report += "\n📝 SAMPLE RESPONSE COMPARISONS\n"
        report += "=" * 50 + "\n"
        
        # Show best and worst performing examples
        responses_with_scores = [
            (r, r['bert_score']['f1']) for r in self.results['responses']
        ]
        responses_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Best performance
        best_response = responses_with_scores[0][0]
        report += f"""
🥇 BEST PERFORMANCE (BERT F1: {best_response['bert_score']['f1']:.4f})
Question: {best_response['question']}

Expected: {best_response['expected_answer'][:200]}...

Generated: {best_response['generated_response'][:200]}...
"""
        
        # Worst performance
        worst_response = responses_with_scores[-1][0]
        report += f"""
🥉 NEEDS IMPROVEMENT (BERT F1: {worst_response['bert_score']['f1']:.4f})
Question: {worst_response['question']}

Expected: {worst_response['expected_answer'][:200]}...

Generated: {worst_response['generated_response'][:200]}...
"""
        
        report += f"""
{'=' * 80}
EVALUATION COMPLETE
Files generated in: {self.output_dir}
{'=' * 80}
"""
        
        return report

    def _create_csv_export(self):
        """Create CSV export for detailed analysis."""
        csv_data = []
        
        for response_data in self.results['responses']:
            csv_data.append({
                'test_id': response_data['test_id'],
                'category': response_data['category'],
                'question': response_data['question'],
                'expected_answer': response_data['expected_answer'],
                'generated_response': response_data['generated_response'],
                'bert_f1': response_data['bert_score']['f1'],
                'bert_precision': response_data['bert_score']['precision'],
                'bert_recall': response_data['bert_score']['recall'],
                'bleu_score': response_data['bleu_score']
            })
        
        df = pd.DataFrame(csv_data)
        csv_file = self.output_dir / "evaluation_results.csv"
        df.to_csv(csv_file, index=False)
        print(f"   📊 CSV export: {csv_file}")

    def _create_visualizations(self):
        """Create performance visualization charts."""
        try:
            # Set up the plotting style
            plt.style.use('default')
            sns.set_palette("husl")
            
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('INGRES AI Chatbot Evaluation Results', fontsize=16, fontweight='bold')
            
            # Data preparation
            categories = list(self.results['category_stats'].keys())
            bert_f1_by_category = [self.results['category_stats'][cat]['avg_bert_f1'] for cat in categories]
            bleu_by_category = [self.results['category_stats'][cat]['avg_bleu'] for cat in categories]
            
            # Plot 1: BERT F1 scores by category
            bars1 = ax1.bar(categories, bert_f1_by_category, alpha=0.8, color='skyblue')
            ax1.set_title('BERT F1 Scores by Category', fontweight='bold')
            ax1.set_ylabel('BERT F1 Score')
            ax1.set_ylim(0, 1)
            ax1.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, score in zip(bars1, bert_f1_by_category):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                        f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
            
            # Plot 2: BLEU scores by category  
            bars2 = ax2.bar(categories, bleu_by_category, alpha=0.8, color='lightcoral')
            ax2.set_title('BLEU Scores by Category', fontweight='bold')
            ax2.set_ylabel('BLEU Score')
            ax2.set_ylim(0, max(bleu_by_category) * 1.2)
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, score in zip(bars2, bleu_by_category):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001, 
                        f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
            
            # Plot 3: Score distribution histogram
            bert_f1_scores = [r['bert_score']['f1'] for r in self.results['responses']]
            ax3.hist(bert_f1_scores, bins=10, alpha=0.7, color='green', edgecolor='black')
            ax3.set_title('BERT F1 Score Distribution', fontweight='bold')
            ax3.set_xlabel('BERT F1 Score')
            ax3.set_ylabel('Frequency')
            ax3.axvline(statistics.mean(bert_f1_scores), color='red', linestyle='--', 
                       label=f'Mean: {statistics.mean(bert_f1_scores):.3f}')
            ax3.legend()
            
            # Plot 4: BERT vs BLEU scatter
            bleu_scores = [r['bleu_score'] for r in self.results['responses']]
            scatter = ax4.scatter(bert_f1_scores, bleu_scores, alpha=0.6, s=50)
            ax4.set_title('BERT F1 vs BLEU Score Correlation', fontweight='bold')
            ax4.set_xlabel('BERT F1 Score')
            ax4.set_ylabel('BLEU Score')
            
            # Add correlation line
            z = np.polyfit(bert_f1_scores, bleu_scores, 1)
            p = np.poly1d(z)
            ax4.plot(bert_f1_scores, p(bert_f1_scores), "r--", alpha=0.8)
            
            # Calculate correlation coefficient
            correlation = np.corrcoef(bert_f1_scores, bleu_scores)[0, 1]
            ax4.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                    transform=ax4.transAxes, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            
            # Save the plot
            plot_file = self.output_dir / "evaluation_charts.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"   📈 Visualizations: {plot_file}")
            
        except Exception as e:
            print(f"   ⚠️ Could not create visualizations: {e}")

async def main():
    """Main evaluation function."""
    print("🔍 INGRES AI Chatbot Evaluation System")
    print("=" * 50)
    
    # Configuration
    dataset_path = Path(__file__).parent / "evaluation_dataset.json"
    output_dir = "evaluation_results"
    
    # Initialize evaluator
    try:
        evaluator = ChatbotEvaluator(str(dataset_path), output_dir)
    except Exception as e:
        print(f"❌ Failed to initialize evaluator: {e}")
        return
    
    # Run evaluation
    try:
        results = await evaluator.evaluate_all()
        
        # Print summary to console
        stats = results['overall_stats']
        print("\n" + "=" * 50)
        print("📋 EVALUATION SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {stats['total_tests']}")
        print(f"BERT F1 Score: {stats['bert_scores']['avg_f1']:.4f}")
        print(f"BLEU Score: {stats['bleu_scores']['average']:.4f}")
        print("=" * 50)
        print(f"📁 Results saved to: {Path(output_dir).absolute()}")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())