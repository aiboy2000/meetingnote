"""
安定版ワークフローアプリ
Gradio互換性問題を解決
"""

import gradio as gr
import json
import os
from pathlib import Path

class StableWorkflowApp:
    def __init__(self):
        """安定版ワークフローアプリを初期化"""
        self.data_dir = Path("workflow_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 状態管理
        self.term_db_ready = False
        self.extracted_terms = []
        self.transcription_ready = False
        self.transcript_text = ""
    
    def extract_terms_simple(self, pdf_files):
        """簡単な術語抽出（ファイルアップロード不使用）"""
        if pdf_files is None:
            return "PDFファイルが選択されていません。", ""
        
        # デモ用の術語データ
        demo_terms = {
            "構造": ["RC造", "PC造", "SRC造", "鉄筋コンクリート造", "基礎工事", "杭工事"],
            "工事": ["型枠工事", "配筋工事", "コンクリート工事", "躯体工事", "仕上工事"],
            "材料": ["コンクリート強度", "鉄筋材料", "セメント", "骨材", "添加剤"],
            "管理": ["品質管理", "安全管理", "工程管理", "施工管理", "検査方法"],
            "設計": ["構造設計", "意匠設計", "構造計算", "施工図面", "仕様書"],
            "法規": ["建築基準法", "確認申請", "完了検査", "検査済証"]
        }

        self.extracted_terms = []
        for category_terms in demo_terms.values():
            self.extracted_terms.extend(category_terms)

        self.term_db_ready = True

        # 結果表示
        result_text = f"✅ 専門術語抽出完了\n\n"
        result_text += f"📊 抽出された術語数: {len(self.extracted_terms)}\n\n"

        for category, terms in demo_terms.items():
            result_text += f"🏗️ {category}: {', '.join(terms)}\n"

        result_text += f"\n✅ ステップ1完了 → ステップ2に進んでください"

        # JSON形式
        json_data = {
            "status": "completed",
            "terms_count": len(self.extracted_terms),
            "terms_by_category": demo_terms
        }

        return result_text, json.dumps(json_data, ensure_ascii=False, indent=2)
    
    def transcribe_audio_simple(self, audio_files):
        """簡単な音声転写（ファイルアップロード不使用）"""
        if not self.term_db_ready:
            return "❌ 先にステップ1で専門術語を抽出してください。", ""
        
        if audio_files is None:
            return "音声ファイルが選択されていません。", ""

        # デモ用転写テキスト
        self.transcript_text = """本日はお忙しい中お集まりいただき、ありがとうございます。

今回の会議では、RC構造の基礎工事について検討いたします。

田中部長より、品質管理の重要性についてご説明いただきました。特に、コンクリートの強度試験については、建築基準法に基づき厳格に実施することが決定されました。

次に、施工図面の修正についてですが、構造計算の見直しが必要との判断になりました。山田係長に来週までに修正案を作成していただくことをお願いいたします。

また、安全管理についても課題が見つかりました。作業員の安全教育を強化する必要があります。これは緊急に対応すべき事項として認識しています。

配筋工事の品質確認も重要な検討事項です。佐藤主任に詳細な検査計画を作成していただきます。

以上で本日の議事を終了いたします。ありがとうございました。"""

        # 使用された術語をチェック
        used_terms = []
        for term in self.extracted_terms:
            if term in self.transcript_text:
                used_terms.append(term)

        self.transcription_ready = True

        # 結果表示
        result_text = f"✅ 音声転写完了\n\n"
        result_text += f"📝 文字数: {len(self.transcript_text)}\n"
        result_text += f"🏗️ 検出された専門術語: {len(used_terms)}個\n\n"

        if used_terms:
            result_text += "検出された術語:\n"
            result_text += f"{', '.join(used_terms)}\n\n"

        result_text += "📄 転写テキスト:\n"
        result_text += "=" * 50 + "\n"
        result_text += self.transcript_text
        result_text += "\n" + "=" * 50 + "\n"
        result_text += "\n✅ ステップ2完了 → ステップ3に進んでください"

        return result_text, self.transcript_text
    
    def generate_minutes_simple(self, meeting_title, meeting_date):
        """簡単な議事録生成"""
        if not self.transcription_ready:
            return "❌ 先にステップ2で音声転写を完了してください。", ""

        title = meeting_title or "建築技術検討会議"
        date = meeting_date or "2024年1月15日"

        # キーワード抽出
        sentences = [s.strip() for s in self.transcript_text.split('。') if s.strip()]

        decisions = []
        actions = []
        issues = []

        # 文章解析
        for sentence in sentences:
            if any(keyword in sentence for keyword in ['決定', '承認', '確定']):
                decisions.append(sentence)
            if any(keyword in sentence for keyword in ['お願い', '作成', '実施', '確認']):
                actions.append(sentence)
            if any(keyword in sentence for keyword in ['課題', '問題', '検討']):
                issues.append(sentence)

        # 使用された術語
        used_terms = [term for term in self.extracted_terms if term in self.transcript_text]

        # 議事録テキスト生成
        minutes_text = []
        minutes_text.append("=" * 60)
        minutes_text.append("🏗️ 建築会議 議事録")
        minutes_text.append("=" * 60)
        minutes_text.append(f"📅 会議名: {title}")
        minutes_text.append(f"📆 日付: {date}")
        minutes_text.append("")

        if decisions:
            minutes_text.append("✅ 【決定事項】")
            for i, decision in enumerate(decisions, 1):
                minutes_text.append(f"{i}. {decision}")
            minutes_text.append("")

        if actions:
            minutes_text.append("📋 【行動項目】")
            for i, action in enumerate(actions, 1):
                minutes_text.append(f"{i}. {action}")
            minutes_text.append("")

        if issues:
            minutes_text.append("⚠️ 【課題・検討事項】")
            for i, issue in enumerate(issues, 1):
                minutes_text.append(f"{i}. {issue}")
            minutes_text.append("")

        if used_terms:
            minutes_text.append("🏗️ 【使用された専門術語】")
            minutes_text.append(f"{', '.join(sorted(used_terms))}")
            minutes_text.append("")

        minutes_text.append("📊 【統計】")
        minutes_text.append(f"決定事項: {len(decisions)}件")
        minutes_text.append(f"行動項目: {len(actions)}件")
        minutes_text.append(f"課題: {len(issues)}件")
        minutes_text.append(f"専門術語: {len(used_terms)}種類")

        # JSON形式
        json_data = {
            "meeting_info": {"title": title, "date": date},
            "decisions": decisions,
            "action_items": actions,
            "issues": issues,
            "technical_terms": used_terms,
            "statistics": {
                "decisions_count": len(decisions),
                "actions_count": len(actions),
                "issues_count": len(issues),
                "terms_count": len(used_terms)
            }
        }

        final_text = '\n'.join(minutes_text)
        final_text += "\n\n✅ 全ワークフロー完了！"

        return final_text, json.dumps(json_data, ensure_ascii=False, indent=2)

def create_stable_interface():
    """安定したインターフェースを作成"""
    app = StableWorkflowApp()

    # 非常にシンプルなインターフェース
    with gr.Blocks(title="建築会議転写システム（安定版）") as demo:
        gr.HTML("<h1>🏗️ 建築会議転写システム（安定版）</h1>")
        gr.HTML("<p>3ステップワークフロー（安定版）</p>")

        # ステップ1
        with gr.Row():
            with gr.Column():
                gr.HTML("<h3>📚 ステップ1: 専門術語抽出</h3>")
                pdf_input = gr.Textbox(
                    label="PDFファイル名（デモ用）",
                    placeholder="任意のファイル名を入力してください",
                    value="building_terms.pdf"
                )
                extract_btn = gr.Button("🔍 術語抽出開始", variant="primary")

            with gr.Column():
                terms_output = gr.Textbox(
                    label="抽出結果",
                    lines=8,
                    interactive=False
                )

        # ステップ2
        with gr.Row():
            with gr.Column():
                gr.HTML("<h3>🎤 ステップ2: 音声転写</h3>")
                audio_input = gr.Textbox(
                    label="音声ファイル名（デモ用）",
                    placeholder="任意のファイル名を入力してください",
                    value="meeting_audio.mp4"
                )
                transcribe_btn = gr.Button("🎤 転写開始", variant="primary")

            with gr.Column():
                transcript_output = gr.Textbox(
                    label="転写結果",
                    lines=8,
                    interactive=False
                )

        # ステップ3
        with gr.Row():
            with gr.Column():
                gr.HTML("<h3>📄 ステップ3: 議事録生成</h3>")
                meeting_title = gr.Textbox(
                    label="会議タイトル",
                    value="RC構造技術検討会議"
                )
                meeting_date = gr.Textbox(
                    label="会議日付",
                    value="2024年1月15日"
                )
                minutes_btn = gr.Button("📋 議事録生成", variant="primary")

            with gr.Column():
                minutes_output = gr.Textbox(
                    label="議事録",
                    lines=12,
                    interactive=False
                )

        # JSON出力
        json_output = gr.Textbox(
            label="JSON出力",
            lines=6,
            interactive=False
        )

        # イベント設定
        extract_btn.click(
            fn=app.extract_terms_simple,
            inputs=[pdf_input],
            outputs=[terms_output, json_output]
        )

        transcribe_btn.click(
            fn=app.transcribe_audio_simple,
            inputs=[audio_input],
            outputs=[transcript_output, json_output]
        )

        minutes_btn.click(
            fn=app.generate_minutes_simple,
            inputs=[meeting_title, meeting_date],
            outputs=[minutes_output, json_output]
        )

        gr.HTML("""
        <div style="margin-top: 20px; padding: 15px; background: #f0f8ff; border-radius: 8px;">
        <h4>📖 使用方法（安定版）:</h4>
        <ol>
        <li><strong>ステップ1:</strong> PDFファイル名を入力して「術語抽出開始」</li>
        <li><strong>ステップ2:</strong> 音声ファイル名を入力して「転写開始」</li>
        <li><strong>ステップ3:</strong> 会議情報を入力して「議事録生成」</li>
        </ol>
        <p><strong>注意:</strong> この安定版はファイルアップロード機能を無効にしてデモデータを使用します。</p>
        </div>
        """)

    return demo

def main():
    """メイン実行"""
    print("🏗️ 建築会議転写システム（安定版）")
    print("Gradio互換性問題を解決した版")

    try:
        demo = create_stable_interface()
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            inbrowser=True,
            debug=False,
            show_error=False
        )
    except Exception as e:
        print(f"❌ エラー: {e}")
        print("\nHTMLバックアップ版を作成中...")
        
        # HTMLバックアップ版
        import simple_workflow
        simple_workflow.main()

if __name__ == "__main__":
    main()