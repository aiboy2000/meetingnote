"""
音声転写器
Whisperを使用した音声転写と専門術語補正
"""

import whisper
import torch
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
from .vector_db import VectorDB

logger = logging.getLogger(__name__)

class BuildingTranscriber:
    def __init__(self, model_size: str = "base", vector_db: Optional[VectorDB] = None):
        """
        建築専門音声転写器を初期化
        
        Args:
            model_size: Whisperモデルサイズ (tiny, base, small, medium, large)
            vector_db: 専門術語検索用のベクターDB
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Whisperモデルをロード
        logger.info(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size, device=self.device)
        
        # ベクターDBを設定
        self.vector_db = vector_db
        
        # 建築専門用語の一般的な誤認識パターン
        self.correction_patterns = {
            r'アールシー': 'RC',
            r'ピーシー': 'PC', 
            r'エスアールシー': 'SRC',
            r'てっきん': '鉄筋',
            r'こんくりーと': 'コンクリート',
            r'きそ': '基礎',
            r'せこう': '施工',
            r'ずめん': '図面',
            r'けんせつ': '建設',
            r'こうじ': '工事',
        }
    
    def transcribe_audio(self, audio_path: str, language: str = "ja") -> Dict:
        """
        音声ファイルを転写
        
        Args:
            audio_path: 音声ファイルパス
            language: 言語コード
            
        Returns:
            転写結果辞書
        """
        logger.info(f"Transcribing audio: {audio_path}")
        
        try:
            # Whisperで転写
            result = self.model.transcribe(
                audio_path, 
                language=language,
                task="transcribe",
                verbose=True
            )
            
            # 結果を処理
            processed_result = self._process_transcription(result)
            
            logger.info(f"Transcription completed. Duration: {result.get('duration', 0):.2f}s")
            return processed_result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {"text": "", "segments": [], "language": language}
    
    def _process_transcription(self, raw_result: Dict) -> Dict:
        """
        転写結果を処理（専門術語補正など）
        
        Args:
            raw_result: Whisperの生の転写結果
            
        Returns:
            処理済み転写結果
        """
        # テキスト全体を補正
        corrected_text = self._correct_technical_terms(raw_result["text"])
        
        # セグメント単位でも補正
        corrected_segments = []
        for segment in raw_result.get("segments", []):
            corrected_segment = segment.copy()
            corrected_segment["text"] = self._correct_technical_terms(segment["text"])
            corrected_segments.append(corrected_segment)
        
        return {
            "text": corrected_text,
            "segments": corrected_segments,
            "language": raw_result.get("language", "ja"),
            "duration": raw_result.get("duration", 0)
        }
    
    def _correct_technical_terms(self, text: str) -> str:
        """
        専門術語を補正
        
        Args:
            text: 元のテキスト
            
        Returns:
            補正されたテキスト
        """
        corrected = text
        
        # 基本的なパターン補正
        for pattern, replacement in self.correction_patterns.items():
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
        
        # ベクターDBを使った高度な補正
        if self.vector_db:
            corrected = self._vector_based_correction(corrected)
        
        return corrected
    
    def _vector_based_correction(self, text: str) -> str:
        """
        ベクターDBを使用した専門術語補正
        
        Args:
            text: 補正対象テキスト
            
        Returns:
            補正されたテキスト
        """
        # 単語単位で分割
        words = re.findall(r'\S+', text)
        corrected_words = []
        
        for word in words:
            # 専門術語の候補を検索
            candidates = self.vector_db.fuzzy_search(word, k=3)
            
            if candidates and candidates[0][1] > 0.8:  # 高い類似度の場合のみ補正
                best_match = candidates[0][0]
                corrected_words.append(best_match)
                logger.debug(f"Corrected: {word} -> {best_match}")
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    def transcribe_video(self, video_path: str) -> Dict:
        """
        動画ファイルから音声を抽出して転写
        
        Args:
            video_path: 動画ファイルパス
            
        Returns:
            転写結果
        """
        # 動画から音声を抽出（ffmpeg使用）
        audio_path = self._extract_audio_from_video(video_path)
        
        try:
            # 音声を転写
            result = self.transcribe_audio(audio_path)
            return result
        finally:
            # 一時音声ファイルを削除
            if Path(audio_path).exists():
                Path(audio_path).unlink()
    
    def _extract_audio_from_video(self, video_path: str) -> str:
        """
        動画から音声を抽出
        
        Args:
            video_path: 動画ファイルパス
            
        Returns:
            抽出された音声ファイルパス
        """
        import ffmpeg
        
        video_path = Path(video_path)
        audio_path = video_path.parent / f"{video_path.stem}_audio.wav"
        
        try:
            (
                ffmpeg
                .input(str(video_path))
                .output(str(audio_path), acodec='pcm_s16le', ac=1, ar='16000')
                .overwrite_output()
                .run(quiet=True)
            )
            return str(audio_path)
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            raise
    
    def batch_transcribe(self, file_paths: List[str]) -> Dict[str, Dict]:
        """
        複数ファイルを一括転写
        
        Args:
            file_paths: ファイルパスのリスト
            
        Returns:
            ファイルパス別の転写結果辞書
        """
        results = {}
        
        for file_path in file_paths:
            logger.info(f"Processing: {file_path}")
            
            try:
                if file_path.lower().endswith(('.mp4', '.avi', '.mov')):
                    result = self.transcribe_video(file_path)
                else:
                    result = self.transcribe_audio(file_path)
                
                results[file_path] = result
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results[file_path] = {"error": str(e)}
        
        return results

def main():
    """テスト実行"""
    # サンプルテキストで術語補正をテスト
    transcriber = BuildingTranscriber()
    
    sample_text = "てっきんこんくりーとこうぞうのきそこうじにおいて、アールシーざいりょうのひんしつかんりがじゅうようである。"
    corrected = transcriber._correct_technical_terms(sample_text)
    
    print(f"元のテキスト: {sample_text}")
    print(f"補正後: {corrected}")

if __name__ == "__main__":
    main()