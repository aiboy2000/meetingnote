"""
ベクターデータベース
専門術語の高速検索のためのFaiss実装
"""

import numpy as np
import faiss
import pickle
import json
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self, model_name: str = "sonoisa/sentence-bert-base-ja-mean-tokens-v2"):
        """
        ベクターデータベースを初期化
        
        Args:
            model_name: SentenceTransformerのモデル名
        """
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.terms = []
        self.term_metadata = {}
        self.dimension = None
    
    def build_index(self, terms: List[str], metadata: Dict[str, Dict] = None):
        """
        術語リストからFaissインデックスを構築
        
        Args:
            terms: 術語のリスト
            metadata: 各術語の追加情報
        """
        logger.info(f"Building index for {len(terms)} terms...")
        
        # ベクトル化
        vectors = self.model.encode(terms, show_progress_bar=True)
        self.dimension = vectors.shape[1]
        
        # Faissインデックス作成（Inner Product用）
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # ベクトルを正規化してコサイン類似度検索を可能にする
        faiss.normalize_L2(vectors)
        
        # インデックスに追加
        self.index.add(vectors.astype('float32'))
        
        # 術語とメタデータを保存
        self.terms = terms
        self.term_metadata = metadata or {}
        
        logger.info(f"Index built successfully with dimension {self.dimension}")
    
    def search(self, query: str, k: int = 5, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """
        クエリに類似する術語を検索
        
        Args:
            query: 検索クエリ
            k: 返す結果数
            threshold: 類似度の閾値
            
        Returns:
            (術語, スコア) のタプルのリスト
        """
        if self.index is None:
            logger.error("Index not built yet")
            return []
        
        # クエリをベクトル化
        query_vector = self.model.encode([query])
        faiss.normalize_L2(query_vector)
        
        # 検索実行
        scores, indices = self.index.search(query_vector.astype('float32'), k)
        
        # 結果をフィルタリング
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if score >= threshold and idx < len(self.terms):
                term = self.terms[idx]
                results.append((term, float(score)))
        
        return results
    
    def fuzzy_search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        ファジー検索（文字列の部分一致も考慮）
        
        Args:
            query: 検索クエリ
            k: 返す結果数
            
        Returns:
            (術語, スコア) のタプルのリスト
        """
        # ベクトル検索
        vector_results = self.search(query, k)
        
        # 文字列の部分一致検索
        string_results = []
        query_lower = query.lower()
        
        for term in self.terms:
            if query_lower in term.lower() or term.lower() in query_lower:
                # 文字列一致度を計算（簡易版）
                match_score = min(len(query), len(term)) / max(len(query), len(term))
                string_results.append((term, match_score))
        
        # 結果をマージして重複を除去
        all_results = {}
        
        # ベクトル検索結果を追加
        for term, score in vector_results:
            all_results[term] = max(all_results.get(term, 0), score)
        
        # 文字列検索結果を追加（スコアを調整）
        for term, score in string_results:
            adjusted_score = score * 0.8  # 文字列マッチのスコアを少し下げる
            all_results[term] = max(all_results.get(term, 0), adjusted_score)
        
        # スコア順にソート
        sorted_results = sorted(all_results.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_results[:k]
    
    def save_index(self, index_dir: str):
        """インデックスをファイルに保存"""
        index_dir = Path(index_dir)
        index_dir.mkdir(parents=True, exist_ok=True)
        
        # Faissインデックスを保存
        faiss.write_index(self.index, str(index_dir / "faiss.index"))
        
        # 術語リストを保存
        with open(index_dir / "terms.pkl", 'wb') as f:
            pickle.dump(self.terms, f)
        
        # メタデータを保存
        with open(index_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(self.term_metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Index saved to {index_dir}")
    
    def load_index(self, index_dir: str):
        """ファイルからインデックスを読み込み"""
        index_dir = Path(index_dir)
        
        # Faissインデックスを読み込み
        self.index = faiss.read_index(str(index_dir / "faiss.index"))
        
        # 術語リストを読み込み
        with open(index_dir / "terms.pkl", 'rb') as f:
            self.terms = pickle.load(f)
        
        # メタデータを読み込み
        with open(index_dir / "metadata.json", 'r', encoding='utf-8') as f:
            self.term_metadata = json.load(f)
        
        self.dimension = self.index.d
        logger.info(f"Index loaded from {index_dir}")
    
    def get_term_info(self, term: str) -> Dict:
        """術語の詳細情報を取得"""
        return self.term_metadata.get(term, {})

def main():
    """テスト実行"""
    # サンプル術語でテスト
    sample_terms = [
        "鉄筋コンクリート",
        "基礎工事",
        "施工管理",
        "品質管理",
        "安全管理",
        "RC構造",
        "PC構造",
        "SRC構造"
    ]
    
    # ベクターDBを構築
    db = VectorDB()
    db.build_index(sample_terms)
    
    # 検索テスト
    results = db.search("コンクリート", k=3)
    print(f"'コンクリート'の検索結果: {results}")
    
    # ファジー検索テスト
    fuzzy_results = db.fuzzy_search("RC", k=3)
    print(f"'RC'のファジー検索結果: {fuzzy_results}")

if __name__ == "__main__":
    main()