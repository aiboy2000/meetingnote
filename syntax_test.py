"""
语法检查测试 - 依赖包检查版本
"""

import sys
import ast
import os

def check_syntax(file_path):
    """检查Python文件的语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 解析语法
        ast.parse(source)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """主测试函数"""
    print("构建语法检查测试")
    print("=" * 40)
    
    # 检查的文件列表
    files_to_check = [
        "src/term_extractor.py",
        "src/vector_db.py", 
        "src/transcriber.py",
        "src/minutes_generator.py",
        "src/tagger.py",
        "main.py",
        "quick_test.py"
    ]
    
    all_passed = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            passed, message = check_syntax(file_path)
            status = "✓" if passed else "✗"
            print(f"{status} {file_path}: {message}")
            if not passed:
                all_passed = False
        else:
            print(f"✗ {file_path}: File not found")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ すべてのファイルの構文チェックが成功しました！")
    else:
        print("✗ 一部のファイルで構文エラーがあります。")
    
    return all_passed

if __name__ == "__main__":
    main()