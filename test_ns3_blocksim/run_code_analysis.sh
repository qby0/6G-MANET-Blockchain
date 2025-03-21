#!/bin/bash
# Script to run code analysis tools for the NS-3 and Blockchain Simulation project

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools and install them if needed
echo "Checking required tools..."
REQUIRED_TOOLS=("black" "pylint" "mypy" "bandit")
MISSING_TOOLS=()

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command_exists "$tool"; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo "The following tools are missing: ${MISSING_TOOLS[*]}"
    read -p "Would you like to install them now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install "${MISSING_TOOLS[@]}"
    else
        echo "Cannot continue without required tools. Exiting."
        exit 1
    fi
fi

# Parse command line arguments
ALL=false
FORMAT_ONLY=false
LINT_ONLY=false
TYPE_CHECK_ONLY=false
SECURITY_ONLY=false
DIRECTORIES=("models" "scripts")

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --all) ALL=true ;;
        --format) FORMAT_ONLY=true ;;
        --lint) LINT_ONLY=true ;;
        --type) TYPE_CHECK_ONLY=true ;;
        --security) SECURITY_ONLY=true ;;
        --dirs)
            shift
            IFS=',' read -ra DIRECTORIES <<< "$1"
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo "Running code analysis on directories: ${DIRECTORIES[*]}"

# Create output directory
REPORT_DIR="code_analysis_reports"
mkdir -p "$REPORT_DIR"
DATE_STAMP=$(date +"%Y%m%d_%H%M%S")

# Run Black (code formatter)
run_black() {
    echo "========== Running Black (Code Formatter) =========="
    black --check "${DIRECTORIES[@]}" | tee "$REPORT_DIR/black_report_$DATE_STAMP.txt"
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✅ Code formatting is consistent!"
    else
        echo "❌ Code formatting issues found."
        echo "Run 'black ${DIRECTORIES[*]}' to automatically format your code."
    fi
    echo
}

# Run Pylint (linter)
run_pylint() {
    echo "========== Running Pylint (Code Linter) =========="
    pylint --recursive=y "${DIRECTORIES[@]}" | tee "$REPORT_DIR/pylint_report_$DATE_STAMP.txt"
    echo
    echo "Full report saved to $REPORT_DIR/pylint_report_$DATE_STAMP.txt"
    echo
}

# Run MyPy (type checker)
run_mypy() {
    echo "========== Running MyPy (Type Checker) =========="
    mypy --ignore-missing-imports "${DIRECTORIES[@]}" | tee "$REPORT_DIR/mypy_report_$DATE_STAMP.txt"
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✅ No type issues found!"
    else
        echo "❌ Type checking issues found."
    fi
    echo "Full report saved to $REPORT_DIR/mypy_report_$DATE_STAMP.txt"
    echo
}

# Run Bandit (security checker)
run_bandit() {
    echo "========== Running Bandit (Security Checker) =========="
    bandit -r "${DIRECTORIES[@]}" -f txt | tee "$REPORT_DIR/bandit_report_$DATE_STAMP.txt"
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✅ No security issues found!"
    else
        echo "❌ Security issues found."
    fi
    echo "Full report saved to $REPORT_DIR/bandit_report_$DATE_STAMP.txt"
    echo
}

# Generate HTML summary report
generate_summary() {
    echo "Generating summary report..."

    HTML_REPORT="$REPORT_DIR/summary_report_$DATE_STAMP.html"

    cat > "$HTML_REPORT" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Code Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .section { margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }
        .pass { color: green; }
        .fail { color: red; }
        pre { background-color: #f5f5f5; padding: 10px; overflow: auto; }
    </style>
</head>
<body>
    <h1>Code Analysis Report (${DATE_STAMP})</h1>

    <div class="section">
        <h2>Summary</h2>
        <p>Directories analyzed: ${DIRECTORIES[*]}</p>
    </div>
EOF

    # Add Black results
    if [ -f "$REPORT_DIR/black_report_$DATE_STAMP.txt" ]; then
        BLACK_STATUS=$(grep -c "would reformat" "$REPORT_DIR/black_report_$DATE_STAMP.txt")
        if [ "$BLACK_STATUS" -gt 0 ]; then
            BLACK_CLASS="fail"
            BLACK_TEXT="Needs formatting"
        else
            BLACK_CLASS="pass"
            BLACK_TEXT="Properly formatted"
        fi

        cat >> "$HTML_REPORT" << EOF
    <div class="section">
        <h2>Code Formatting (Black)</h2>
        <p class="${BLACK_CLASS}">Status: ${BLACK_TEXT}</p>
        <pre>$(cat "$REPORT_DIR/black_report_$DATE_STAMP.txt")</pre>
    </div>
EOF
    fi

    # Add Pylint results
    if [ -f "$REPORT_DIR/pylint_report_$DATE_STAMP.txt" ]; then
        PYLINT_SCORE=$(grep -o "Your code has been rated at [-0-9.]*/10" "$REPORT_DIR/pylint_report_$DATE_STAMP.txt" | cut -d' ' -f6 | cut -d'/' -f1)

        if [ -z "$PYLINT_SCORE" ]; then
            PYLINT_CLASS="fail"
            PYLINT_TEXT="Analysis failed"
        elif (( $(echo "$PYLINT_SCORE >= 7.0" | bc -l) )); then
            PYLINT_CLASS="pass"
            PYLINT_TEXT="Score: $PYLINT_SCORE/10"
        else
            PYLINT_CLASS="fail"
            PYLINT_TEXT="Score: $PYLINT_SCORE/10"
        fi

        cat >> "$HTML_REPORT" << EOF
    <div class="section">
        <h2>Code Quality (Pylint)</h2>
        <p class="${PYLINT_CLASS}">Status: ${PYLINT_TEXT}</p>
        <pre>$(head -n 50 "$REPORT_DIR/pylint_report_$DATE_STAMP.txt")
...
See full report in $REPORT_DIR/pylint_report_$DATE_STAMP.txt</pre>
    </div>
EOF
    fi

    # Add MyPy results
    if [ -f "$REPORT_DIR/mypy_report_$DATE_STAMP.txt" ]; then
        MYPY_ISSUES=$(grep -c "error:" "$REPORT_DIR/mypy_report_$DATE_STAMP.txt")

        if [ "$MYPY_ISSUES" -gt 0 ]; then
            MYPY_CLASS="fail"
            MYPY_TEXT="$MYPY_ISSUES type issues found"
        else
            MYPY_CLASS="pass"
            MYPY_TEXT="No type issues"
        fi

        cat >> "$HTML_REPORT" << EOF
    <div class="section">
        <h2>Type Checking (MyPy)</h2>
        <p class="${MYPY_CLASS}">Status: ${MYPY_TEXT}</p>
        <pre>$(cat "$REPORT_DIR/mypy_report_$DATE_STAMP.txt")</pre>
    </div>
EOF
    fi

    # Add Bandit results
    if [ -f "$REPORT_DIR/bandit_report_$DATE_STAMP.txt" ]; then
        BANDIT_ISSUES=$(grep -c "Issue:" "$REPORT_DIR/bandit_report_$DATE_STAMP.txt")

        if [ "$BANDIT_ISSUES" -gt 0 ]; then
            BANDIT_CLASS="fail"
            BANDIT_TEXT="$BANDIT_ISSUES security issues found"
        else
            BANDIT_CLASS="pass"
            BANDIT_TEXT="No security issues"
        fi

        cat >> "$HTML_REPORT" << EOF
    <div class="section">
        <h2>Security Analysis (Bandit)</h2>
        <p class="${BANDIT_CLASS}">Status: ${BANDIT_TEXT}</p>
        <pre>$(cat "$REPORT_DIR/bandit_report_$DATE_STAMP.txt")</pre>
    </div>
EOF
    fi

    # Close HTML
    cat >> "$HTML_REPORT" << EOF
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            <li>Run <code>black ${DIRECTORIES[*]}</code> to automatically format your code.</li>
            <li>Address Pylint warnings to improve code quality.</li>
            <li>Add type hints to fix MyPy warnings for better type safety.</li>
            <li>Fix security issues identified by Bandit.</li>
        </ul>
    </div>
</body>
</html>
EOF

    echo "Summary report generated: $HTML_REPORT"
}

# Run tools based on flags
if [ "$FORMAT_ONLY" = true ]; then
    run_black
elif [ "$LINT_ONLY" = true ]; then
    run_pylint
elif [ "$TYPE_CHECK_ONLY" = true ]; then
    run_mypy
elif [ "$SECURITY_ONLY" = true ]; then
    run_bandit
else
    # Run all tools
    run_black
    run_pylint
    run_mypy
    run_bandit
    generate_summary

    echo "========== Analysis Complete =========="
    echo "All reports saved to $REPORT_DIR/"
    echo "Open $REPORT_DIR/summary_report_$DATE_STAMP.html to view a summary"
fi
