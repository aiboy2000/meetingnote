"""
日本語サポートのインストールスクリプト
MeCabとfugashiを安全にインストール
"""

import subprocess
import sys
import os
import platform

def install_package(package):
    """パッケージをインストール"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package):
    """パッケージがインストールされているかチェック"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def install_mecab_windows():
    """Windows用MeCabインストール手順を表示"""
    print("=" * 60)
    print("Windows用MeCabインストール手順:")
    print("=" * 60)
    print("1. 以下からMeCabをダウンロード:")
    print("   https://github.com/ikegami-yukino/mecab/releases")
    print("   ファイル名例: mecab-0.996-64.exe")
    print()
    print("2. ダウンロードしたファイルを実行してインストール")
    print("3. インストール後、以下のコマンドを実行:")
    print("   pip install mecab-python3")
    print("   pip install fugashi[unidic]")
    print()
    print("4. 環境変数の設定（必要に応じて）:")
    print("   MECAB_PATH=C:\\Program Files (x86)\\MeCab\\bin")
    print("=" * 60)

def install_japanese_support():
    """日本語サポートをインストール"""
    print("日本語サポートのインストールを開始します...")
    
    # OSを確認
    os_name = platform.system()
    print(f"OS: {os_name}")
    
    # 基本パッケージのチェック
    packages_to_install = []
    
    if not check_package("fugashi"):
        packages_to_install.append("fugashi")
    
    if not check_package("unidic"):
        packages_to_install.append("unidic-lite")
    
    # Windowsの場合の特別処理
    if os_name == "Windows":
        print("Windowsが検出されました。")
        
        # fugashiのインストールを試行
        if "fugashi" in packages_to_install:
            print("fugashiのインストールを試行中...")
            if install_package("fugashi"):
                print("✓ fugashiのインストールに成功しました")
                packages_to_install.remove("fugashi")
            else:
                print("✗ fugashiのインストールに失敗しました")
                install_mecab_windows()
                return False
    
    # 残りのパッケージをインストール
    for package in packages_to_install:
        print(f"{package}をインストール中...")
        if install_package(package):
            print(f"✓ {package}のインストールに成功しました")
        else:
            print(f"✗ {package}のインストールに失敗しました")
    
    # 日本語モデルのインストール
    japanese_models = [
        "sentence-transformers",
        "transformers",
    ]
    
    for model in japanese_models:
        if not check_package(model.replace("-", "_")):
            print(f"{model}をインストール中...")
            install_package(model)
    
    return True

def test_japanese_support():
    """日本語サポートをテスト"""
    print("\n日本語サポートのテストを実行中...")
    
    try:
        # MeCabのテスト
        try:
            import MeCab
            tagger = MeCab.Tagger()
            result = tagger.parse("これはテストです")
            print("✓ MeCabが正常に動作しています")
        except Exception as e:
            print(f"✗ MeCabのテストに失敗: {e}")
    
        # fugashiのテスト
        try:
            import fugashi
            tagger = fugashi.Tagger()
            result = tagger("これはテストです")
            print("✓ fugashiが正常に動作しています")
        except Exception as e:
            print(f"✗ fugashiのテストに失敗: {e}")
    
        # 日本語モデルのテスト
        try:
            from sentence_transformers import SentenceTransformer
            # 軽量な多言語モデルをテスト
            model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            embedding = model.encode("鉄筋コンクリート構造")
            print("✓ 多言語SentenceTransformerが正常に動作しています")
            print(f"  ベクトル次元: {len(embedding)}")
        except Exception as e:
            print(f"✗ SentenceTransformerのテストに失敗: {e}")
    
    except Exception as e:
        print(f"テスト中にエラーが発生しました: {e}")

def main():
    print("=" * 60)
    print("建築会議転写システム - 日本語サポートインストーラー")
    print("=" * 60)
    
    # 現在の状況をチェック
    print("\n現在のパッケージ状況:")
    packages = ["fugashi", "MeCab", "unidic", "sentence_transformers"]
    for package in packages:
        status = "✓" if check_package(package.replace("-", "_")) else "✗"
        print(f"  {status} {package}")
    
    print("\nインストールを実行しますか？ (y/n): ", end="")
    choice = input().lower()
    
    if choice == 'y':
        if install_japanese_support():
            test_japanese_support()
            print("\n日本語サポートのインストールが完了しました！")
            print("main.pyを再実行してください。")
        else:
            print("\nインストールに問題がありました。")
            print("手動でMeCabをインストールしてから再実行してください。")
    else:
        print("インストールをキャンセルしました。")

if __name__ == "__main__":
    main()