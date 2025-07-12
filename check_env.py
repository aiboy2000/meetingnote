"""
環境チェックスクリプト
Gradioとその他の依存関係をチェック
"""

import sys
import subprocess

def check_python_version():
    """Pythonバージョンをチェック"""
    version = sys.version_info
    print(f"🐍 Python: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("   ✅ サポートされているバージョンです")
    else:
        print("   ❌ Python 3.8以上が必要です")
    print()

def check_package(package_name):
    """パッケージの存在とバージョンをチェック"""
    try:
        module = __import__(package_name.replace('-', '_'))
        version = getattr(module, '__version__', 'unknown')
        print(f"📦 {package_name}: {version}")
        return True, version
    except ImportError:
        print(f"❌ {package_name}: インストールされていません")
        return False, None

def check_gradio_compatibility():
    """Gradioの互換性をチェック"""
    print("🔍 Gradio互換性チェック:")
    
    try:
        import gradio as gr
        version = gr.__version__
        print(f"   現在のバージョン: {version}")
        
        # バージョン番号を解析
        major, minor = map(int, version.split('.')[:2])
        
        if major >= 4:
            print("   ✅ 新しいバージョンです（推奨）")
            compatibility = "good"
        elif major == 3 and minor >= 40:
            print("   ⚠️  古いですが動作する可能性があります")
            compatibility = "fair"
        else:
            print("   ❌ 古すぎる可能性があります")
            compatibility = "poor"
        
        return compatibility
        
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return "error"

def suggest_fixes(gradio_compatibility):
    """修正案を提案"""
    print("\n🔧 推奨アクション:")
    
    if gradio_compatibility == "poor" or gradio_compatibility == "error":
        print("1. Gradioを最新版に更新:")
        print("   pip install --upgrade gradio")
        print()
        
    print("2. 仮想環境を新規作成（推奨）:")
    print("   python -m venv meetingnote_env")
    print("   meetingnote_env\\Scripts\\activate  # Windows")
    print("   pip install gradio")
    print()
    
    print("3. 起動方法:")
    if gradio_compatibility in ["good", "fair"]:
        print("   python minimal_app.py  # 最小版（推奨）")
        print("   python simple_app.py   # シンプル版")
    else:
        print("   python minimal_app.py  # 最小版のみ試行")

def install_gradio():
    """Gradioのインストールを試行"""
    print("📥 Gradioのインストールを試行中...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "gradio"])
        print("✅ Gradioのインストール/アップデートが完了しました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ インストールに失敗しました: {e}")
        return False

def main():
    """メインチェック"""
    print("=" * 60)
    print("🏗️ 建築会議転写システム - 環境チェック")
    print("=" * 60)
    print()
    
    # Python版本检查
    check_python_version()
    
    # 包检查
    print("📦 インストール済みパッケージ:")
    packages = ["gradio", "json", "pathlib"]
    
    gradio_installed = False
    for package in packages:
        if package == "gradio":
            installed, version = check_package(package)
            gradio_installed = installed
        else:
            check_package(package)
    
    print()
    
    # Gradio兼容性检查
    if gradio_installed:
        compatibility = check_gradio_compatibility()
    else:
        print("❌ Gradioがインストールされていません")
        compatibility = "error"
        
        print("\nGradioをインストールしますか？ (y/n): ", end="")
        choice = input().lower()
        if choice == 'y':
            if install_gradio():
                compatibility = check_gradio_compatibility()
    
    print()
    suggest_fixes(compatibility)
    
    print("\n" + "=" * 60)
    print("✨ 環境チェック完了")
    
    if compatibility in ["good", "fair"]:
        print("🚀 minimal_app.py を実行して開始してください!")
    else:
        print("🔧 上記の修正案を試してからもう一度実行してください")

if __name__ == "__main__":
    main()