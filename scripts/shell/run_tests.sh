#!/bin/bash
#
# Test runner script for claude_max_proxy project
# Generates JSON report and markdown summary using both pytest-json-report and custom reporter
#

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure we're in the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Create test reports directory if it doesn't exist
mkdir -p test_reports
mkdir -p docs/reports

# Run tests with JSON reporter
echo -e "${BLUE}Running tests with JSON reporter...${NC}"
echo ""

# Run the tests - the custom reporter in conftest.py will generate markdown reports
if uv run pytest -v \
    --json-report \
    --json-report-file=test_results.json \
    --json-report-indent=2 \
    --tb=short \
    --no-header \
    "$@"; then
    TEST_EXIT_CODE=0
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
else
    TEST_EXIT_CODE=$?
    echo -e "\n${RED}❌ Some tests failed!${NC}"
fi

# Generate additional summary report if JSON file exists
if [ -f "test_results.json" ]; then
    echo -e "\n${BLUE}Generating additional summary report...${NC}"
    
    # Generate timestamp
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    REPORT_FILE="test_reports/claude_max_proxy_report.md"
    
    # Create summary JSON file
    SUMMARY_FILE="test_reports/claude_max_proxy_summary.json"
    python -c "
import json
from datetime import datetime

try:
    with open('test_results.json', 'r') as f:
        data = json.load(f)

    summary_data = {
        'project': 'claude_max_proxy',
        'timestamp': datetime.now().isoformat(),
        'summary': data.get('summary', {}),
        'failed_tests': [
            {
                'name': test.get('nodeid', ''),
                'outcome': test.get('outcome', ''),
                'error': test.get('call', {}).get('longrepr', '') if test.get('call') else ''
            }
            for test in data.get('tests', [])
            if test.get('outcome') == 'failed'
        ],
        'passed_tests': len([t for t in data.get('tests', []) if t.get('outcome') == 'passed']),
        'total_tests': len(data.get('tests', [])),
        'duration': data.get('summary', {}).get('duration', 0)
    }

    with open('${SUMMARY_FILE}', 'w') as f:
        json.dump(summary_data, f, indent=2)

    print(f'Summary JSON generated: ${SUMMARY_FILE}')
    
    # Also create a simple markdown summary
    summary = data.get('summary', {})
    total = summary.get('total', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    skipped = summary.get('skipped', 0)
    
    with open('${REPORT_FILE}', 'w') as f:
        f.write(f'''# Claude Max Proxy - Test Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Quick Summary
- **Total Tests**: {total}
- **Passed**: {passed} ✅
- **Failed**: {failed} ❌  
- **Skipped**: {skipped} ⏭️
- **Success Rate**: {(passed/total*100 if total > 0 else 0):.1f}%
- **Duration**: {summary_data['duration']:.2f}s

## Status
{'🟢 All tests passing!' if failed == 0 else '🔴 Tests failing - investigation needed'}

See the full report in docs/reports/test_report_latest.md
''')
    
    print('Summary report generated: ${REPORT_FILE}')
    
except Exception as e:
    print(f'Error generating reports: {e}')
"
    
    echo -e "${GREEN}Reports generated successfully!${NC}"
    
    # Show location of reports
    echo -e "\n${BLUE}Report locations:${NC}"
    echo -e "  - Full report: docs/reports/test_report_latest.md"
    echo -e "  - Summary: ${REPORT_FILE}"
    echo -e "  - JSON data: ${SUMMARY_FILE}"
    
    # Show quick summary
    if [ -f "${REPORT_FILE}" ]; then
        echo -e "\n${BLUE}Quick Summary:${NC}"
        grep -E "(Total Tests|Passed|Failed|Success Rate)" "${REPORT_FILE}" | sed 's/^/  /'
    fi
fi

# Exit with the test exit code
exit $TEST_EXIT_CODE