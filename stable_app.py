"""
安定版アプリケーション
Gradio 5.x の既知の問題を回避
"""

import gradio as gr
import json
import os

def analyze_meeting_text(text, title="", date=""):
    """会議テキストを解析する"""
    if not text.strip():
        return "テキストを入力してください。", ""
    
    # キーワード定義
    decision_words = ['決定', '承認', '採用', '選定', '確定', '合意', '了承']
    action_words = ['検討', '確認', '調整', '実施', '対応', '準備', '作成', '提出', '報告', '連絡']
    issue_words = ['課題', '問題', '懸念', '検討事項', '要確認', '要検討']
    building_words = ['RC', 'PC', 'SRC', '鉄筋', 'コンクリート', '基礎', '施工', '図面', '構造', '設計']
    
    sentences = [s.strip() for s in text.split('。') if s.strip()]
    
    decisions = []
    actions = []
    issues = []
    building_terms = set()
    
    # 文章解析
    for sentence in sentences:
        # 決定事項
        for word in decision_words:
            if word in sentence:
                decisions.append(sentence)
                break
        
        # 行動項目
        for word in action_words:
            if word in sentence:
                actions.append(sentence)
                break
        
        # 課題
        for word in issue_words:
            if word in sentence:
                issues.append(sentence)
                break
        
        # 建築用語
        for term in building_words:
            if term in sentence:
                building_terms.add(term)
    
    # テキスト結果
    result = []
    result.append("=" * 50)
    result.append("🏗️ 建築会議 議事録")
    result.append("=" * 50)
    result.append(f"会議: {title or '未設定'}")
    result.append(f"日付: {date or '未設定'}")
    result.append("")
    
    if decisions:
        result.append("✅ 決定事項:")
        for d in decisions:
            result.append(f"  • {d}")
        result.append("")
    
    if actions:
        result.append("📋 行動項目:")
        for a in actions:
            result.append(f"  • {a}")
        result.append("")
    
    if issues:
        result.append("⚠️ 課題:")
        for i in issues:
            result.append(f"  • {i}")
        result.append("")
    
    if building_terms:
        result.append("🏗️ 建築用語:")
        result.append(f"  {', '.join(sorted(building_terms))}")
        result.append("")
    
    result.append(f"📊 統計: 決定{len(decisions)}件, 行動{len(actions)}件, 課題{len(issues)}件")
    
    # JSON結果
    json_data = {
        "meeting": {"title": title, "date": date},
        "decisions": decisions,
        "actions": actions,
        "issues": issues,
        "building_terms": list(building_terms),
        "stats": {"decisions": len(decisions), "actions": len(actions), "issues": len(issues)}
    }
    
    return "\n".join(result), json.dumps(json_data, ensure_ascii=False, indent=2)

def get_sample_text():
    """サンプルテキストを返す"""
    return """本日の会議では、RC構造の基礎工事について検討しました。田中部長から品質管理の重要性について説明がありました。施工図面の修正が必要であることが決定されました。山田さんが来週までに図面を確認することになりました。安全管理についても課題があることが判明しました。"""

# Gradio インターフェース作成
def create_interface():
    """インターフェースを作成"""
    
    # 最もシンプルな設定でBlocks作成
    with gr.Blocks() as demo:
        gr.HTML("<h1>🏗️ 建築会議転写システム</h1>")
        gr.HTML("<p>日本語建築会議の議事録を自動生成します</p>")
        
        with gr.Row():
            with gr.Column():
                title = gr.Textbox(label="会議タイトル", placeholder="例: RC構造検討会議")
                date = gr.Textbox(label="日付", placeholder="例: 2024-01-15")
                text = gr.Textbox(
                    label="会議内容", 
                    lines=6,
                    placeholder="会議の内容を入力してください..."
                )
                
                with gr.Row():
                    submit_btn = gr.Button("議事録生成", variant="primary")
                    sample_btn = gr.Button("サンプル読み込み")
            
            with gr.Column():
                output_text = gr.Textbox(
                    label="議事録", 
                    lines=12,
                    interactive=False
                )
                output_json = gr.Textbox(
                    label="JSON出力", 
                    lines=6,
                    interactive=False
                )
        
        # イベント設定
        submit_btn.click(
            fn=analyze_meeting_text,
            inputs=[text, title, date],
            outputs=[output_text, output_json]
        )
        
        sample_btn.click(
            fn=get_sample_text,
            outputs=[text]
        )
        
        gr.HTML("""
        <div style="margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px;">
        <h4>使用方法:</h4>
        <ol>
        <li>会議タイトルと日付を入力（オプション）</li>
        <li>会議内容を入力</li>
        <li>「議事録生成」をクリック</li>
        </ol>
        <p><b>機能:</b> 決定事項・行動項目・課題・建築用語の自動抽出</p>
        </div>
        """)
    
    return demo

def main():
    """メイン実行"""
    print("🏗️ 建築会議転写システム（安定版）")
    print(f"📦 Gradio version: {gr.__version__}")
    
    # インターフェース作成
    demo = create_interface()
    
    try:
        # 最も安定した設定で起動
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            debug=False,
            quiet=True,
            show_error=False,  # エラー表示を無効化
            inbrowser=True
        )
    except Exception as e:
        print(f"❌ 起動エラー: {e}")
        print("\n🔧 代替手段:")
        print("1. 古いGradioバージョンを試す:")
        print("   pip install gradio==4.44.0")
        print("2. ブラウザを手動で開く:")
        print("   http://127.0.0.1:7860")

if __name__ == "__main__":
    main()