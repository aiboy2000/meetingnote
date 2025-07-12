"""
专业术语提取器
从PDF文档中提取建筑专业术语并构建知识库
"""

import pdfplumber
import re
import json
from pathlib import Path
from typing import List, Dict, Set
import logging

logger = logging.getLogger(__name__)

class TermExtractor:
    def __init__(self):
        # 建筑专业术语的常见模式
        self.term_patterns = [
            r'[A-Z]{2,}',  # 大写缩写 (RC, PC等)
            r'[\u4e00-\u9faf]{2,}工事',  # XX工事
            r'[\u4e00-\u9faf]{2,}材料',  # XX材料
            r'[\u4e00-\u9faf]{2,}構造',  # XX構造
            r'[\u4e00-\u9faf]{2,}設備',  # XX設備
            r'[\u4e00-\u9faf]{2,}管理',  # XX管理
            r'コンクリート[^\s]*',  # コンクリート関連
            r'鉄筋[^\s]*',  # 鉄筋関連
            r'基礎[^\s]*',  # 基礎関連
            r'施工[^\s]*',  # 施工関連
        ]
        
        # 除外する一般的な単語
        self.exclude_words = {
            '工事', '材料', '構造', '設備', '管理', '施工', '基礎',
            'について', 'により', 'による', 'として', 'までに',
            'ページ', '図面', '参照', '以下', '以上', '記載',
        }
    
    def extract_from_pdf(self, pdf_path: str) -> Set[str]:
        """PDFから専門術語を抽出"""
        terms = set()
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        page_terms = self._extract_terms_from_text(text)
                        terms.update(page_terms)
            
            logger.info(f"Extracted {len(terms)} terms from {pdf_path}")
            return terms
            
        except Exception as e:
            logger.error(f"Error extracting from {pdf_path}: {e}")
            return set()
    
    def _extract_terms_from_text(self, text: str) -> Set[str]:
        """テキストから専門術語を抽出"""
        terms = set()
        
        # パターンマッチングで術語を抽出
        for pattern in self.term_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # クリーニング
                term = self._clean_term(match)
                if self._is_valid_term(term):
                    terms.add(term)
        
        return terms
    
    def _clean_term(self, term: str) -> str:
        """術語をクリーニング"""
        # 前後の空白や記号を除去
        term = re.sub(r'^[^\w\u4e00-\u9faf]+|[^\w\u4e00-\u9faf]+$', '', term)
        return term.strip()
    
    def _is_valid_term(self, term: str) -> bool:
        """有効な術語かチェック"""
        if len(term) < 2:
            return False
        if term in self.exclude_words:
            return False
        if re.match(r'^\d+$', term):  # 数字のみは除外
            return False
        return True
    
    def extract_from_directory(self, pdf_dir: str) -> Dict[str, List[str]]:
        """ディレクトリ内の全PDFから術語を抽出"""
        pdf_dir = Path(pdf_dir)
        all_terms = {}
        
        for pdf_file in pdf_dir.glob("**/*.pdf"):
            terms = self.extract_from_pdf(str(pdf_file))
            all_terms[str(pdf_file)] = list(terms)
        
        return all_terms
    
    def save_terms_to_json(self, terms_dict: Dict[str, List[str]], output_path: str):
        """術語辞書をJSONファイルに保存"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(terms_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Terms saved to {output_path}")

def main():
    """テスト実行"""
    extractor = TermExtractor()
    
    # サンプルテキストでテスト
    sample_text = """
    鉄筋コンクリート構造の基礎工事において、RC材料の品質管理が重要である。
    施工図面に基づき、NET査定を実施する必要がある。
    """
    
    terms = extractor._extract_terms_from_text(sample_text)
    print(f"抽出された術語: {terms}")

if __name__ == "__main__":
    main()