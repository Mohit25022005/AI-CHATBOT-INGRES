#!/usr/bin/env python3
"""
Easy-to-use script to run chatbot evaluation.
Installs dependencies and runs the complete evaluation suite.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required dependencies for evaluation."""
    print("🔧 Installing evaluation dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_evaluation():
    """Run the chatbot evaluation."""
    print("\n🚀 Starting chatbot evaluation...")
    
    # Change to tests directory
    tests_dir = Path(__file__).parent / "tests"
    os.chdir(tests_dir)
    
    try:
        # Run the evaluation script
        subprocess.check_call([sys.executable, "evaluate_chatbot.py"])
        print("✅ Evaluation completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Evaluation failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Evaluation script not found. Make sure evaluate_chatbot.py exists in tests directory.")
        return False

def main():
    """Main execution function."""
    print("=" * 60)
    print("🔍 INGRES AI Chatbot Evaluation Runner")
    print("=" * 60)
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"📂 Working directory: {current_dir}")
    
    # Check if we're in the right directory (backend)
    backend_dir = Path(__file__).parent
    if current_dir != backend_dir:
        print(f"📂 Changing to backend directory: {backend_dir}")
        os.chdir(backend_dir)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Cannot proceed without required dependencies.")
        sys.exit(1)
    
    # Run evaluation
    success = run_evaluation()
    
    if success:
        # Show results location
        results_dir = backend_dir / "tests" / "evaluation_results"
        print(f"\n📊 Results saved to: {results_dir}")
        print("\n📋 Key files generated:")
        print("   • evaluation_report.txt    - Human-readable summary")
        print("   • detailed_results.json    - Complete results data")
        print("   • evaluation_results.csv   - Spreadsheet format")
        print("   • evaluation_charts.png    - Performance visualizations")
        print("\n🎉 Evaluation complete! Check the results directory for detailed analysis.")
    else:
        print("\n❌ Evaluation failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()