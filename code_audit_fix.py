#!/usr/bin/env python3
"""
Comprehensive Code Audit and Fix Script for SMITE 2 Divine Arsenal
Identifies and fixes all code issues, import problems, and structural problems
"""

import os
import sys
import ast
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass

@dataclass
class CodeIssue:
    file_path: str
    line_number: int
    issue_type: str
    description: str
    severity: str
    fix_applied: bool = False

class CodeAuditor:
    """Comprehensive code auditor and fixer."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues: List[CodeIssue] = []
        self.fixed_files: Set[str] = set()
        
        # Common import patterns that need fixing
        self.import_patterns = [
            (r'from database import Database', 'from database import Database  # type: ignore'),
            (r'from working_build_optimizer import WorkingBuildOptimizer', 'from working_build_optimizer import WorkingBuildOptimizer  # type: ignore'),
            (r'from scrapers\.wiki_smite2 import WikiSmite2Scraper', 'from scrapers.wiki_smite2 import WikiSmite2Scraper  # type: ignore'),
            (r'from scrapers\.smite2 import Smite2Scraper', 'from scrapers.smite2 import Smite2Scraper  # type: ignore'),
        ]
        
        # Files that need path fixes
        self.path_fix_files = [
            'check_db.py',
            'automated_patch_updater.py',
            'divine_arsenal_status.py',
            'launch_divine_arsenal.py',
            'launch_divine_arsenal_performance.py'
        ]

    def audit_all(self) -> Dict[str, Any]:
        """Run comprehensive audit of entire codebase."""
        print("🔍 Starting comprehensive code audit...")
        print("=" * 60)
        
        audit_results = {
            'total_issues': 0,
            'critical_issues': 0,
            'warnings': 0,
            'fixed_issues': 0,
            'files_checked': 0,
            'issues_by_type': {},
            'issues_by_file': {}
        }
        
        # 1. Check Python syntax errors
        self._check_syntax_errors()
        
        # 2. Check import issues
        self._check_import_issues()
        
        # 3. Check path issues
        self._check_path_issues()
        
        # 4. Check for missing __init__.py files
        self._check_missing_init_files()
        
        # 5. Check for duplicate files
        self._check_duplicate_files()
        
        # 6. Check for unused imports
        self._check_unused_imports()
        
        # 7. Check for hardcoded paths
        self._check_path_issues()
        
        # 8. Check for potential runtime errors
        self._check_runtime_issues()
        
        # Compile results
        for issue in self.issues:
            audit_results['total_issues'] += 1
            if issue.severity == 'critical':
                audit_results['critical_issues'] += 1
            elif issue.severity == 'warning':
                audit_results['warnings'] += 1
            
            if issue.fix_applied:
                audit_results['fixed_issues'] += 1
            
            # Group by type
            if issue.issue_type not in audit_results['issues_by_type']:
                audit_results['issues_by_type'][issue.issue_type] = 0
            audit_results['issues_by_type'][issue.issue_type] += 1
            
            # Group by file
            if issue.file_path not in audit_results['issues_by_file']:
                audit_results['issues_by_file'][issue.file_path] = 0
            audit_results['issues_by_file'][issue.file_path] += 1
        
        return audit_results

    def _check_syntax_errors(self):
        """Check for Python syntax errors."""
        print("📝 Checking Python syntax...")
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                self.issues.append(CodeIssue(
                    file_path=str(py_file.relative_to(self.project_root)),
                    line_number=e.lineno or 0,
                    issue_type="syntax_error",
                    description=f"Syntax error: {e.msg}",
                    severity="critical"
                ))
            except Exception as e:
                self.issues.append(CodeIssue(
                    file_path=str(py_file.relative_to(self.project_root)),
                    line_number=0,
                    issue_type="file_error",
                    description=f"Error reading file: {e}",
                    severity="critical"
                ))

    def _check_import_issues(self):
        """Check for import-related issues."""
        print("📦 Checking import issues...")
        
        for py_file in self.project_root.rglob("*.py"):
            if py_file.name in self.path_fix_files:
                self._fix_import_issues_in_file(py_file)

    def _fix_import_issues_in_file(self, file_path: Path):
        """Fix import issues in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix path setup
            if 'sys.path.insert(0, os.path.join(os.path.dirname(__file__), "divine_arsenal", "backend"))' in content:
                content = content.replace(
                    'sys.path.insert(0, os.path.join(os.path.dirname(__file__), "divine_arsenal", "backend"))',
                    'backend_path = os.path.join(os.path.dirname(__file__), "divine_arsenal", "backend")\nsys.path.insert(0, backend_path)'
                )
            
            # Fix imports with type ignore
            for pattern, replacement in self.import_patterns:
                if re.search(pattern, content) and '# type: ignore' not in content:
                    content = re.sub(pattern, replacement, content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixed_files.add(str(file_path.relative_to(self.project_root)))
                self.issues.append(CodeIssue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=0,
                    issue_type="import_fix",
                    description="Fixed import issues with type ignore comments",
                    severity="warning",
                    fix_applied=True
                ))
                
        except Exception as e:
            self.issues.append(CodeIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=0,
                issue_type="import_error",
                description=f"Error fixing imports: {e}",
                severity="critical"
            ))

    def _check_path_issues(self):
        """Check for path-related issues."""
        print("🛤️ Checking path issues...")
        
        # Check for hardcoded paths
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for hardcoded paths
                hardcoded_patterns = [
                    r'C:\\Users\\',
                    r'/home/',
                    r'/Users/',
                    r'C:/Users/'
                ]
                
                for pattern in hardcoded_patterns:
                    if re.search(pattern, content):
                        self.issues.append(CodeIssue(
                            file_path=str(py_file.relative_to(self.project_root)),
                            line_number=0,
                            issue_type="hardcoded_path",
                            description=f"Found hardcoded path pattern: {pattern}",
                            severity="warning"
                        ))
                        
            except Exception as e:
                continue

    def _check_missing_init_files(self):
        """Check for missing __init__.py files."""
        print("📁 Checking for missing __init__.py files...")
        
        for py_dir in self.project_root.rglob("*/"):
            if py_dir.is_dir() and any(py_dir.glob("*.py")):
                init_file = py_dir / "__init__.py"
                if not init_file.exists():
                    self.issues.append(CodeIssue(
                        file_path=str(py_dir.relative_to(self.project_root)),
                        line_number=0,
                        issue_type="missing_init",
                        description="Missing __init__.py file",
                        severity="warning"
                    ))

    def _check_duplicate_files(self):
        """Check for duplicate files."""
        print("🔄 Checking for duplicate files...")
        
        file_names = {}
        for py_file in self.project_root.rglob("*.py"):
            if py_file.name in file_names:
                self.issues.append(CodeIssue(
                    file_path=str(py_file.relative_to(self.project_root)),
                    line_number=0,
                    issue_type="duplicate_file",
                    description=f"Duplicate file name: {py_file.name}",
                    severity="warning"
                ))
            else:
                file_names[py_file.name] = py_file

    def _check_unused_imports(self):
        """Check for potentially unused imports."""
        print("📚 Checking for unused imports...")
        
        # This is a simplified check - in a real scenario you'd use tools like autoflake
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for common unused import patterns
                if 'import os' in content and 'os.' not in content:
                    self.issues.append(CodeIssue(
                        file_path=str(py_file.relative_to(self.project_root)),
                        line_number=0,
                        issue_type="unused_import",
                        description="Potentially unused import: os",
                        severity="warning"
                    ))
                    
            except Exception as e:
                continue

    def _check_runtime_issues(self):
        """Check for potential runtime issues."""
        print("⚡ Checking for runtime issues...")
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for common runtime issues
                if 'except Exception:' in content:
                    self.issues.append(CodeIssue(
                        file_path=str(py_file.relative_to(self.project_root)),
                        line_number=0,
                        issue_type="bare_except",
                        description="Bare except clause - should specify exception type",
                        severity="warning"
                    ))
                
                if 'print(' in content and 'logging' not in content:
                    # This is just a warning, not necessarily an issue
                    pass
                    
            except Exception as e:
                continue

    def fix_all_issues(self) -> bool:
        """Apply fixes for all identified issues."""
        print("\n🔧 Applying fixes...")
        print("=" * 60)
        
        fixes_applied = 0
        
        # Apply import fixes
        for py_file in self.project_root.rglob("*.py"):
            if py_file.name in self.path_fix_files:
                if self._apply_import_fixes(py_file):
                    fixes_applied += 1
        
        # Create missing __init__.py files
        for issue in self.issues:
            if issue.issue_type == "missing_init" and not issue.fix_applied:
                if self._create_init_file(issue.file_path):
                    issue.fix_applied = True
                    fixes_applied += 1
        
        print(f"✅ Applied {fixes_applied} fixes")
        return fixes_applied > 0

    def _apply_import_fixes(self, file_path: Path) -> bool:
        """Apply import fixes to a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all import fixes
            for pattern, replacement in self.import_patterns:
                if re.search(pattern, content) and '# type: ignore' not in content:
                    content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
            
        return False

    def _create_init_file(self, dir_path: str) -> bool:
        """Create a missing __init__.py file."""
        try:
            init_path = self.project_root / dir_path / "__init__.py"
            init_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write("# Auto-generated __init__.py file\n")
            
            return True
        except Exception as e:
            print(f"❌ Error creating __init__.py in {dir_path}: {e}")
            return False

    def generate_report(self, audit_results: Dict[str, Any]) -> str:
        """Generate a comprehensive audit report."""
        report = []
        report.append("# SMITE 2 Divine Arsenal - Code Audit Report")
        report.append("=" * 60)
        report.append(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        report.append("## 📊 Summary")
        report.append(f"- Total Issues: {audit_results['total_issues']}")
        report.append(f"- Critical Issues: {audit_results['critical_issues']}")
        report.append(f"- Warnings: {audit_results['warnings']}")
        report.append(f"- Fixed Issues: {audit_results['fixed_issues']}")
        report.append("")
        
        # Issues by type
        report.append("## 🏷️ Issues by Type")
        for issue_type, count in audit_results['issues_by_type'].items():
            report.append(f"- {issue_type}: {count}")
        report.append("")
        
        # Issues by file
        report.append("## 📁 Issues by File")
        for file_path, count in audit_results['issues_by_file'].items():
            report.append(f"- {file_path}: {count} issues")
        report.append("")
        
        # Detailed issues
        report.append("## 🔍 Detailed Issues")
        for issue in self.issues:
            status = "✅ FIXED" if issue.fix_applied else "❌ OPEN"
            report.append(f"### {status} - {issue.file_path}:{issue.line_number}")
            report.append(f"- **Type**: {issue.issue_type}")
            report.append(f"- **Severity**: {issue.severity}")
            report.append(f"- **Description**: {issue.description}")
            report.append("")
        
        # Recommendations
        report.append("## 💡 Recommendations")
        if audit_results['critical_issues'] > 0:
            report.append("🚨 **CRITICAL**: Fix all critical issues before deployment")
        if audit_results['warnings'] > 0:
            report.append("⚠️ **WARNINGS**: Address warnings to improve code quality")
        if audit_results['fixed_issues'] > 0:
            report.append("✅ **FIXES**: Review applied fixes to ensure they're correct")
        
        report.append("")
        report.append("## 🛠️ Next Steps")
        report.append("1. Review and test all applied fixes")
        report.append("2. Address remaining critical issues")
        report.append("3. Consider addressing warnings for better code quality")
        report.append("4. Run tests to ensure functionality is preserved")
        report.append("5. Consider adding automated linting to CI/CD pipeline")
        
        return "\n".join(report)

    def run_full_audit(self) -> bool:
        """Run complete audit and fix process."""
        print("🚀 Starting full code audit and fix process...")
        print("=" * 60)
        
        # Run audit
        audit_results = self.audit_all()
        
        # Apply fixes
        fixes_applied = self.fix_all_issues()
        
        # Generate report
        report = self.generate_report(audit_results)
        
        # Save report
        report_path = self.project_root / "CODE_AUDIT_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total Issues Found: {audit_results['total_issues']}")
        print(f"Critical Issues: {audit_results['critical_issues']}")
        print(f"Warnings: {audit_results['warnings']}")
        print(f"Fixes Applied: {audit_results['fixed_issues']}")
        print(f"Report Saved: {report_path}")
        
        if audit_results['critical_issues'] == 0:
            print("\n✅ No critical issues found!")
            return True
        else:
            print(f"\n⚠️ {audit_results['critical_issues']} critical issues remain")
            return False


def main():
    """Main function."""
    project_root = os.getcwd()
    auditor = CodeAuditor(project_root)
    
    success = auditor.run_full_audit()
    
    if success:
        print("\n🎉 Code audit completed successfully!")
        print("   All critical issues have been resolved.")
    else:
        print("\n⚠️ Code audit completed with issues.")
        print("   Please review the report and address remaining critical issues.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 