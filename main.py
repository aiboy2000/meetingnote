"""
建築業務会議転写システム メインアプリケーション
Gradioを使用したWebインターフェース
"""

import gradio as gr
import logging
import json
import os
from pathlib import Path
from typing import Optional, Tuple, Dict

# 相対インポートに修正
from src.term_extractor import TermExtractor
from src.vector_db import VectorDB
from src.transcriber import BuildingTranscriber
from src.minutes_generator import MinutesGenerator
from src.tagger import SmartTagger

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeetingTranscriberApp:
    def __init__(self):
        """アプリケーションを初期化"""
        self.term_extractor = TermExtractor()
        
        # ベクターDBを安全に初期化
        try:
            self.vector_db = VectorDB("all-MiniLM-L6-v2")  # 軽量な英語モデルを使用
        except Exception as e:
            logger.error(f"VectorDB initialization failed: {e}")
            self.vector_db = None
            
        self.transcriber = None
        self.minutes_generator = MinutesGenerator()
        self.tagger = SmartTagger()
        
        # データディレクトリを作成
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 専門術語データベースの状態
        self.term_db_loaded = False
    
    def build_term_database(self, pdf_files) -> str:
        """
        PDFファイルから専門術語データベースを構築
        
        Args:
            pdf_files: アップロードされたPDFファイルのリスト
            
        Returns:
            結果メッセージ
        """
        try:
            if not pdf_files:
                return "PDFファイルが選択されていません。"
            
            # 一時ディレクトリにPDFを保存
            temp_dir = self.data_dir / "temp_pdfs"
            temp_dir.mkdir(exist_ok=True)
            
            # PDFファイルを保存
            pdf_paths = []
            for pdf_file in pdf_files:
                pdf_path = temp_dir / Path(pdf_file.name).name
                # ファイルをコピー
                import shutil
                shutil.copy2(pdf_file.name, pdf_path)
                pdf_paths.append(str(pdf_path))
            
            # 専門術語を抽出
            logger.info("Extracting terms from PDFs...")
            all_terms = set()
            for pdf_path in pdf_paths:
                terms = self.term_extractor.extract_from_pdf(pdf_path)
                all_terms.update(terms)
            
            logger.info(f"Extracted {len(all_terms)} unique terms")
            
            # ベクターデータベースを構築
            if all_terms and self.vector_db:
                logger.info("Building vector database...")
                self.vector_db.build_index(list(all_terms))
                
                # インデックスを保存
                index_dir = self.data_dir / "vector_index"
                self.vector_db.save_index(str(index_dir))
                
                self.term_db_loaded = True
                
                # クリーンアップ
                shutil.rmtree(temp_dir)
                
                return f"専門術語データベースを構築しました。\n抽出された術語数: {len(all_terms)}"
            else:
                return "専門術語を抽出できませんでした。"
                
        except Exception as e:
            logger.error(f"Error building term database: {e}")
            return f"エラーが発生しました: {str(e)}"
    
    def load_existing_database(self) -> str:
        """既存の専門術語データベースを読み込み"""
        try:
            if not self.vector_db:
                return "ベクターデータベースが初期化されていません。"
                
            index_dir = self.data_dir / "vector_index"
            if index_dir.exists():
                self.vector_db.load_index(str(index_dir))
                self.term_db_loaded = True
                return f"既存のデータベースを読み込みました。\n術語数: {len(self.vector_db.terms)}"
            else:
                return "既存のデータベースが見つかりません。"
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return f"エラーが発生しました: {str(e)}"
    
    def transcribe_meeting(self, audio_file, model_size: str = "base") -> Tuple[str, str]:
        """
        会議音声を転写
        
        Args:
            audio_file: 音声ファイル
            model_size: Whisperモデルサイズ
            
        Returns:
            (転写テキスト, ステータスメッセージ)
        """
        try:
            if not audio_file:
                return "", "音声ファイルが選択されていません。"
            
            # 転写器を初期化（初回のみ）
            if self.transcriber is None:
                vector_db = self.vector_db if self.term_db_loaded else None
                self.transcriber = BuildingTranscriber(model_size, vector_db)
            
            # 転写実行
            logger.info(f"Transcribing audio: {audio_file.name}")
            
            # ファイル拡張子をチェック
            file_path = audio_file.name
            if file_path.lower().endswith(('.mp4', '.avi', '.mov')):
                result = self.transcriber.transcribe_video(file_path)
            else:
                result = self.transcriber.transcribe_audio(file_path)
            
            transcript = result.get("text", "")
            duration = result.get("duration", 0)
            
            status = f"転写完了。\n音声時間: {duration:.1f}秒\n文字数: {len(transcript)}"
            
            return transcript, status
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return "", f"エラーが発生しました: {str(e)}"
    
    def generate_minutes(self, transcript: str, meeting_title: str = "", meeting_date: str = "") -> Tuple[str, str]:
        """
        議事録を生成
        
        Args:
            transcript: 転写テキスト
            meeting_title: 会議タイトル
            meeting_date: 会議日付
            
        Returns:
            (議事録JSON, テキスト形式議事録)
        """
        try:
            if not transcript.strip():
                return "", "転写テキストが入力されていません。"
            
            # 会議情報を準備
            meeting_info = {}
            if meeting_title:
                meeting_info["title"] = meeting_title
            if meeting_date:
                meeting_info["date"] = meeting_date
            
            # 議事録を生成
            logger.info("Generating minutes...")
            minutes = self.minutes_generator.generate_minutes(transcript, meeting_info)
            
            # タグ付け
            tagged_minutes = self.tagger.tag_minutes(minutes)
            
            # JSON形式
            json_output = json.dumps(tagged_minutes, ensure_ascii=False, indent=2)
            
            # テキスト形式
            text_output = self.minutes_generator._format_minutes_text(tagged_minutes)
            
            return json_output, text_output
            
        except Exception as e:
            logger.error(f"Error generating minutes: {e}")
            return "", f"エラーが発生しました: {str(e)}"
    
    def search_terms(self, query: str, k: int = 5) -> str:
        """
        専門術語を検索
        
        Args:
            query: 検索クエリ
            k: 返す結果数
            
        Returns:
            検索結果
        """
        try:
            if not self.vector_db:
                return "ベクターデータベースが初期化されていません。"
                
            if not self.term_db_loaded:
                return "専門術語データベースが読み込まれていません。"
            
            if not query.strip():
                return "検索クエリを入力してください。"
            
            # 検索実行
            results = self.vector_db.fuzzy_search(query, k)
            
            if results:
                output_lines = [f"'{query}' の検索結果:"]
                for i, (term, score) in enumerate(results, 1):
                    output_lines.append(f"{i}. {term} (類似度: {score:.3f})")
                return "\n".join(output_lines)
            else:
                return "該当する術語が見つかりませんでした。"
                
        except Exception as e:
            logger.error(f"Error searching terms: {e}")
            return f"エラーが発生しました: {str(e)}"
    
    def create_interface(self):
        """Gradioインターフェースを作成"""
        
        with gr.Blocks(title="建築業務会議転写システム") as app:
            gr.Markdown("# 建築業務会議転写システム")
            gr.Markdown("専門術語データベースを使用した高精度な会議転写と議事録生成")
            
            with gr.Tabs():
                # タブ1: 専門術語データベース構築
                with gr.TabItem("専門術語データベース"):
                    gr.Markdown("## 専門術語データベースの構築")
                    
                    pdf_files = gr.File(
                        label="専門術語PDFファイル",
                        file_count="multiple",
                        file_types=[".pdf"]
                    )
                    
                    with gr.Row():
                        build_btn = gr.Button("データベース構築", variant="primary")
                        load_btn = gr.Button("既存DB読み込み")
                    
                    db_status = gr.Textbox(
                        label="構築状況",
                        lines=3,
                        interactive=False
                    )
                    
                    # 術語検索テスト
                    gr.Markdown("### 術語検索テスト")
                    with gr.Row():
                        search_query = gr.Textbox(
                            label="検索クエリ",
                            placeholder="例: コンクリート"
                        )
                        search_btn = gr.Button("検索")
                    
                    search_results = gr.Textbox(
                        label="検索結果",
                        lines=5,
                        interactive=False
                    )
                
                # タブ2: 音声転写
                with gr.TabItem("音声転写"):
                    gr.Markdown("## 会議音声の転写")
                    
                    audio_file = gr.File(
                        label="音声/動画ファイル",
                        file_types=[".wav", ".mp3", ".m4a", ".mp4", ".avi", ".mov"]
                    )
                    
                    model_size = gr.Dropdown(
                        choices=["tiny", "base", "small", "medium", "large"],
                        value="base",
                        label="Whisperモデルサイズ"
                    )
                    
                    transcribe_btn = gr.Button("転写開始", variant="primary")
                    
                    transcribe_status = gr.Textbox(
                        label="転写状況",
                        lines=2,
                        interactive=False
                    )
                    
                    transcript_output = gr.Textbox(
                        label="転写結果",
                        lines=10,
                        placeholder="転写されたテキストがここに表示されます..."
                    )
                
                # タブ3: 議事録生成
                with gr.TabItem("議事録生成"):
                    gr.Markdown("## 議事録の生成とタグ付け")
                    
                    with gr.Row():
                        meeting_title = gr.Textbox(
                            label="会議タイトル",
                            placeholder="例: RC構造検討会議"
                        )
                        meeting_date = gr.Textbox(
                            label="会議日付",
                            placeholder="例: 2024-01-15"
                        )
                    
                    transcript_input = gr.Textbox(
                        label="転写テキスト",
                        lines=8,
                        placeholder="転写テキストを入力してください..."
                    )
                    
                    generate_btn = gr.Button("議事録生成", variant="primary")
                    
                    with gr.Row():
                        minutes_json = gr.Textbox(
                            label="議事録 (JSON形式)",
                            lines=15,
                            interactive=False
                        )
                        minutes_text = gr.Textbox(
                            label="議事録 (テキスト形式)",
                            lines=15,
                            interactive=False
                        )
            
            # イベントハンドラ
            build_btn.click(
                fn=self.build_term_database,
                inputs=[pdf_files],
                outputs=[db_status]
            )
            
            load_btn.click(
                fn=self.load_existing_database,
                outputs=[db_status]
            )
            
            search_btn.click(
                fn=self.search_terms,
                inputs=[search_query],
                outputs=[search_results]
            )
            
            transcribe_btn.click(
                fn=self.transcribe_meeting,
                inputs=[audio_file, model_size],
                outputs=[transcript_output, transcribe_status]
            )
            
            generate_btn.click(
                fn=self.generate_minutes,
                inputs=[transcript_input, meeting_title, meeting_date],
                outputs=[minutes_json, minutes_text]
            )
        
        return app

def main():
    """メイン実行関数"""
    # アプリケーションを初期化
    app_instance = MeetingTranscriberApp()
    
    # 既存のデータベースがあれば自動読み込み
    try:
        app_instance.load_existing_database()
        logger.info("Existing database loaded automatically")
    except:
        logger.info("No existing database found")
    
    # Gradioインターフェースを起動
    interface = app_instance.create_interface()
    
    # アプリケーションを起動
    interface.launch(
        server_name="0.0.0.0",  # 外部からアクセス可能
        server_port=7860,
        share=False,  # パブリック共有は無効
        debug=True
    )

if __name__ == "__main__":
    main()