"""
シンプル版アプリケーション
Gradioの互換性問題を回避した最小構成
"""

import gradio as gr
import json
import logging
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleApp:
    def __init__(self):
        """シンプル版アプリケーションを初期化"""
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 基本的なキーワード定義
        self.keywords = {
            "action": ['検討', '確認', '調整', '実施', '対応', '準備', '作成', '提出', '報告'],
            "decision": ['決定', '承認', '採用', '選定', '確定', '合意', '了承'],
            "issue": ['課題', '問題', '懸念', '検討事項', '要確認', '要検討'],
            "building": ['RC', 'PC', 'SRC', '鉄筋', 'コンクリート', '基礎', '施工', '図面', '構造', '設計']
        }
    
    def analyze_text(self, text: str) -> dict:
        """テキスト解析"""
        if not text.strip():
            return {"error": "テキストを入力してください"}
        
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        
        results = {
            "decisions": [],
            "actions": [],
            "issues": [],
            "building_terms": []
        }
        
        # 各文を分析
        for sentence in sentences:
            # 決定事項
            for keyword in self.keywords["decision"]:
                if keyword in sentence:
                    results["decisions"].append({
                        "content": sentence,
                        "keyword": keyword
                    })
                    break
            
            # 行動項目
            for keyword in self.keywords["action"]:
                if keyword in sentence:
                    results["actions"].append({
                        "content": sentence,
                        "keyword": keyword
                    })
                    break
            
            # 課題
            for keyword in self.keywords["issue"]:
                if keyword in sentence:
                    results["issues"].append({
                        "content": sentence,
                        "keyword": keyword
                    })
                    break
            
            # 建築用語
            for term in self.keywords["building"]:
                if term in sentence:
                    if term not in results["building_terms"]:
                        results["building_terms"].append(term)
        
        return results
    
    def generate_minutes(self, text: str, title: str = "", date: str = "") -> tuple:
        """議事録生成"""
        try:
            analysis = self.analyze_text(text)
            
            if "error" in analysis:
                return "", analysis["error"]
            
            # JSON出力
            minutes = {
                "会議情報": {
                    "タイトル": title or "未設定",
                    "日付": date or "未設定"
                },
                "決定事項": analysis["decisions"],
                "行動項目": analysis["actions"], 
                "課題": analysis["issues"],
                "建築用語": analysis["building_terms"],
                "統計": {
                    "決定事項数": len(analysis["decisions"]),
                    "行動項目数": len(analysis["actions"]),
                    "課題数": len(analysis["issues"]),
                    "建築用語数": len(analysis["building_terms"])
                }
            }
            
            json_output = json.dumps(minutes, ensure_ascii=False, indent=2)
            
            # テキスト出力
            text_lines = []
            text_lines.append("=" * 50)
            text_lines.append("議事録")
            text_lines.append("=" * 50)
            text_lines.append(f"会議: {title or '未設定'}")
            text_lines.append(f"日付: {date or '未設定'}")
            text_lines.append("")
            
            if analysis["decisions"]:
                text_lines.append("【決定事項】")
                for i, item in enumerate(analysis["decisions"], 1):
                    text_lines.append(f"{i}. {item['content']}")
                text_lines.append("")
            
            if analysis["actions"]:
                text_lines.append("【行動項目】")
                for i, item in enumerate(analysis["actions"], 1):
                    text_lines.append(f"{i}. {item['content']}")
                text_lines.append("")
            
            if analysis["issues"]:
                text_lines.append("【課題】")
                for i, item in enumerate(analysis["issues"], 1):
                    text_lines.append(f"{i}. {item['content']}")
                text_lines.append("")
            
            if analysis["building_terms"]:
                text_lines.append("【検出された建築用語】")
                text_lines.append(", ".join(analysis["building_terms"]))
                text_lines.append("")
            
            text_output = '\n'.join(text_lines)
            
            return json_output, text_output
            
        except Exception as e:
            error_msg = f"エラーが発生しました: {str(e)}"
            logger.error(error_msg)
            return "", error_msg

def create_app():
    """Gradioアプリを作成"""
    app = SimpleApp()
    
    # シンプルなインターフェースを作成
    with gr.Blocks() as interface:
        gr.HTML("<h1>🏗️ 建築会議転写システム</h1>")
        gr.HTML("<p>日本語建築会議の議事録を自動生成します</p>")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<h3>📝 入力</h3>")
                
                title_input = gr.Textbox(
                    label="会議タイトル",
                    placeholder="例: RC構造検討会議",
                    lines=1
                )
                
                date_input = gr.Textbox(
                    label="会議日付", 
                    placeholder="例: 2024-01-15",
                    lines=1
                )
                
                text_input = gr.Textbox(
                    label="会議内容",
                    placeholder="会議の転写テキストまたは議事内容を入力してください...\n\n例:\n本日の会議では、RC構造の基礎工事について検討しました。田中部長から品質管理の重要性について説明がありました。施工図面の修正が必要であることが決定されました。",
                    lines=8
                )
                
                generate_btn = gr.Button("📋 議事録生成", variant="primary")
                
                # サンプルボタン
                sample_btn = gr.Button("🔄 サンプルデータ読み込み")
            
            with gr.Column(scale=1):
                gr.HTML("<h3>📄 出力</h3>")
                
                with gr.Tab("📝 テキスト形式"):
                    text_output = gr.Textbox(
                        label="議事録",
                        lines=15,
                        interactive=False
                    )
                
                with gr.Tab("💻 JSON形式"):
                    json_output = gr.Textbox(
                        label="構造化データ",
                        lines=15,
                        interactive=False
                    )
        
        # サンプルデータ
        sample_text = """本日の会議では、RC構造の基礎工事について検討しました。田中部長から品質管理の重要性について説明がありました。施工図面の修正が必要であることが決定されました。山田さんが来週までに図面を確認することになりました。安全管理についても課題があることが判明しました。PC構造との比較も実施する予定です。"""
        
        # イベント設定
        generate_btn.click(
            fn=app.generate_minutes,
            inputs=[text_input, title_input, date_input],
            outputs=[json_output, text_output]
        )
        
        sample_btn.click(
            fn=lambda: sample_text,
            outputs=[text_input]
        )
        
        # 使用方法の説明
        gr.HTML("""
        <div style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
        <h4>💡 使用方法</h4>
        <ol>
        <li>会議タイトルと日付を入力（オプション）</li>
        <li>会議の転写テキストまたは議事内容を入力</li>
        <li>「議事録生成」ボタンをクリック</li>
        <li>結果がテキスト形式とJSON形式で表示されます</li>
        </ol>
        <p><strong>対応機能:</strong> 決定事項・行動項目・課題の自動抽出、建築専門用語の検出</p>
        </div>
        """)
    
    return interface

def main():
    """メイン実行"""
    print("🏗️ 建築会議転写システム（シンプル版）を起動中...")
    
    try:
        app = create_app()
        
        # 起動
        app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            inbrowser=True,
            quiet=False
        )
        
    except Exception as e:
        print(f"❌ 起動エラー: {e}")
        print("以下のコマンドで必要なパッケージをインストールしてください:")
        print("pip install gradio")

if __name__ == "__main__":
    main()