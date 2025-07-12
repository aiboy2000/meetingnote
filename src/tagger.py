"""
タグ付けシステム
議事録内容に対する自動タグ付け
"""

import re
from typing import List, Dict, Set, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class SmartTagger:
    def __init__(self):
        """スマートタガーを初期化"""
        
        # 建築分野のカテゴリ別キーワード
        self.category_keywords = {
            "構造": [
                "RC", "SRC", "PC", "鉄筋", "コンクリート", "構造", "基礎", 
                "杭", "梁", "柱", "スラブ", "壁", "フレーム"
            ],
            "設備": [
                "電気", "機械", "空調", "給排水", "ガス", "消防", "エレベーター",
                "配管", "配線", "ダクト", "設備"
            ],
            "施工管理": [
                "工程", "品質", "安全", "原価", "施工", "管理", "検査", 
                "試験", "測定", "監理"
            ],
            "設計": [
                "図面", "仕様", "設計", "計画", "レイアウト", "詳細",
                "構造計算", "意匠", "構造図"
            ],
            "法規": [
                "建築基準法", "消防法", "条例", "申請", "許可", "認定",
                "検査済証", "確認申請"
            ],
            "材料": [
                "材料", "資材", "鋼材", "木材", "仕上げ", "防水",
                "断熱", "塗装", "タイル"
            ]
        }
        
        # 内容タイプ別キーワード
        self.content_type_keywords = {
            "決定事項": [
                "決定", "確定", "承認", "採用", "選定", "合意", "了承",
                "決める", "決まる"
            ],
            "行動項目": [
                "検討", "確認", "調整", "実施", "対応", "準備", "作成",
                "提出", "報告", "連絡", "相談", "修正", "変更"
            ],
            "課題": [
                "課題", "問題", "懸念", "検討事項", "要確認", "要検討",
                "要調整", "困った", "難しい"
            ],
            "情報共有": [
                "報告", "連絡", "情報", "状況", "進捗", "現状",
                "説明", "共有"
            ]
        }
        
        # 優先度キーワード
        self.priority_keywords = {
            "高": [
                "緊急", "至急", "重要", "必須", "急ぎ", "すぐに",
                "即座に", "早急", "優先"
            ],
            "中": [
                "要確認", "要検討", "なるべく", "できれば", "推奨"
            ],
            "低": [
                "参考", "情報", "念のため", "余裕があれば"
            ]
        }
        
        # 関係者キーワード
        self.stakeholder_keywords = {
            "発注者": [
                "発注者", "クライアント", "お客様", "施主", "建主"
            ],
            "設計者": [
                "設計者", "設計事務所", "アーキテクト", "構造設計",
                "設備設計", "意匠設計"
            ],
            "施工者": [
                "施工者", "ゼネコン", "建設会社", "工事会社", "請負"
            ],
            "監理者": [
                "監理者", "工事監理", "現場監督", "監督"
            ],
            "行政": [
                "行政", "役所", "建築主事", "確認検査機関", "消防署"
            ]
        }
    
    def tag_content(self, content: str, content_type: str = None) -> Dict:
        """
        コンテンツにタグを付与
        
        Args:
            content: タグ付け対象のテキスト
            content_type: コンテンツタイプ（決定事項、行動項目など）
            
        Returns:
            タグ情報辞書
        """
        tags = {
            "categories": self._extract_category_tags(content),
            "content_types": self._extract_content_type_tags(content, content_type),
            "priority": self._extract_priority_tag(content),
            "stakeholders": self._extract_stakeholder_tags(content),
            "keywords": self._extract_keywords(content),
            "technical_terms": self._extract_technical_terms(content)
        }
        
        return tags
    
    def _extract_category_tags(self, content: str) -> List[str]:
        """専門分野カテゴリタグを抽出"""
        tags = []
        content_lower = content.lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    tags.append(category)
                    break
        
        return list(set(tags))  # 重複を除去
    
    def _extract_content_type_tags(self, content: str, provided_type: str = None) -> List[str]:
        """内容タイプタグを抽出"""
        if provided_type:
            return [provided_type]
        
        tags = []
        content_lower = content.lower()
        
        for content_type, keywords in self.content_type_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    tags.append(content_type)
                    break
        
        return tags
    
    def _extract_priority_tag(self, content: str) -> str:
        """優先度タグを抽出"""
        content_lower = content.lower()
        
        # 高優先度から順にチェック
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    return priority
        
        return "中"  # デフォルト
    
    def _extract_stakeholder_tags(self, content: str) -> List[str]:
        """関係者タグを抽出"""
        tags = []
        content_lower = content.lower()
        
        for stakeholder, keywords in self.stakeholder_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    tags.append(stakeholder)
                    break
        
        return tags
    
    def _extract_keywords(self, content: str) -> List[str]:
        """重要キーワードを抽出"""
        # 名詞っぽい単語を抽出（簡易版）
        words = re.findall(r'[\u4e00-\u9faf\w]{2,}', content)
        
        # 出現頻度でフィルタリング
        word_counts = Counter(words)
        
        # 一般的すぎる単語を除外
        exclude_words = {
            'こと', 'もの', 'ため', 'よう', 'など', 'について',
            'による', 'により', 'として', 'から', 'まで'
        }
        
        keywords = []
        for word, count in word_counts.most_common(10):
            if word not in exclude_words and len(word) >= 2:
                keywords.append(word)
        
        return keywords
    
    def _extract_technical_terms(self, content: str) -> List[str]:
        """専門術語を抽出"""
        technical_terms = []
        
        # すべてのカテゴリキーワードをチェック
        all_keywords = []
        for keywords in self.category_keywords.values():
            all_keywords.extend(keywords)
        
        content_lower = content.lower()
        for keyword in all_keywords:
            if keyword.lower() in content_lower:
                technical_terms.append(keyword)
        
        return list(set(technical_terms))
    
    def tag_minutes(self, minutes: Dict) -> Dict:
        """
        議事録全体にタグを付与
        
        Args:
            minutes: 議事録データ
            
        Returns:
            タグ付きの議事録データ
        """
        tagged_minutes = minutes.copy()
        
        # 各セクションにタグを追加
        for section in ["decisions", "action_items", "issues"]:
            if section in tagged_minutes:
                for item in tagged_minutes[section]:
                    content = item.get("content", "")
                    content_type = item.get("type", section[:-1])  # 's'を除去
                    
                    # タグを生成
                    tags = self.tag_content(content, content_type)
                    item["tags"] = tags
        
        # 全体のタグサマリーを生成
        tagged_minutes["tag_summary"] = self._generate_tag_summary(tagged_minutes)
        
        return tagged_minutes
    
    def _generate_tag_summary(self, minutes: Dict) -> Dict:
        """議事録全体のタグサマリーを生成"""
        all_categories = []
        all_stakeholders = []
        all_priorities = []
        
        # 各項目からタグを集計
        for section in ["decisions", "action_items", "issues"]:
            items = minutes.get(section, [])
            for item in items:
                tags = item.get("tags", {})
                all_categories.extend(tags.get("categories", []))
                all_stakeholders.extend(tags.get("stakeholders", []))
                priority = tags.get("priority")
                if priority:
                    all_priorities.append(priority)
        
        # 出現頻度を集計
        category_counts = Counter(all_categories)
        stakeholder_counts = Counter(all_stakeholders)
        priority_counts = Counter(all_priorities)
        
        return {
            "main_categories": [cat for cat, count in category_counts.most_common(3)],
            "involved_stakeholders": list(stakeholder_counts.keys()),
            "priority_distribution": dict(priority_counts),
            "total_items": len(minutes.get("decisions", [])) + 
                          len(minutes.get("action_items", [])) + 
                          len(minutes.get("issues", []))
        }
    
    def search_by_tags(self, minutes_list: List[Dict], search_criteria: Dict) -> List[Dict]:
        """
        タグに基づいて議事録を検索
        
        Args:
            minutes_list: 議事録のリスト
            search_criteria: 検索条件
            
        Returns:
            マッチした議事録のリスト
        """
        results = []
        
        for minutes in minutes_list:
            if self._matches_criteria(minutes, search_criteria):
                results.append(minutes)
        
        return results
    
    def _matches_criteria(self, minutes: Dict, criteria: Dict) -> bool:
        """議事録が検索条件にマッチするかチェック"""
        tag_summary = minutes.get("tag_summary", {})
        
        # カテゴリ条件
        required_categories = criteria.get("categories", [])
        if required_categories:
            main_categories = tag_summary.get("main_categories", [])
            if not any(cat in main_categories for cat in required_categories):
                return False
        
        # 関係者条件
        required_stakeholders = criteria.get("stakeholders", [])
        if required_stakeholders:
            involved_stakeholders = tag_summary.get("involved_stakeholders", [])
            if not any(stakeholder in involved_stakeholders for stakeholder in required_stakeholders):
                return False
        
        # 優先度条件
        required_priority = criteria.get("priority")
        if required_priority:
            priority_dist = tag_summary.get("priority_distribution", {})
            if required_priority not in priority_dist:
                return False
        
        return True

def main():
    """テスト実行"""
    tagger = SmartTagger()
    
    # サンプルコンテンツ
    sample_content = "RC構造の基礎工事について、田中部長が品質管理の重要性を説明した。緊急に図面の修正が必要。"
    
    # タグ付けテスト
    tags = tagger.tag_content(sample_content)
    print("タグ付け結果:")
    for key, value in tags.items():
        print(f"  {key}: {value}")
    
    # 議事録タグ付けテスト
    sample_minutes = {
        "decisions": [
            {"content": "RC構造を採用することが決定された", "type": "decision"}
        ],
        "action_items": [
            {"content": "山田さんが図面を確認する", "type": "action_item"}
        ]
    }
    
    tagged_minutes = tagger.tag_minutes(sample_minutes)
    print("\n議事録タグ付け結果:")
    print(f"タグサマリー: {tagged_minutes['tag_summary']}")

if __name__ == "__main__":
    main()