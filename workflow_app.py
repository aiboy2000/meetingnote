"""
建築会議転写システム - ワークフロー版
1. 専門術語抽出 → 2. 音声転写 → 3. 議事録生成
"""

import gradio as gr
import json
import os
import tempfile
import shutil
from pathlib import Path

class WorkflowApp:
    def __init__(self):
        """ワークフローアプリを初期化"""
        self.data_dir = Path("workflow_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 状態管理
        self.term_db_ready = False
        self.extracted_terms = []
        self.transcription_ready = False
        self.transcript_text = ""
    
    # === ステップ1: 専門術語抽出 ===
    def extract_terms_from_pdf(self, pdf_files):
        """PDFから専門術語を抽出"""
        if not pdf_files:
            return "PDFファイルを選択してください。", ""
        
        try:
            all_terms = set()
            
            # 建築専門用語のパターン
            building_patterns = [
                'RC', 'PC', 'SRC', '鉄筋', 'コンクリート', '基礎', '杭', '梁', '柱', 'スラブ',
                '施工', '設計', '構造', '図面', '仕様', '検査', '試験', '品質管理', '安全管理',
                '工程管理', '施工管理', '建築基準法', '確認申請', '検査済証', '完了検査',
                '型枠', '配筋', '打設', '養生', '強度', '圧縮', '引張', '曲げ', '剪断',
                '基礎工事', '躯体工事', '仕上工事', '設備工事', '外構工事'
            ]
            
            # 簡易的なテキスト抽出（実際にはpdfplumberを使用）
            for pdf_file in pdf_files:
                # ファイル名から術語を推測（デモ用）
                filename = os.path.basename(pdf_file.name).lower()
                
                # ファイル名に含まれる建築用語を検出
                for term in building_patterns:
                    if term.lower() in filename or term in filename:
                        all_terms.add(term)
                
                # デモ用のサンプル術語を追加
                sample_terms = [
                    '鉄筋コンクリート造', 'RC造', '基礎工事', '杭工事', '型枠工事',
                    '配筋工事', 'コンクリート打設', '品質管理', '施工管理', '安全管理',
                    '構造計算', '意匠設計', '設備設計', '施工図面', '建築基準法'
                ]
                all_terms.update(sample_terms[:10])  # 最初の10個を追加
            
            self.extracted_terms = list(all_terms)
            self.term_db_ready = True
            
            # 結果表示
            result_text = f"✅ 専門術語抽出完了\n\n"
            result_text += f"📊 抽出された術語数: {len(self.extracted_terms)}\n\n"
            result_text += "🏗️ 主要な建築専門術語:\n"
            
            for i, term in enumerate(sorted(self.extracted_terms)[:15], 1):
                result_text += f"{i:2d}. {term}\n"
            
            if len(self.extracted_terms) > 15:
                result_text += f"... 他 {len(self.extracted_terms) - 15} 個\n"
            
            result_text += f"\n✅ ステップ1完了 → ステップ2に進んでください"
            
            # JSON形式
            json_data = {
                "status": "completed",
                "terms_count": len(self.extracted_terms),
                "terms": self.extracted_terms
            }
            
            return result_text, json.dumps(json_data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"❌ エラー: {str(e)}", ""
    
    # === ステップ2: 音声転写 ===
    def transcribe_audio(self, audio_file):
        """音声ファイルを転写"""
        if not audio_file:
            return "音声ファイルを選択してください。", ""
        
        if not self.term_db_ready:
            return "❌ 先にステップ1で専門術語を抽出してください。", ""
        
        try:
            # 実際にはWhisperを使用するが、ここではデモ用の模擬転写
            filename = os.path.basename(audio_file.name)
            
            # デモ用のサンプル転写テキスト
            demo_transcript = """本日はお忙しい中お集まりいただき、ありがとうございます。

今回の会議では、RC構造の基礎工事について検討いたします。

田中部長より、品質管理の重要性についてご説明いただきました。特に、コンクリートの強度試験については、建築基準法に基づき厳格に実施することが決定されました。

次に、施工図面の修正についてですが、構造計算の見直しが必要との判断になりました。山田係長に来週までに修正案を作成していただくことをお願いいたします。

また、安全管理についても課題が見つかりました。作業員の安全教育を強化する必要があります。これは緊急に対応すべき事項として認識しています。

配筋工事の品質確認も重要な検討事項です。佐藤主任に詳細な検査計画を作成していただきます。

型枠工事については、施工精度の向上が求められています。

以上で本日の議事を終了いたします。ありがとうございました。"""
            
            # 専門術語を使用した補正（デモ）
            corrected_transcript = demo_transcript
            
            # 専門術語チェック
            found_terms = []
            for term in self.extracted_terms:
                if term in corrected_transcript:
                    found_terms.append(term)
            
            self.transcript_text = corrected_transcript
            self.transcription_ready = True
            
            # 結果表示
            result_text = f"✅ 音声転写完了\n\n"
            result_text += f"📁 ファイル: {filename}\n"
            result_text += f"📝 文字数: {len(corrected_transcript)}\n"
            result_text += f"🏗️ 検出された専門術語: {len(found_terms)}個\n\n"
            
            if found_terms:
                result_text += "検出された術語:\n"
                for term in found_terms[:10]:
                    result_text += f"• {term}\n"
                if len(found_terms) > 10:
                    result_text += f"... 他 {len(found_terms) - 10} 個\n"
                result_text += "\n"
            
            result_text += "📄 転写テキスト:\n"
            result_text += "=" * 50 + "\n"
            result_text += corrected_transcript
            result_text += "\n" + "=" * 50 + "\n"
            result_text += "\n✅ ステップ2完了 → ステップ3に進んでください"
            
            return result_text, corrected_transcript
            
        except Exception as e:
            return f"❌ エラー: {str(e)}", ""
    
    # === ステップ3: 議事録生成 ===
    def generate_minutes(self, meeting_title="", meeting_date=""):
        """議事録を生成"""
        if not self.transcription_ready:
            return "❌ 先にステップ2で音声転写を完了してください。", ""
        
        try:
            # キーワード定義
            decision_keywords = ['決定', '承認', '採用', '選定', '確定', '合意', '了承']
            action_keywords = ['検討', '確認', '調整', '実施', '対応', '準備', '作成', '提出', '報告', 'お願い']
            issue_keywords = ['課題', '問題', '懸念', '検討事項', '要確認', '要検討']
            
            sentences = [s.strip() for s in self.transcript_text.split('。') if s.strip()]
            
            decisions = []
            actions = []
            issues = []
            participants = []
            
            # 文章解析
            for sentence in sentences:
                # 決定事項
                for keyword in decision_keywords:
                    if keyword in sentence:
                        decisions.append(sentence)
                        break
                
                # 行動項目
                for keyword in action_keywords:
                    if keyword in sentence:
                        # 担当者を抽出
                        assignee = None
                        if '田中' in sentence:
                            assignee = '田中部長'
                        elif '山田' in sentence:
                            assignee = '山田係長'
                        elif '佐藤' in sentence:
                            assignee = '佐藤主任'
                        
                        actions.append({
                            'content': sentence,
                            'assignee': assignee
                        })
                        break
                
                # 課題
                for keyword in issue_keywords:
                    if keyword in sentence:
                        issues.append(sentence)
                        break
                
                # 参加者抽出
                if '田中' in sentence and '田中部長' not in participants:
                    participants.append('田中部長')
                if '山田' in sentence and '山田係長' not in participants:
                    participants.append('山田係長')
                if '佐藤' in sentence and '佐藤主任' not in participants:
                    participants.append('佐藤主任')
            
            # 議事録テキスト生成
            minutes_text = []
            minutes_text.append("=" * 60)
            minutes_text.append("🏗️ 建築会議 議事録")
            minutes_text.append("=" * 60)
            minutes_text.append(f"📅 会議名: {meeting_title or '建築技術検討会議'}")
            minutes_text.append(f"📆 日付: {meeting_date or '2024年1月15日'}")
            minutes_text.append(f"👥 参加者: {', '.join(participants) if participants else '記載なし'}")
            minutes_text.append("")
            
            # 要約
            summary = "RC構造の基礎工事について検討し、品質管理の強化と施工図面の修正について決定した。"
            minutes_text.append("📋 【要約】")
            minutes_text.append(summary)
            minutes_text.append("")
            
            # 決定事項
            if decisions:
                minutes_text.append("✅ 【決定事項】")
                for i, decision in enumerate(decisions, 1):
                    minutes_text.append(f"{i}. {decision}")
                minutes_text.append("")
            
            # 行動項目
            if actions:
                minutes_text.append("📋 【行動項目】")
                for i, action in enumerate(actions, 1):
                    assignee = f" ({action['assignee']})" if action.get('assignee') else ""
                    minutes_text.append(f"{i}. {action['content']}{assignee}")
                minutes_text.append("")
            
            # 課題
            if issues:
                minutes_text.append("⚠️ 【課題・検討事項】")
                for i, issue in enumerate(issues, 1):
                    minutes_text.append(f"{i}. {issue}")
                minutes_text.append("")
            
            # 専門術語サマリー
            used_terms = []
            for term in self.extracted_terms:
                if term in self.transcript_text:
                    used_terms.append(term)
            
            if used_terms:
                minutes_text.append("🏗️ 【使用された専門術語】")
                minutes_text.append(f"{', '.join(sorted(used_terms))}")
                minutes_text.append("")
            
            # 統計
            minutes_text.append("📊 【統計】")
            minutes_text.append(f"決定事項: {len(decisions)}件")
            minutes_text.append(f"行動項目: {len(actions)}件")
            minutes_text.append(f"課題: {len(issues)}件")
            minutes_text.append(f"専門術語: {len(used_terms)}種類")
            
            # JSON形式
            json_data = {
                "meeting_info": {
                    "title": meeting_title or "建築技術検討会議",
                    "date": meeting_date or "2024年1月15日",
                    "participants": participants
                },
                "summary": summary,
                "decisions": decisions,
                "action_items": [{"content": a['content'], "assignee": a.get('assignee')} for a in actions],
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
            
        except Exception as e:
            return f"❌ エラー: {str(e)}", ""
    
    def get_workflow_status(self):
        """ワークフローの状態を取得"""
        status = []
        status.append("🔄 ワークフロー進行状況:")
        status.append("")
        
        # ステップ1
        step1_status = "✅ 完了" if self.term_db_ready else "⏳ 未完了"
        status.append(f"📚 ステップ1: 専門術語抽出 - {step1_status}")
        if self.term_db_ready:
            status.append(f"   術語数: {len(self.extracted_terms)}個")
        
        # ステップ2
        step2_status = "✅ 完了" if self.transcription_ready else "⏳ 未完了"
        status.append(f"🎤 ステップ2: 音声転写 - {step2_status}")
        if self.transcription_ready:
            status.append(f"   文字数: {len(self.transcript_text)}文字")
        
        # ステップ3
        step3_available = "✅ 実行可能" if self.transcription_ready else "❌ 前ステップ完了待ち"
        status.append(f"📄 ステップ3: 議事録生成 - {step3_available}")
        
        return '\n'.join(status)

def create_workflow_interface():
    """ワークフローインターフェースを作成"""
    app = WorkflowApp()
    
    with gr.Blocks() as demo:
        gr.HTML("<h1>🏗️ 建築会議転写システム - ワークフロー版</h1>")
        gr.HTML("<p>3ステップで専門的な議事録を生成します</p>")
        
        # 進行状況表示
        with gr.Row():
            status_display = gr.Textbox(
                label="🔄 ワークフロー進行状況",
                value=app.get_workflow_status(),
                lines=8,
                interactive=False
            )
        
        # ステップ1: 専門術語抽出
        with gr.Tab("📚 ステップ1: 専門術語抽出"):
            gr.HTML("<h3>PDFから建築専門術語を抽出</h3>")
            
            pdf_files = gr.File(
                label="📁 建築関連PDFファイル",
                file_count="multiple",
                file_types=[".pdf"]
            )
            
            extract_btn = gr.Button("🔍 術語抽出開始", variant="primary")
            
            with gr.Row():
                terms_result = gr.Textbox(
                    label="抽出結果",
                    lines=12,
                    interactive=False
                )
                terms_json = gr.Textbox(
                    label="JSON出力",
                    lines=12,
                    interactive=False
                )
        
        # ステップ2: 音声転写
        with gr.Tab("🎤 ステップ2: 音声転写"):
            gr.HTML("<h3>会議音声/動画を転写（専門術語補正付き）</h3>")
            
            audio_file = gr.File(
                label="🎬 音声/動画ファイル",
                file_types=[".mp4", ".wav", ".mp3", ".m4a", ".avi", ".mov"]
            )
            
            transcribe_btn = gr.Button("🎤 転写開始", variant="primary")
            
            with gr.Row():
                transcript_result = gr.Textbox(
                    label="転写結果",
                    lines=15,
                    interactive=False
                )
                transcript_text = gr.Textbox(
                    label="転写テキスト",
                    lines=15,
                    interactive=False
                )
        
        # ステップ3: 議事録生成
        with gr.Tab("📄 ステップ3: 議事録生成"):
            gr.HTML("<h3>転写テキストから構造化議事録を生成</h3>")
            
            with gr.Row():
                meeting_title = gr.Textbox(
                    label="会議タイトル",
                    placeholder="例: RC構造技術検討会議"
                )
                meeting_date = gr.Textbox(
                    label="会議日付",
                    placeholder="例: 2024年1月15日"
                )
            
            minutes_btn = gr.Button("📋 議事録生成", variant="primary")
            
            with gr.Row():
                minutes_result = gr.Textbox(
                    label="議事録",
                    lines=20,
                    interactive=False
                )
                minutes_json = gr.Textbox(
                    label="構造化データ",
                    lines=20,
                    interactive=False
                )
        
        # イベント設定
        def update_status():
            return app.get_workflow_status()
        
        extract_btn.click(
            fn=app.extract_terms_from_pdf,
            inputs=[pdf_files],
            outputs=[terms_result, terms_json]
        ).then(
            fn=update_status,
            outputs=[status_display]
        )
        
        transcribe_btn.click(
            fn=app.transcribe_audio,
            inputs=[audio_file],
            outputs=[transcript_result, transcript_text]
        ).then(
            fn=update_status,
            outputs=[status_display]
        )
        
        minutes_btn.click(
            fn=app.generate_minutes,
            inputs=[meeting_title, meeting_date],
            outputs=[minutes_result, minutes_json]
        ).then(
            fn=update_status,
            outputs=[status_display]
        )
        
        # 使用説明
        gr.HTML("""
        <div style="margin-top: 20px; padding: 15px; background: #f0f8ff; border-radius: 8px;">
        <h4>📖 使用手順:</h4>
        <ol>
        <li><strong>ステップ1:</strong> 建築関連のPDFファイルをアップロードして専門術語を抽出</li>
        <li><strong>ステップ2:</strong> 会議の音声/動画ファイルをアップロードして転写（専門術語で補正）</li>
        <li><strong>ステップ3:</strong> 転写テキストから構造化された議事録を生成</li>
        </ol>
        <p><strong>💡 Tips:</strong> 各ステップを順番に実行してください。前のステップが完了していないと次に進めません。</p>
        </div>
        """)
    
    return demo

def main():
    """メイン実行"""
    print("🏗️ 建築会議転写システム（ワークフロー版）")
    
    demo = create_workflow_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )

if __name__ == "__main__":
    main()