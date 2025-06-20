#!/bin/bash
# Complete verification script for llm_call - tests ALL 100 features

echo "🚀 Running COMPLETE llm_call Feature Verification (100% coverage)"
echo "================================================================"
echo "This will test ALL 100 documented features comprehensively."
echo "Estimated time: 10-15 minutes"
echo "================================================================"

# Ensure we're in the right directory
cd /home/graham/workspace/experiments/llm_call

# Set up environment
export PYTHONPATH=./src
source .venv/bin/activate 2>/dev/null || true

# Run the ultimate verification WITHOUT quick mode to test everything
echo ""
echo "Starting comprehensive verification..."
python -m llm_call.verification.ultimate_feature_verification --cache 2>&1 | tee verification_complete.log

echo ""
echo "================================================================"
echo "✅ Complete verification finished!"
echo "📊 Report available at: verification_dashboard.html"
echo "📝 Full log saved to: verification_complete.log"
echo ""
echo "To view the report:"
echo "  python -m http.server 8000"
echo "  Then open: http://localhost:8000/verification_dashboard.html"
echo "================================================================"