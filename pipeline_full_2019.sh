#!/bin/bash
#
# Nike 2019 SEC Filings Complete Pipeline Automation Script
#
# This script executes the complete 2019 SEC filings extraction and analysis pipeline
# as validated in the deployment reports. It runs all four processing stages in the
# correct dependency order and provides comprehensive logging and error handling.
#
# Pipeline Stages:
# 1. XLS Extraction - Processes Excel financial data supplements  
# 2. PDF Text Extraction - Extracts text from SEC filing PDFs
# 3. Keyword Sentinel Scan - Performs intelligent keyword analysis
# 4. Data Triangulation - Cross-references facility and operational data
#
# Usage:
#     chmod +x pipeline_full_2019.sh
#     ./pipeline_full_2019.sh
#

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Configuration
YEAR="2019"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${BASE_DIR}/pipeline_full_2019.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    echo -e "[$TIMESTAMP] [$level] $message" | tee -a "$LOG_FILE"
}

# Error handling function
error_exit() {
    log "ERROR" "$1"
    echo -e "${RED}❌ PIPELINE FAILED: $1${NC}"
    exit 1
}

# Success function
success() {
    log "SUCCESS" "$1"
    echo -e "${GREEN}✅ $1${NC}"
}

# Info function
info() {
    log "INFO" "$1"
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Warning function
warn() {
    log "WARN" "$1"
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python dependencies
check_dependencies() {
    info "Checking Python dependencies..."
    
    # Check Python version
    if ! command_exists python3; then
        error_exit "Python3 is not installed or not in PATH"
    fi
    
    # Check required Python packages
    local required_packages=("pandas" "openpyxl" "PyPDF2" "xlrd" "numpy")
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            warn "Missing Python package: $package"
            info "Installing missing dependencies..."
            pip install -r requirements.txt openpyxl PyPDF2 || error_exit "Failed to install dependencies"
            break
        fi
    done
    
    success "Dependencies check completed"
}

# Function to verify input data exists
check_input_data() {
    info "Verifying input data for year $YEAR..."
    
    local filings_dir="${BASE_DIR}/filings/${YEAR}"
    if [[ ! -d "$filings_dir" ]]; then
        error_exit "Filings directory not found: $filings_dir"
    fi
    
    # Check for required file types
    local pdf_count=$(find "$filings_dir" -name "*.pdf" | wc -l)
    local xls_count=$(find "$filings_dir" \( -name "*.xls" -o -name "*.xlsx" \) | wc -l)
    
    if [[ $pdf_count -eq 0 ]]; then
        error_exit "No PDF files found in $filings_dir"
    fi
    
    if [[ $xls_count -eq 0 ]]; then
        error_exit "No XLS/XLSX files found in $filings_dir"
    fi
    
    info "Found $pdf_count PDF files and $xls_count XLS/XLSX files"
    success "Input data verification completed"
}

# Function to run a pipeline stage
run_stage() {
    local stage_name="$1"
    local script_path="$2"
    local stage_number="$3"
    
    info "=========================================="
    info "STAGE $stage_number: $stage_name"
    info "=========================================="
    info "Executing: python3 $script_path --year $YEAR"
    
    local start_time=$(date +%s)
    
    # Run the script and capture output
    if python3 "$script_path" --year "$YEAR" 2>&1 | tee -a "$LOG_FILE"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        success "$stage_name completed successfully in ${duration}s"
        return 0
    else
        local exit_code=$?
        error_exit "$stage_name failed with exit code $exit_code"
    fi
}

# Function to validate output directories and files
validate_outputs() {
    info "Validating pipeline outputs..."
    
    local extracted_data_dir="${BASE_DIR}/extracted_data/${YEAR}"
    local analysis_results_dir="${BASE_DIR}/analysis_results/${YEAR}"
    
    # Check extracted data directory
    if [[ -d "$extracted_data_dir" ]]; then
        local extraction_files=$(find "$extracted_data_dir" -name "*.json" | wc -l)
        info "Found $extraction_files JSON extraction files"
    else
        warn "Extracted data directory not found: $extracted_data_dir"
    fi
    
    # Check analysis results directory  
    if [[ -d "$analysis_results_dir" ]]; then
        local analysis_files=$(find "$analysis_results_dir" -name "*.json" | wc -l)
        info "Found $analysis_files JSON analysis files"
    else
        warn "Analysis results directory not found: $analysis_results_dir"
    fi
    
    # Check for triangulation report
    local triangulation_reports=$(find "$BASE_DIR" -name "nike_triangulation_report_${YEAR}_*.json" | wc -l)
    if [[ $triangulation_reports -gt 0 ]]; then
        info "Found $triangulation_reports triangulation report(s)"
    else
        warn "No triangulation reports found"
    fi
    
    success "Output validation completed"
}

# Function to generate summary report
generate_summary() {
    info "=========================================="
    info "PIPELINE EXECUTION SUMMARY"
    info "=========================================="
    
    local total_end_time=$(date +%s)
    local total_duration=$((total_end_time - pipeline_start_time))
    
    info "Year: $YEAR"
    info "Total execution time: ${total_duration}s"
    info "Log file: $LOG_FILE"
    
    # Count output files
    local total_json_files=$(find "$BASE_DIR" -name "*.json" -path "*/extracted_data/${YEAR}/*" -o -path "*/analysis_results/${YEAR}/*" -o -name "nike_triangulation_report_${YEAR}_*.json" | wc -l)
    info "Total output files generated: $total_json_files"
    
    success "🎯 PIPELINE EXECUTION COMPLETED SUCCESSFULLY"
    info "All four stages of the 2019 SEC filings analysis pipeline have been executed:"
    info "✅ XLS Extraction - Financial data processing"
    info "✅ PDF Text Extraction - SEC document text analysis"  
    info "✅ Keyword Sentinel Scan - Intelligent keyword analysis"
    info "✅ Data Triangulation - Facility and operational cross-reference"
    info ""
    info "The pipeline is ready for production use and outputs can be used for further analysis."
}

# Main execution function
main() {
    # Initialize log file
    echo "Nike 2019 SEC Filings Pipeline Execution Log" > "$LOG_FILE"
    echo "Started: $TIMESTAMP" >> "$LOG_FILE"
    echo "========================================" >> "$LOG_FILE"
    
    info "🚀 Starting Nike 2019 SEC Filings Complete Analysis Pipeline"
    info "Base directory: $BASE_DIR"
    info "Year: $YEAR"
    info "Log file: $LOG_FILE"
    
    # Record start time
    pipeline_start_time=$(date +%s)
    
    # Pre-flight checks
    check_dependencies
    check_input_data
    
    # Execute pipeline stages in dependency order
    run_stage "XLS Extraction" "${BASE_DIR}/scripts/xls_extractor.py" "1"
    run_stage "PDF Text Extraction" "${BASE_DIR}/scripts/pdf_extractor.py" "2"
    run_stage "Keyword Sentinel Scan" "${BASE_DIR}/scripts/keyword_sentinel.py" "3"
    run_stage "Data Triangulation" "${BASE_DIR}/scripts/triangulator_auto_executor.py" "4"
    
    # Post-execution validation
    validate_outputs
    
    # Generate final summary
    generate_summary
}

# Help function
show_help() {
    echo "Nike 2019 SEC Filings Complete Pipeline Automation Script"
    echo ""
    echo "This script executes the complete 2019 SEC filings extraction and analysis pipeline"
    echo "as validated in the deployment reports. It runs all four processing stages in the"
    echo "correct dependency order and provides comprehensive logging and error handling."
    echo ""
    echo "Pipeline Stages:"
    echo "  1. XLS Extraction - Processes Excel financial data supplements"
    echo "  2. PDF Text Extraction - Extracts text from SEC filing PDFs"
    echo "  3. Keyword Sentinel Scan - Performs intelligent keyword analysis"
    echo "  4. Data Triangulation - Cross-references facility and operational data"
    echo ""
    echo "Usage:"
    echo "  ./pipeline_full_2019.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message and exit"
    echo ""
    echo "Output:"
    echo "  - extracted_data/2019/      Individual file extractions and summaries"
    echo "  - analysis_results/2019/    Keyword analysis results"
    echo "  - nike_triangulation_report_2019_*.json  Comprehensive facility analysis"
    echo "  - pipeline_full_2019.log   Execution log file"
    echo ""
    echo "Requirements:"
    echo "  - Python 3.x with required packages (pandas, openpyxl, PyPDF2, etc.)"
    echo "  - Input data in filings/2019/ directory (PDF and XLS/XLSX files)"
    echo ""
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information."
                exit 1
                ;;
        esac
    done
    
    main "$@"
fi