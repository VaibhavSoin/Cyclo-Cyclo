from flask import Flask, render_template, request
import subprocess
from typing import Dict, List, Tuple

app = Flask(__name__)

CLANG_TOOL_PATH = r"C:\Users\VAIBHAV SOIN\Desktop\llvm-project\build\bin\cyclomatic"
TEST_C_FILE = r"C:\Users\VAIBHAV SOIN\Desktop\tests\temp.c"

class ComplexityAnalyzer:
    def __init__(self):
        self.complexity_thresholds = {
            'low': (1, 4),
            'moderate': (5, 9),
            'high': (10, 14),
            'very_high': (15, float('inf'))
        }
    
    def get_optimization_strategies(self, complexity: int) -> List[str]:
        strategies = []
        if complexity >= 15:
            strategies.extend([
                "CRITICAL: This function needs immediate refactoring",
                "Break this function into 3-5 smaller functions",
                "Each new function should have a single responsibility",
                "Consider using design patterns (Strategy, State, Command)",
                "Implement comprehensive unit tests before refactoring"
            ])
        elif complexity >= 10:
            strategies.extend([
                "HIGH PRIORITY: Significant complexity reduction needed",
                "Extract complex logic into helper functions",
                "Reduce nesting depth using guard clauses",
                "Consider early returns to flatten control flow"
            ])
        elif complexity >= 5:
            strategies.extend([
                "MODERATE: Some optimization opportunities available",
                "Look for repeated code patterns to extract",
                "Simplify complex boolean expressions",
                "Consider using lookup tables for multiple conditions"
            ])
        else:
            strategies.extend([
                "GOOD: Function complexity is manageable",
                "Maintain current clean coding practices",
                "Consider adding inline documentation for algorithms"
            ])
        return strategies
    
    def calculate_maintainability_score(self, complexity: int) -> Tuple[int, str]:
        base_score = max(0, 100 - (complexity * 5))
        score = max(0, min(100, base_score))
        
        if score >= 80:
            grade = "A - Excellent"
        elif score >= 60:
            grade = "B - Good"
        elif score >= 40:
            grade = "C - Fair"
        elif score >= 20:
            grade = "D - Poor"
        else:
            grade = "F - Critical"
        
        return score, grade

def analyze_complexity(output: str, code: str) -> Dict:
    analyzer = ComplexityAnalyzer()
    
    functions_data = []
    total_functions = 0
    total_complexity = 0
    high_risk_functions = 0

    lines = output.splitlines()
    for line in lines:
        if "Results written to" in line:
            continue
        
        parts = line.strip().split()
        if len(parts) == 2:
            func_name, complexity_str = parts
            try:
                complexity = int(complexity_str)
                total_functions += 1
                total_complexity += complexity
                
                if complexity >= 10:
                    high_risk_functions += 1

                strategies = analyzer.get_optimization_strategies(complexity)
                maintainability_score, grade = analyzer.calculate_maintainability_score(complexity)

                if complexity >= 15:
                    risk_level = "CRITICAL"
                    risk_class = "critical"
                elif complexity >= 10:
                    risk_level = "HIGH"
                    risk_class = "high"
                elif complexity >= 5:
                    risk_level = "MODERATE"
                    risk_class = "moderate"
                else:
                    risk_level = "LOW"
                    risk_class = "low"
                
                function_data = {
                    'name': func_name,
                    'complexity': complexity,
                    'risk_level': risk_level,
                    'risk_class': risk_class,
                    'maintainability_score': maintainability_score,
                    'grade': grade,
                    'strategies': strategies
                }
                
                functions_data.append(function_data)
            except ValueError:
                continue
    
    summary = None
    if total_functions > 0:
        avg_complexity = total_complexity / total_functions
        overall_risk = "HIGH" if avg_complexity >= 10 else "MODERATE" if avg_complexity >= 5 else "LOW"
        
        summary = {
            'total_functions': total_functions,
            'avg_complexity': round(avg_complexity, 1),
            'high_risk_functions': high_risk_functions,
            'overall_risk': overall_risk,
            'total_complexity': total_complexity,
            'max_complexity': max([f['complexity'] for f in functions_data]) if functions_data else 0
        }

    return {'functions': functions_data, 'summary': summary}

@app.route('/', methods=['GET', 'POST'])
def index():
    output = ""
    analysis_data = None

    if request.method == 'POST':
        code = request.form['code']
        
        with open(TEST_C_FILE, 'w') as f:
            f.write(code)
        
        try:
            result = subprocess.run([CLANG_TOOL_PATH, TEST_C_FILE], capture_output=True, text=True)
            output = result.stdout or result.stderr
            analysis_data = analyze_complexity(output, code)
        except Exception as e:
            output = f"Error: {e}"
    
    return render_template('index.html', 
                           output=output, 
                           analysis_data=analysis_data)

if __name__ == '__main__':
    app.run(debug=True)
