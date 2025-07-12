"""
Gradio修復スクリプト
バージョン問題を解決
"""

import subprocess
import sys

def install_stable_gradio():
    """安定版Gradioをインストール"""
    print("🔧 Gradio 5.x の i18n 問題を修復中...")
    
    stable_versions = [
        "4.44.0",  # 最後の安定した4.x版
        "4.36.1",  # 長期安定版
        "4.28.3"   # 古い安定版
    ]
    
    for version in stable_versions:
        print(f"\n📦 Gradio {version} をインストール中...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                f"gradio=={version}", "--force-reinstall"
            ])
            
            # インストール確認
            import gradio as gr
            print(f"✅ Gradio {gr.__version__} のインストールが成功しました")
            
            # テスト起動
            print("🧪 テスト起動中...")
            test_interface()
            return True
            
        except Exception as e:
            print(f"❌ バージョン {version} でエラー: {e}")
            continue
    
    print("❌ すべてのバージョンで失敗しました")
    return False

def test_interface():
    """インターフェースをテスト"""
    try:
        import gradio as gr
        
        def test_func(text):
            return f"テスト成功: {text}"
        
        with gr.Blocks() as demo:
            gr.HTML("<h3>🧪 Gradio テスト</h3>")
            input_text = gr.Textbox(label="テスト入力")
            output_text = gr.Textbox(label="テスト出力")
            btn = gr.Button("テスト")
            btn.click(test_func, inputs=[input_text], outputs=[output_text])
        
        print("✅ インターフェース作成成功")
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

def create_alternative_launcher():
    """代替起動方法を作成"""
    launcher_code = '''"""
代替起動スクリプト
"""

import gradio as gr
import json

def simple_analysis(text, title="", date=""):
    if not text:
        return "テキストを入力してください", ""
    
    decisions = [line for line in text.split('。') if '決定' in line or '承認' in line]
    actions = [line for line in text.split('。') if '検討' in line or '確認' in line]
    issues = [line for line in text.split('。') if '課題' in line or '問題' in line]
    
    result = f"""
=== 議事録 ===
会議: {title}
日付: {date}

決定事項 ({len(decisions)}件):
{chr(10).join(f"• {d.strip()}" for d in decisions)}

行動項目 ({len(actions)}件):
{chr(10).join(f"• {a.strip()}" for a in actions)}

課題 ({len(issues)}件):
{chr(10).join(f"• {i.strip()}" for i in issues)}
"""
    
    json_result = json.dumps({
        "決定事項": decisions,
        "行動項目": actions,
        "課題": issues
    }, ensure_ascii=False, indent=2)
    
    return result.strip(), json_result

# 非常にシンプルなインターフェース
iface = gr.Interface(
    fn=simple_analysis,
    inputs=[
        gr.Textbox(label="会議内容", lines=5),
        gr.Textbox(label="タイトル", value=""),
        gr.Textbox(label="日付", value="")
    ],
    outputs=[
        gr.Textbox(label="議事録", lines=10),
        gr.Textbox(label="JSON", lines=5)
    ],
    title="🏗️ 建築会議転写システム（代替版）",
    description="シンプルな議事録生成"
)

if __name__ == "__main__":
    iface.launch(server_name="127.0.0.1", server_port=7860)
'''
    
    with open("emergency_app.py", "w", encoding="utf-8") as f:
        f.write(launcher_code)
    
    print("🆘 emergency_app.py を作成しました")

def main():
    """メイン実行"""
    print("🔧 Gradio修復ツール")
    print("=" * 40)
    
    print("現在のGradioで問題が発生しています。")
    print("以下の修復方法を試します:\n")
    
    print("1. 安定版Gradioへのダウングレード")
    print("2. 代替起動スクリプトの作成")
    print("3. トラブルシューティングガイド")
    
    print("\n修復を開始しますか? (y/n): ", end="")
    choice = input()
    
    if choice.lower() == 'y':
        # 安定版をインストール
        success = install_stable_gradio()
        
        if not success:
            print("\n🆘 代替方法を準備中...")
            create_alternative_launcher()
            
            print("\n🔧 手動修復手順:")
            print("1. pip uninstall gradio")
            print("2. pip install gradio==4.44.0")
            print("3. python emergency_app.py")
        
        else:
            print("\n✅ 修復完了!")
            print("以下のコマンドで起動してください:")
            print("python stable_app.py")
    
    else:
        print("\n📋 手動修復手順:")
        print("1. 新しい仮想環境を作成:")
        print("   python -m venv gradio_env")
        print("   gradio_env\\Scripts\\activate")
        print("2. 安定版Gradioをインストール:")
        print("   pip install gradio==4.44.0")
        print("3. アプリを起動:")
        print("   python stable_app.py")

if __name__ == "__main__":
    main()