"""
PDF専門術語抽出器
建築関連PDFから専門術語を抽出
"""

import re
import json
from pathlib import Path
from collections import Counter
import logging

# 基本的なログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFTermExtractor:
    def __init__(self):
        """PDF術語抽出器を初期化"""
        
        # 建築専門用語のパターン定義
        self.term_patterns = {
            # 構造関連
            "構造": [
                r'RC[造構法工事]*', r'PC[造構法工事]*', r'SRC[造構法工事]*',
                r'鉄筋[コンクリート造構法]*', r'鉄[骨筋][造構法]*',
                r'木[造構法]*', r'鋼[造構法]*', r'混合構造',
                r'基礎[工事構造]*', r'杭[工事基礎]*', r'直接基礎',
                r'梁[構造]*', r'柱[構造]*', r'スラブ[構造]*',
                r'壁[構造]*', r'床[構造]*', r'屋根[構造]*'
            ],
            
            # 工事関連
            "工事": [
                r'基礎工事', r'杭工事', r'土工事', r'躯体工事',
                r'型枠工事', r'配筋工事', r'コンクリート工事',
                r'鉄骨工事', r'防水工事', r'仕上工事',
                r'設備工事', r'電気工事', r'機械工事',
                r'外構工事', r'解体工事'
            ],
            
            # 材料関連
            "材料": [
                r'コンクリート[強度種類]*', r'鉄筋[材料種類]*',
                r'鋼[材料種類]*', r'木[材料種類]*',
                r'セメント[種類]*', r'骨材[種類]*',
                r'添加[剤材料]*', r'防水[材料]*',
                r'断熱[材料]*', r'仕上[材料]*'
            ],
            
            # 管理関連
            "管理": [
                r'品質管理', r'安全管理', r'工程管理', r'施工管理',
                r'原価管理', r'環境管理', r'労務管理',
                r'検査[方法種類]*', r'試験[方法種類]*',
                r'測定[方法種類]*', r'監理[業務]*'
            ],
            
            # 設計関連
            "設計": [
                r'構造設計', r'意匠設計', r'設備設計',
                r'構造計算', r'応力解析', r'耐震設計',
                r'図面[種類]*', r'仕様[書類]*', r'詳細図',
                r'施工図[面]*', r'竣工図[面]*'
            ],
            
            # 法規関連
            "法規": [
                r'建築基準法', r'消防法', r'都市計画法',
                r'確認申請', r'建築許可', r'完了検査',
                r'検査済証', r'建築確認', r'用途変更',
                r'構造計算[適合判定]*'
            ]
        }
        
        # 除外する一般的な語句
        self.exclude_words = {
            'について', 'により', 'による', 'として', 'ための',
            'である', 'であり', 'です', 'ます', 'した',
            'する', 'され', 'など', 'また', 'さらに',
            'ページ', '図面', '参照', '以下', '以上', '記載',
            '場合', '時期', '方法', '状況', '条件'
        }
    
    def extract_from_text(self, text: str) -> dict:
        """テキストから専門術語を抽出"""
        extracted_terms = {}
        
        for category, patterns in self.term_patterns.items():
            category_terms = set()
            
            for pattern in patterns:
                # パターンマッチング
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # クリーニング
                    cleaned_term = self._clean_term(match)
                    if self._is_valid_term(cleaned_term):
                        category_terms.add(cleaned_term)
            
            extracted_terms[category] = sorted(list(category_terms))
        
        return extracted_terms
    
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
    
    def extract_from_sample_pdfs(self, pdf_files) -> dict:
        """サンプルPDFファイルから術語を抽出（デモ用）"""
        
        # 実際の実装ではpdfplumberやPyPDF2を使用
        # ここではデモ用のサンプルデータを返す
        
        sample_terms = {
            "構造": [
                "RC造", "PC造", "SRC造", "鉄筋コンクリート造",
                "基礎工事", "杭工事", "直接基礎", "梁構造",
                "柱構造", "スラブ構造", "耐力壁"
            ],
            "工事": [
                "型枠工事", "配筋工事", "コンクリート工事", 
                "躯体工事", "仕上工事", "防水工事",
                "鉄骨工事", "設備工事"
            ],
            "材料": [
                "コンクリート強度", "鉄筋材料", "セメント種類",
                "骨材種類", "添加剤", "防水材料", "断熱材料"
            ],
            "管理": [
                "品質管理", "安全管理", "工程管理", "施工管理",
                "検査方法", "試験方法", "測定方法"
            ],
            "設計": [
                "構造設計", "意匠設計", "設備設計", "構造計算",
                "耐震設計", "施工図面", "仕様書", "詳細図"
            ],
            "法規": [
                "建築基準法", "確認申請", "完了検査",
                "検査済証", "建築確認", "構造計算適合判定"
            ]
        }
        
        # ファイル数に応じて術語数を調整
        if pdf_files:
            file_count = len(pdf_files)
            logger.info(f"Processing {file_count} PDF files")
            
            # ファイル名から追加の術語を推測
            additional_terms = set()
            for pdf_file in pdf_files:
                filename = pdf_file.name.lower()
                
                # ファイル名に含まれるキーワードから術語を推測
                if 'rc' in filename or 'コンクリート' in filename:
                    additional_terms.update(['RC構造', '鉄筋コンクリート', 'コンクリート強度'])
                if '基礎' in filename:
                    additional_terms.update(['基礎工事', '杭基礎', '直接基礎'])
                if '施工' in filename:
                    additional_terms.update(['施工管理', '施工図面', '施工計画'])
                if '品質' in filename:
                    additional_terms.update(['品質管理', '品質検査', '品質試験'])
                if '安全' in filename:
                    additional_terms.update(['安全管理', '安全計画', '安全教育'])
            
            # 追加術語をサンプルに統合
            if additional_terms:
                for term in additional_terms:
                    # 適切なカテゴリに分類
                    if '構造' in term or 'RC' in term or 'コンクリート' in term:
                        sample_terms["構造"].append(term)
                    elif '工事' in term:
                        sample_terms["工事"].append(term)
                    elif '管理' in term:
                        sample_terms["管理"].append(term)
                    elif '設計' in term or '図面' in term:
                        sample_terms["設計"].append(term)
        
        # 重複を除去
        for category in sample_terms:
            sample_terms[category] = sorted(list(set(sample_terms[category])))
        
        return sample_terms
    
    def save_terms_to_json(self, terms_dict: dict, output_path: str):
        """術語辞書をJSONファイルに保存"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(terms_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Terms saved to {output_path}")
    
    def load_terms_from_json(self, json_path: str) -> dict:
        """JSONファイルから術語辞書を読み込み"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                terms_dict = json.load(f)
            logger.info(f"Terms loaded from {json_path}")
            return terms_dict
        except FileNotFoundError:
            logger.warning(f"File not found: {json_path}")
            return {}
    
    def get_all_terms_flat(self, terms_dict: dict) -> list:
        """カテゴリ分けされた術語を平坦なリストに変換"""
        all_terms = []
        for category_terms in terms_dict.values():
            all_terms.extend(category_terms)
        return sorted(list(set(all_terms)))

def test_pdf_extractor():
    """PDF抽出器のテスト"""
    print("=== PDF専門術語抽出器テスト ===")
    
    extractor = PDFTermExtractor()
    
    # サンプルテキストでテスト
    sample_text = """
    鉄筋コンクリート造（RC造）の基礎工事において、コンクリートの品質管理が重要である。
    構造設計に基づき、配筋工事および型枠工事を実施する。
    建築基準法に適合する構造計算を行い、確認申請を提出する。
    施工管理者は安全管理を徹底し、工程管理を適切に行う必要がある。
    """
    
    # 術語抽出
    extracted = extractor.extract_from_text(sample_text)
    
    print("抽出結果:")
    for category, terms in extracted.items():
        if terms:
            print(f"  {category}: {', '.join(terms)}")
    
    # 平坦なリストも生成
    flat_terms = extractor.get_all_terms_flat(extracted)
    print(f"\n全術語 ({len(flat_terms)}個):")
    print(f"  {', '.join(flat_terms)}")

def main():
    """メインテスト実行"""
    test_pdf_extractor()

if __name__ == "__main__":
    main()