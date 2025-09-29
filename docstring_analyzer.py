"""Docstring Analysis Tool for RxFlow Pharmacy Assistant"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class DocstringAnalyzer:
    """Analyzes Python files for docstring completeness and quality"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analysis_results = []
        
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze docstrings in a single Python file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            file_analysis = {
                'file': str(file_path.relative_to(self.project_root)),
                'classes': [],
                'functions': [],
                'module_docstring': ast.get_docstring(tree),
                'issues': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node)
                    file_analysis['classes'].append(class_info)
                elif isinstance(node, ast.FunctionDef) and not self._is_method(node, tree):
                    func_info = self._analyze_function(node)
                    file_analysis['functions'].append(func_info)
            
            return file_analysis
            
        except Exception as e:
            return {
                'file': str(file_path.relative_to(self.project_root)),
                'error': str(e),
                'classes': [],
                'functions': [],
                'module_docstring': None,
                'issues': [f"Failed to parse: {str(e)}"]
            }
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze a class and its methods for docstring quality"""
        
        class_docstring = ast.get_docstring(node)
        methods = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._analyze_function(item, is_method=True)
                methods.append(method_info)
        
        return {
            'name': node.name,
            'line': node.lineno,
            'docstring': class_docstring,
            'docstring_quality': self._assess_docstring_quality(class_docstring, 'class'),
            'methods': methods,
            'inheritance': [base.id for base in node.bases if isinstance(base, ast.Name)]
        }
    
    def _analyze_function(self, node: ast.FunctionDef, is_method: bool = False) -> Dict[str, Any]:
        """Analyze a function or method for docstring quality"""
        
        func_docstring = ast.get_docstring(node)
        
        # Get parameter info
        params = []
        for arg in node.args.args:
            if arg.arg not in ['self', 'cls']:
                params.append({
                    'name': arg.arg,
                    'annotation': ast.unparse(arg.annotation) if arg.annotation else None
                })
        
        # Get return annotation
        return_annotation = ast.unparse(node.returns) if node.returns else None
        
        return {
            'name': node.name,
            'line': node.lineno,
            'is_method': is_method,
            'is_private': node.name.startswith('_'),
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'docstring': func_docstring,
            'docstring_quality': self._assess_docstring_quality(func_docstring, 'function'),
            'parameters': params,
            'return_annotation': return_annotation,
            'decorators': [ast.unparse(dec) for dec in node.decorator_list]
        }
    
    def _is_method(self, node: ast.FunctionDef, tree: ast.Module) -> bool:
        """Check if a function is a method inside a class"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                if node in parent.body:
                    return True
        return False
    
    def _assess_docstring_quality(self, docstring: Optional[str], item_type: str) -> Dict[str, Any]:
        """Assess the quality and completeness of a docstring"""
        
        if not docstring:
            return {
                'score': 0,
                'issues': ['Missing docstring'],
                'has_description': False,
                'has_parameters': False,
                'has_returns': False,
                'has_examples': False,
                'has_raises': False
            }
        
        issues = []
        has_description = len(docstring.strip()) > 10
        has_parameters = 'Args:' in docstring or 'Parameters:' in docstring or 'param' in docstring.lower()
        has_returns = 'Returns:' in docstring or 'return' in docstring.lower()
        has_examples = 'Example:' in docstring or 'Examples:' in docstring
        has_raises = 'Raises:' in docstring or 'raise' in docstring.lower()
        
        # Calculate score
        score = 0
        if has_description:
            score += 40
        if has_parameters:
            score += 20
        if has_returns:
            score += 20
        if has_examples:
            score += 10
        if has_raises:
            score += 10
        
        # Identify issues
        if len(docstring.strip()) < 20:
            issues.append('Docstring too short')
        if not has_description:
            issues.append('Missing description')
        if item_type == 'function' and not has_parameters:
            issues.append('Missing parameter documentation')
        if item_type == 'function' and not has_returns:
            issues.append('Missing return documentation')
        
        return {
            'score': score,
            'issues': issues,
            'has_description': has_description,
            'has_parameters': has_parameters,
            'has_returns': has_returns,
            'has_examples': has_examples,
            'has_raises': has_raises
        }
    
    def scan_project(self) -> Dict[str, Any]:
        """Scan entire project for docstring analysis"""
        
        python_files = list(self.project_root.rglob("*.py"))
        results = []
        stats = {
            'total_files': 0,
            'total_classes': 0,
            'total_functions': 0,
            'classes_with_docstrings': 0,
            'functions_with_docstrings': 0,
            'avg_docstring_score': 0.0
        }
        
        total_score = 0
        total_items = 0
        
        for py_file in python_files:
            # Skip __pycache__ and .git directories
            if '__pycache__' in str(py_file) or '.git' in str(py_file):
                continue
                
            result = self.analyze_file(py_file)
            results.append(result)
            
            stats['total_files'] += 1
            
            # Count classes and functions
            for cls in result.get('classes', []):
                stats['total_classes'] += 1
                if cls['docstring']:
                    stats['classes_with_docstrings'] += 1
                total_score += cls['docstring_quality']['score']
                total_items += 1
                
                for method in cls.get('methods', []):
                    stats['total_functions'] += 1
                    if method['docstring']:
                        stats['functions_with_docstrings'] += 1
                    total_score += method['docstring_quality']['score']
                    total_items += 1
            
            for func in result.get('functions', []):
                stats['total_functions'] += 1
                if func['docstring']:
                    stats['functions_with_docstrings'] += 1
                total_score += func['docstring_quality']['score']
                total_items += 1
        
        stats['avg_docstring_score'] = total_score / total_items if total_items > 0 else 0.0
        
        return {
            'files': results,
            'statistics': stats,
            'recommendations': self._generate_recommendations(stats)
        }
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving documentation"""
        
        recommendations = []
        
        class_coverage = (stats['classes_with_docstrings'] / stats['total_classes'] * 100) if stats['total_classes'] > 0 else 0
        func_coverage = (stats['functions_with_docstrings'] / stats['total_functions'] * 100) if stats['total_functions'] > 0 else 0
        
        if class_coverage < 90:
            recommendations.append(f"Improve class docstring coverage from {class_coverage:.1f}% to 90%+")
        
        if func_coverage < 80:
            recommendations.append(f"Improve function docstring coverage from {func_coverage:.1f}% to 80%+")
        
        if stats['avg_docstring_score'] < 70:
            recommendations.append(f"Improve docstring quality score from {stats['avg_docstring_score']:.1f} to 70+")
        
        recommendations.extend([
            "Add comprehensive parameter descriptions with types",
            "Include return value documentation with types",
            "Add usage examples for complex functions",
            "Document exceptions that may be raised",
            "Use consistent docstring style (Google or NumPy format)",
            "Include cross-references to related functions/classes"
        ])
        
        return recommendations


def main() -> None:
    """
    Execute comprehensive docstring analysis for the RxFlow project.
    
    Analyzes all Python files in the project directory to assess docstring
    quality and coverage, generating detailed reports and recommendations.
    
    Returns:
        None: Prints analysis results to stdout and generates reports
        
    Side Effects:
        - Prints documentation statistics to console
        - Displays files needing enhancement
        - Shows quality recommendations
        - Assigns documentation grade based on analysis
    """
    
    project_root = "/home/alireza/projects/rxflow_pharmacy_assistant"
    
    print("🔍 RxFlow Docstring Analyzer - Analyzing documentation...")
    print("=" * 60)
    
    analyzer = DocstringAnalyzer(project_root)
    results = analyzer.scan_project()
    
    # Print statistics
    stats = results['statistics']
    print(f"\n📊 DOCUMENTATION ANALYSIS:")
    print(f"Files Analyzed: {stats['total_files']}")
    print(f"Classes Found: {stats['total_classes']}")
    print(f"Functions/Methods: {stats['total_functions']}")
    print(f"Class Docstring Coverage: {stats['classes_with_docstrings']}/{stats['total_classes']} ({stats['classes_with_docstrings']/stats['total_classes']*100:.1f}%)" if stats['total_classes'] > 0 else "Class Docstring Coverage: N/A")
    print(f"Function Docstring Coverage: {stats['functions_with_docstrings']}/{stats['total_functions']} ({stats['functions_with_docstrings']/stats['total_functions']*100:.1f}%)" if stats['total_functions'] > 0 else "Function Docstring Coverage: N/A")
    print(f"Average Docstring Quality Score: {stats['avg_docstring_score']:.1f}/100")
    
    # Print files with low documentation
    print(f"\n⚠️  FILES NEEDING DOCUMENTATION ENHANCEMENT:")
    print("=" * 50)
    
    for file_result in results['files']:
        if 'error' in file_result:
            continue
            
        issues = []
        
        # Check module docstring
        if not file_result['module_docstring']:
            issues.append("Missing module docstring")
        
        # Check classes
        for cls in file_result['classes']:
            if cls['docstring_quality']['score'] < 70:
                issues.append(f"Class '{cls['name']}' needs better documentation (score: {cls['docstring_quality']['score']})")
        
        # Check functions
        for func in file_result['functions']:
            if func['docstring_quality']['score'] < 70:
                issues.append(f"Function '{func['name']}' needs better documentation (score: {func['docstring_quality']['score']})")
        
        if issues:
            print(f"\n📄 {file_result['file']}:")
            for issue in issues[:3]:  # Show top 3 issues
                print(f"  - {issue}")
            if len(issues) > 3:
                print(f"  ... and {len(issues) - 3} more issues")
    
    # Print recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("=" * 30)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")
    
    # Grade the documentation
    avg_score = stats['avg_docstring_score']
    if avg_score >= 90:
        grade = "A+"
        color = "🟢"
    elif avg_score >= 80:
        grade = "A"
        color = "🟢"
    elif avg_score >= 70:
        grade = "B"
        color = "🟡"
    elif avg_score >= 60:
        grade = "C"
        color = "🟡"
    else:
        grade = "F"
        color = "🔴"
    
    print(f"\n🎯 DOCUMENTATION GRADE: {color} {grade}")
    print(f"Average Score: {avg_score:.1f}/100")
    print("=" * 60)


if __name__ == "__main__":
    main()