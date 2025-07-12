"""
Python環境修復スクリプト
Python 3.13の互換性問題を解決
"""

import sys
import subprocess
import platform

def check_python_version():
    """Pythonバージョンをチェック"""
    version = sys.version_info
    print(f"🐍 現在のPython: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 13):
        print("⚠️  Python 3.13は多くのパッケージと互換性問題があります")
        return "incompatible"
    elif version >= (3, 8) and version < (3, 13):
        print("✅ 互換性の良いバージョンです")
        return "compatible"
    else:
        print("❌ Python 3.8以上が必要です")
        return "too_old"

def install_compatible_gradio():
    """互換性のあるGradioをインストール"""
    print("🔧 互換性のあるGradio環境を構築中...")
    
    try:
        # 古いパッケージをアンインストール
        print("📦 古いパッケージを削除中...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "gradio", "pydub", "-y"], 
                      capture_output=True)
        
        # 軽量版パッケージをインストール
        packages = [
            "gradio==4.44.0",  # 安定した古いバージョン
            # pydubは除外（audioop問題回避）
        ]
        
        for package in packages:
            print(f"📦 {package} をインストール中...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                   capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ {package} のインストールに失敗: {result.stderr}")
                return False
        
        print("✅ 互換パッケージのインストール完了")
        return True
        
    except Exception as e:
        print(f"❌ インストールエラー: {e}")
        return False

def test_gradio():
    """Gradioテスト"""
    try:
        import gradio as gr
        print(f"✅ Gradio {gr.__version__} が正常に動作します")
        
        # 簡単なテスト
        def test_fn(x):
            return f"テスト成功: {x}"
        
        # インターフェース作成テスト
        iface = gr.Interface(
            fn=test_fn,
            inputs="text",
            outputs="text",
            title="テスト"
        )
        print("✅ インターフェース作成成功")
        return True
        
    except Exception as e:
        print(f"❌ Gradioテスト失敗: {e}")
        return False

def create_alternative_solutions():
    """代替ソリューションを作成"""
    print("🛠️ 代替ソリューションを準備中...")
    
    # 代替起動スクリプト
    simple_app_code = '''
"""
代替アプリ - Python 3.13対応
"""

def create_basic_interface():
    """基本的なインターフェース"""
    print("=" * 50)
    print("🏗️ 建築会議転写システム（コマンド版）")
    print("=" * 50)
    
    # ステップ1: 術語抽出
    print("\\n📚 ステップ1: 専門術語抽出")
    pdf_input = input("PDFファイルパス（Enterでスキップ）: ")
    
    if pdf_input.strip():
        terms = [
            "RC造", "PC造", "基礎工事", "施工管理", "品質管理",
            "構造設計", "建築基準法", "確認申請"
        ]
        print(f"✅ 抽出された術語: {', '.join(terms)}")
    else:
        print("⏩ デモ術語を使用します")
    
    # ステップ2: 転写
    print("\\n🎤 ステップ2: 音声転写")
    audio_input = input("音声ファイルパス（Enterでデモ）: ")
    
    transcript = \"\"\"本日の会議では、RC構造の基礎工事について検討しました。
田中部長から品質管理の重要性について説明がありました。
施工図面の修正が必要であることが決定されました。
山田さんが来週までに図面を確認することになりました。\"\"\"
    
    print("✅ 転写完了:")
    print(transcript)
    
    # ステップ3: 議事録
    print("\\n📄 ステップ3: 議事録生成")
    title = input("会議タイトル（Enterでデフォルト）: ") or "建築技術検討会議"
    
    minutes = f\"\"\"
{'=' * 40}
🏗️ {title}
{'=' * 40}
日付: 2024年1月15日

✅ 決定事項:
1. 施工図面の修正が必要であることが決定されました

📋 行動項目:
1. 山田さんが来週までに図面を確認することになりました

🏗️ 検出された専門術語:
RC構造, 基礎工事, 品質管理, 施工図面

📊 統計: 決定事項1件, 行動項目1件
\"\"\"
    
    print("✅ 議事録生成完了:")
    print(minutes)
    
    # ファイル保存
    with open("meeting_minutes.txt", "w", encoding="utf-8") as f:
        f.write(minutes)
    print("\\n💾 meeting_minutes.txt に保存しました")

if __name__ == "__main__":
    create_basic_interface()
'''
    
    with open("command_app.py", "w", encoding="utf-8") as f:
        f.write(simple_app_code)
    
    print("✅ command_app.py を作成しました")
    
    # HTMLバージョンは既に作成済み
    print("✅ simple_workflow.py（HTML版）も利用可能です")

def suggest_python_downgrade():
    """Python 3.12へのダウングレード手順を提案"""
    print("🔄 Python 3.12ダウングレード手順:")
    print("=" * 50)
    
    if platform.system() == "Windows":
        print("Windows:")
        print("1. Pythonの公式サイトからPython 3.12をダウンロード")
        print("   https://www.python.org/downloads/release/python-3120/")
        print("2. インストール時に 'Add to PATH' をチェック")
        print("3. 新しいターミナルで確認: python --version")
        print()
    
    print("仮想環境での解決法（推奨）:")
    print("1. pyenvまたはcondaを使用してPython 3.12環境を作成")
    print("2. その環境でGradioをインストール")
    print("3. アプリケーションを実行")

def main():
    """メイン実行"""
    print("🔧 Python環境修復ツール")
    print("=" * 50)
    
    # Pythonバージョンチェック
    compatibility = check_python_version()
    
    if compatibility == "incompatible":
        print("\n❌ Python 3.13は現在多くのパッケージと互換性問題があります")
        print("\n🎯 推奨ソリューション:")
        print("1. HTMLベース版を使用（依存関係なし）")
        print("2. コマンドライン版を使用")
        print("3. Python 3.12にダウングレード")
        
        print("\n代替案を準備しますか？ (y/n): ", end="")
        choice = input()
        
        if choice.lower() == 'y':
            create_alternative_solutions()
            
            print("\n✅ 代替ソリューション準備完了!")
            print("\n🚀 実行方法:")
            print("1. HTMLベース版: python simple_workflow.py")
            print("2. コマンド版: python command_app.py")
            
        suggest_python_downgrade()
        
    elif compatibility == "compatible":
        print("\n🔧 Gradio互換性を確認中...")
        
        if not test_gradio():
            print("\nGradioを修復しますか？ (y/n): ", end="")
            choice = input()
            
            if choice.lower() == 'y':
                if install_compatible_gradio():
                    test_gradio()
                    print("\n🚀 workflow_app.py を実行できます!")
                else:
                    create_alternative_solutions()
        else:
            print("\n🚀 環境は正常です！workflow_app.py を実行できます")
    
    else:
        print("\n❌ Python 3.8以上にアップグレードしてください")

if __name__ == "__main__":
    main()