"""
最小限アプリケーション
Gradioの互換性問題を完全回避
"""

import gradio as gr
import json
import logging
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_japanese_meeting(text: str, title: str = "", date: str = "") -> tuple:
    """日本語会議テキストを解析"""
    if not text.strip():
        return "", "テキストを入力してください"
    
    # キーワード定義
    decision_keywords = ['決定', '承認', '採用', '選定', '確定', '合意', '了承']
    action_keywords = ['検討', '確認', '調整', '実施', '対応', '準備', '作成', '提出', '報告', '連絡']
    issue_keywords = ['課題', '問題', '懸念', '検討事項', '要確認', '要検討']
    building_keywords = ['RC', 'PC', 'SRC', '鉄筋', 'コンクリート', '基礎', '施工', '図面', '構造', '設計', '品質管理', '安全管理']
    
    sentences = [s.strip() for s in text.split('。') if s.strip()]
    
    # 結果格納
    decisions = []
    actions = []
    issues = []
    building_terms = set()
    
    # 各文を解析
    for sentence in sentences:
        # 決定事項
        for keyword in decision_keywords:
            if keyword in sentence:
                decisions.append(f"• {sentence}")
                break
        
        # 行動項目
        for keyword in action_keywords:
            if keyword in sentence:
                actions.append(f"• {sentence}")
                break
        
        # 課題
        for keyword in issue_keywords:
            if keyword in sentence:
                issues.append(f"• {sentence}")
                break
        
        # 建築用語
        for term in building_keywords:
            if term in sentence:
                building_terms.add(term)
    
    # 結果をテキスト形式で生成
    result_lines = []
    result_lines.append("=" * 60)
    result_lines.append("🏗️ 建築会議 議事録")
    result_lines.append("=" * 60)
    result_lines.append(f"📅 会議: {title or '未設定'}")
    result_lines.append(f"📆 日付: {date or '未設定'}")
    result_lines.append("")
    
    if decisions:
        result_lines.append("✅ 【決定事項】")
        result_lines.extend(decisions)
        result_lines.append("")
    
    if actions:
        result_lines.append("📋 【行動項目】")
        result_lines.extend(actions)
        result_lines.append("")
    
    if issues:
        result_lines.append("⚠️ 【課題・検討事項】")
        result_lines.extend(issues)
        result_lines.append("")
    
    if building_terms:
        result_lines.append("🏗️ 【検出された建築用語】")
        result_lines.append(f"   {', '.join(sorted(building_terms))}")
        result_lines.append("")
    
    # 統計
    result_lines.append("📊 【統計】")
    result_lines.append(f"   決定事項: {len(decisions)}件")
    result_lines.append(f"   行動項目: {len(actions)}件")
    result_lines.append(f"   課題: {len(issues)}件")
    result_lines.append(f"   建築用語: {len(building_terms)}種類")
    
    # JSON形式
    json_result = {
        "会議情報": {
            "タイトル": title or "未設定",
            "日付": date or "未設定"
        },
        "決定事項": [d.replace("• ", "") for d in decisions],
        "行動項目": [a.replace("• ", "") for a in actions],
        "課題": [i.replace("• ", "") for i in issues],
        "建築用語": list(building_terms),
        "統計": {
            "決定事項数": len(decisions),
            "行動項目数": len(actions),
            "課題数": len(issues),
            "建築用語数": len(building_terms)
        }
    }
    
    text_result = '\n'.join(result_lines)
    json_text = json.dumps(json_result, ensure_ascii=False, indent=2)
    
    return text_result, json_text

def load_sample():
    """サンプルデータを返す"""
    return """本日の会議では、RC構造の基礎工事について検討しました。田中部長から品質管理の重要性について説明がありました。施工図面の修正が必要であることが決定されました。山田さんが来週までに図面を確認することになりました。安全管理についても課題があることが判明しました。緊急に対応が必要な項目があります。PC構造との比較検討も実施する予定です。佐藤係長に工程表の調整をお願いします。"""

def create_minimal_interface():
    """最小限のインターフェースを作成"""
    
    # 古いGradioバージョンとの互換性を考慮した最小構成
    with gr.Blocks(
        title="建築会議転写システム",
        css=".gradio-container { font-family: Arial, sans-serif; }"
    ) as app:
        
        # ヘッダー
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background-color: #f0f8ff; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: #2c3e50; margin: 0;">🏗️ 建築会議転写システム</h1>
            <p style="color: #7f8c8d; margin: 10px 0 0 0;">日本語建築会議の議事録を自動生成</p>
        </div>
        """)
        
        # メインコンテンツ
        with gr.Row():
            # 入力部分
            with gr.Column():
                gr.HTML("<h3 style='color: #34495e;'>📝 入力</h3>")
                
                title_input = gr.Textbox(
                    label="会議タイトル",
                    placeholder="例: RC構造検討会議"
                )
                
                date_input = gr.Textbox(
                    label="会議日付",
                    placeholder="例: 2024-01-15"
                )
                
                text_input = gr.Textbox(
                    label="会議内容",
                    placeholder="会議の内容を入力してください...",
                    lines=8
                )
                
                with gr.Row():
                    generate_btn = gr.Button("📋 議事録生成", variant="primary")
                    sample_btn = gr.Button("🔄 サンプル")
            
            # 出力部分
            with gr.Column():
                gr.HTML("<h3 style='color: #34495e;'>📄 出力</h3>")
                
                text_output = gr.Textbox(
                    label="議事録（テキスト形式）",
                    lines=12,
                    interactive=False
                )
                
                json_output = gr.Textbox(
                    label="議事録（JSON形式）",
                    lines=8,
                    interactive=False
                )
        
        # 使用説明
        gr.HTML("""
        <div style="margin-top: 20px; padding: 15px; background-color: #ecf0f1; border-radius: 8px;">
            <h4 style="color: #2c3e50; margin-top: 0;">💡 使用方法</h4>
            <ol style="color: #34495e;">
                <li>会議タイトルと日付を入力（任意）</li>
                <li>会議の内容テキストを入力</li>
                <li>「議事録生成」ボタンをクリック</li>
                <li>結果が表示されます</li>
            </ol>
            <p style="color: #7f8c8d; margin-bottom: 0;"><strong>検出機能:</strong> 決定事項、行動項目、課題、建築専門用語</p>
        </div>
        """)
        
        # イベント設定
        generate_btn.click(
            fn=analyze_japanese_meeting,
            inputs=[text_input, title_input, date_input],
            outputs=[text_output, json_output]
        )
        
        sample_btn.click(
            fn=load_sample,
            outputs=[text_input]
        )
    
    return app

def main():
    """メイン実行"""
    print("🏗️ 建築会議転写システム（最小版）を起動中...")
    print("⚠️  Gradioのバージョン:", gr.__version__)
    
    try:
        # アプリケーション作成
        app = create_minimal_interface()
        
        # 最も互換性の高い設定で起動
        print("🌐 サーバーを起動中...")
        app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            debug=False,
            quiet=True,
            inbrowser=True
        )
        
    except Exception as e:
        print(f"❌ 起動エラー: {e}")
        print("\n🔧 トラブルシューティング:")
        print("1. Gradioを最新版に更新: pip install --upgrade gradio")
        print("2. 仮想環境を新規作成: python -m venv new_env")
        print("3. Pythonバージョンを確認: python --version")

if __name__ == "__main__":
    main()