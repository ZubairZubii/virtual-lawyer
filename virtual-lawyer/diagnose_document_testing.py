"""
Diagnostic script to identify issues with document testing
Run this BEFORE running the test script
"""
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    print("=" * 60)
    print("CHECKING DEPENDENCIES")
    print("=" * 60)
    
    required_packages = {
        'requests': 'requests',
        'json': 'json (built-in)',
        'pathlib': 'pathlib (built-in)',
    }
    
    missing = []
    for module, name in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - MISSING")
            missing.append(name)
    
    optional_packages = {
        'docx': 'python-docx (optional)',
        'docxtpl': 'python-docxtpl (optional)',
        'fitz': 'PyMuPDF (optional)',
        'pdfplumber': 'pdfplumber (optional)',
    }
    
    print("\nOptional packages:")
    for module, name in optional_packages.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"⚠️  {name} - Not installed (optional)")
    
    return len(missing) == 0

def check_files():
    """Check if required files exist"""
    print("\n" + "=" * 60)
    print("CHECKING FILES")
    print("=" * 60)
    
    files_to_check = [
        ('test_document_features.py', 'Test script'),
        ('api_complete.py', 'API server script'),
        ('test_document.pdf', 'Test document (optional)'),
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"⚠️  {description}: {file_path} - NOT FOUND")
            if file_path != 'test_document.pdf':
                all_exist = False
    
    return all_exist

def check_api_server():
    """Check if API server is running"""
    print("\n" + "=" * 60)
    print("CHECKING API SERVER")
    print("=" * 60)
    
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=3)
        print("✅ API server is running on http://localhost:8000")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ API server is NOT running")
        print("   Start it with: python api_complete.py")
        return False
    except requests.exceptions.Timeout:
        print("⚠️  API server timed out (may be slow or not responding)")
        return False
    except ImportError:
        print("⚠️  Cannot check API - requests module not installed")
        return None
    except Exception as e:
        print(f"⚠️  Error checking API: {e}")
        return False

def check_system_resources():
    """Check system resources"""
    print("\n" + "=" * 60)
    print("SYSTEM INFORMATION")
    print("=" * 60)
    
    import platform
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version.split()[0]}")
    
    try:
        import psutil
        mem = psutil.virtual_memory()
        print(f"Available Memory: {mem.available / (1024**3):.2f} GB")
        print(f"Memory Usage: {mem.percent}%")
        
        if mem.percent > 90:
            print("⚠️  WARNING: High memory usage - system may be slow")
    except ImportError:
        print("⚠️  psutil not installed - cannot check memory")

def main():
    """Run all diagnostics"""
    print("=" * 60)
    print("DOCUMENT TESTING DIAGNOSTICS")
    print("=" * 60)
    print("\nThis script will check your system for potential issues")
    print("before running document feature tests.\n")
    
    issues = []
    
    # Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        issues.append("Missing required dependencies")
    
    # Check files
    files_ok = check_files()
    if not files_ok:
        issues.append("Missing required files")
    
    # Check API
    api_status = check_api_server()
    
    # Check system
    check_system_resources()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n⚠️  Fix these issues before running tests")
    else:
        print("✅ Basic checks passed")
    
    if api_status is False:
        print("\n⚠️  IMPORTANT: API server is not running")
        print("   Start it with: python api_complete.py")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    print("1. If system was freezing, use: python test_document_features_safe.py")
    print("2. Make sure API server is running before testing")
    print("3. Close other heavy applications to free memory")
    print("4. If issues persist, check API server logs")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error running diagnostics: {e}")
        import traceback
        traceback.print_exc()








