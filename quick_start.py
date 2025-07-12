"""
クイックスタート - 基本機能のみ
依存関係の問題を回避して基本機能をテスト
"""

import gradio as gr
import json
import logging
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTranscriberApp:
    def __init__(self):
        """シンプル版アプリケーションを初期化"""
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 基本的なタグ付けキーワード
        self.action_keywords = ['検討', '確認', '調整', '実施', '対応', '準備', '作成']
        self.decision_keywords = ['決定', '承認', '採用', '選定', '確定', '合意']
        self.issue_keywords = ['課題', '問題', '懸念', '検討事項']
    
    def simple_text_analysis(self, text: str) -> dict:
        """簡易テキスト解析"""
        if not text.strip():
            return {"error": "テキストが入力されていません"}
        
        sentences = text.split('。')
        
        # 決定事項を抽出
        decisions = []
        for sentence in sentences:
            for keyword in self.decision_keywords:
                if keyword in sentence and len(sentence.strip()) > 5:
                    decisions.append({
                        "content": sentence.strip(),
                        "keyword": keyword,
                        "type": "decision"
                    })
                    break
        
        # 行動項目を抽出
        actions = []
        for sentence in sentences:
            for keyword in self.action_keywords:
                if keyword in sentence and len(sentence.strip()) > 5:
                    actions.append({
                        "content": sentence.strip(),
                        "keyword": keyword,
                        "type": "action"
                    })
                    break
        
        # 課題を抽出
        issues = []
        for sentence in sentences:
            for keyword in self.issue_keywords:
                if keyword in sentence and len(sentence.strip()) > 5:
                    issues.append({
                        "content": sentence.strip(),
                        "keyword": keyword,
                        "type": "issue"
                    })
                    break
        
        # 要約（最初の2文）
        summary_sentences = [s.strip() for s in sentences[:2] if s.strip()]
        summary = '。'.join(summary_sentences)
        
        return {
            "summary": summary,
            "decisions": decisions,
            "actions": actions,
            "issues": issues,
            "total_sentences": len([s for s in sentences if s.strip()])
        }
    
    def generate_simple_minutes(self, text: str, title: str = "", date: str = "") -> tuple:
        """簡易議事録生成"""
        try:
            analysis = self.simple_text_analysis(text)
            
            if "error" in analysis:
                return "", analysis["error"]
            
            # JSON形式の結果
            minutes = {
                "meeting_info": {
                    "title": title or "会議",
                    "date": date or "未設定"
                },
                "summary": analysis["summary"],
                "decisions": analysis["decisions"],
                "action_items": analysis["actions"],
                "issues": analysis["issues"],
                "stats": {
                    "total_sentences": analysis["total_sentences"],
                    "decisions_count": len(analysis["decisions"]),
                    "actions_count": len(analysis["actions"]),
                    "issues_count": len(analysis["issues"])
                }
            }
            
            json_output = json.dumps(minutes, ensure_ascii=False, indent=2)
            
            # テキスト形式の結果
            text_lines = []
            text_lines.append("=" * 50)
            text_lines.append("簡易議事録")
            text_lines.append("=" * 50)
            text_lines.append(f"会議名: {title or '未設定'}")
            text_lines.append(f"日付: {date or '未設定'}")
            text_lines.append("")
            
            text_lines.append("【要約】")
            text_lines.append(analysis["summary"])
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
                text_lines.append("【課題・検討事項】")
                for i, item in enumerate(analysis["issues"], 1):
                    text_lines.append(f"{i}. {item['content']}")
                text_lines.append("")
            
            text_lines.append(f"統計: 文数={analysis['total_sentences']}, 決定事項={len(analysis['decisions'])}, 行動項目={len(analysis['actions'])}, 課題={len(analysis['issues'])}")
            
            text_output = '\n'.join(text_lines)
            
            return json_output, text_output
            
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            return "", f"エラーが発生しました: {str(e)}"
    
    def create_interface(self):
        """Gradioインターフェースを作成"""
        
        with gr.Blocks(title="建築会議転写システム（シンプル版）") as app:
            gr.Markdown("# 建築会議転写システム（シンプル版）")
            gr.Markdown("基本的なテキスト解析と議事録生成機能")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## 会議情報入力")
                    meeting_title = gr.Textbox(
                        label="会議タイトル",
                        placeholder="例: RC構造検討会議"
                    )
                    meeting_date = gr.Textbox(
                        label="会議日付",
                        placeholder="例: 2024-01-15"
                    )
                    
                    meeting_text = gr.Textbox(
                        label="会議内容（テキスト）",
                        lines=10,
                        placeholder="会議の内容をここに入力してください。\n\n例:\n本日の会議では、RC構造の基礎工事について検討しました。\n田中部長から品質管理の重要性について説明がありました。\n施工図面の修正が必要であることが決定されました。\n山田さんが来週までに図面を確認することになりました。\n安全管理についても課題があることが判明しました。"
                    )
                    
                    analyze_btn = gr.Button("議事録生成", variant="primary")
                
                with gr.Column():
                    gr.Markdown("## 生成結果")
                    
                    with gr.Tab("テキスト形式"):
                        minutes_text = gr.Textbox(
                            label="議事録（テキスト）",
                            lines=20,
                            interactive=False
                        )
                    
                    with gr.Tab("JSON形式"):
                        minutes_json = gr.Textbox(
                            label="議事録（JSON）",
                            lines=20,
                            interactive=False
                        )
            
            # サンプルデータ
            gr.Markdown("### サンプルデータ")
            sample_text = """本日の会議では、RC構造の基礎工事について検討しました。田中部長から品質管理の重要性について説明がありました。施工図面の修正が必要であることが決定されました。山田さんが来週までに図面を確認することになりました。安全管理についても課題があることが判明しました。緊急に対応が必要な項目があります。"""
            
            sample_btn = gr.Button("サンプルデータを読み込み")
            
            # イベントハンドラ
            analyze_btn.click(
                fn=self.generate_simple_minutes,
                inputs=[meeting_text, meeting_title, meeting_date],
                outputs=[minutes_json, minutes_text]
            )
            
            sample_btn.click(
                fn=lambda: sample_text,
                outputs=[meeting_text]
            )
        
        return app

def main():
    """メイン実行関数"""
    logger.info("Starting Simple Transcriber App...")
    
    # シンプル版アプリケーションを初期化
    app_instance = SimpleTranscriberApp()
    
    # Gradioインターフェースを起動
    interface = app_instance.create_interface()
    
    # アプリケーションを起動
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

if __name__ == "__main__":
    main()