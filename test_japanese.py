"""
日本語機能テスト
日本語の専門術語処理と議事録生成をテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.term_extractor import TermExtractor
from src.minutes_generator import MinutesGenerator
from src.tagger import SmartTagger

def test_japanese_term_extraction():
    """日本語専門術語抽出のテスト"""
    print("=== 日本語専門術語抽出テスト ===")
    
    extractor = TermExtractor()
    
    # 日本語建築専門用語のサンプルテキスト
    japanese_text = """
    鉄筋コンクリート造（RC造）の基礎工事において、コンクリートの品質管理が重要である。
    鉄筋の配筋検査、型枠工事、コンクリート打設工事の各工程で厳格な施工管理を行う。
    構造計算書に基づき、梁、柱、スラブの寸法を確認する。
    建築基準法第20条に適合する構造設計とする。
    PC工法、SRC構造との比較検討も実施する。
    """
    
    terms = extractor._extract_terms_from_text(japanese_text)
    print(f"抽出された日本語術語: {terms}")
    print(f"術語数: {len(terms)}")
    print()

def test_japanese_minutes():
    """日本語議事録生成のテスト"""
    print("=== 日本語議事録生成テスト ===")
    
    generator = MinutesGenerator()
    
    # 日本語会議の転写テキスト
    japanese_transcript = """
    本日は貴重なお時間をいただき、ありがとうございます。
    今回の会議では、RC構造の基礎工事について検討いたします。
    
    田中部長より、品質管理の重要性についてご説明いただきました。
    特に、コンクリートの強度試験については厳格に実施することが決定されました。
    
    次に、施工図面の修正についてですが、構造計算の見直しが必要との判断になりました。
    山田係長に来週までに修正案を作成していただくことをお願いいたします。
    
    また、安全管理についても課題が見つかりました。
    作業員の安全教育を強化する必要があります。
    これは緊急に対応すべき事項として認識しています。
    
    工程表の見直しも検討が必要です。
    佐藤さんにスケジュール調整をお願いします。
    
    以上で本日の議事を終了いたします。
    """
    
    # 議事録生成
    minutes = generator.generate_minutes(japanese_transcript)
    
    print("生成された日本語議事録:")
    print(f"要約: {minutes['summary']}")
    print(f"決定事項数: {len(minutes['decisions'])}")
    if minutes['decisions']:
        for i, decision in enumerate(minutes['decisions'], 1):
            print(f"  {i}. {decision['content']}")
    
    print(f"行動項目数: {len(minutes['action_items'])}")
    if minutes['action_items']:
        for i, action in enumerate(minutes['action_items'], 1):
            assignee = f" ({action.get('assignee', '未定')})" if action.get('assignee') else ""
            print(f"  {i}. {action['content']}{assignee}")
    
    print(f"課題数: {len(minutes['issues'])}")
    if minutes['issues']:
        for i, issue in enumerate(minutes['issues'], 1):
            priority = f" [{issue.get('priority', '中')}]"
            print(f"  {i}. {issue['content']}{priority}")
    print()

def test_japanese_tagging():
    """日本語タグ付けのテスト"""
    print("=== 日本語タグ付けテスト ===")
    
    tagger = SmartTagger()
    
    # 日本語建築コンテンツ
    japanese_contents = [
        "RC構造の基礎工事について、田中部長が品質管理の重要性を説明した",
        "緊急に図面の修正が必要である",
        "安全管理体制の見直しを検討する必要がある",
        "コンクリート強度試験の実施が決定された",
        "設計者との調整が必要な事項が発見された"
    ]
    
    for i, content in enumerate(japanese_contents, 1):
        print(f"コンテンツ {i}: {content}")
        tags = tagger.tag_content(content)
        
        print(f"  カテゴリ: {tags['categories']}")
        print(f"  コンテンツタイプ: {tags['content_types']}")
        print(f"  優先度: {tags['priority']}")
        print(f"  関係者: {tags['stakeholders']}")
        print()

def test_vector_db_japanese():
    """日本語ベクターDB（利用可能な場合）"""
    print("=== 日本語ベクターDBテスト ===")
    
    try:
        from src.vector_db import VectorDB
        
        # 日本語建築専門用語
        japanese_terms = [
            "鉄筋コンクリート", "RC構造", "PC構造", "SRC構造",
            "基礎工事", "杭工事", "型枠工事", "配筋工事",
            "施工管理", "品質管理", "安全管理", "工程管理",
            "構造計算", "意匠設計", "設備設計", "施工図面",
            "建築基準法", "確認申請", "検査済証", "完了検査"
        ]
        
        print("日本語対応ベクターDBを構築中...")
        db = VectorDB("auto")  # 自動選択で日本語対応モデルを試行
        db.build_index(japanese_terms)
        print("✓ 構築完了")
        
        # 日本語検索テスト
        test_queries = ["コンクリート", "RC", "管理", "設計", "工事"]
        
        for query in test_queries:
            results = db.search(query, k=3)
            print(f"'{query}' の検索結果:")
            for term, score in results:
                print(f"  - {term}: {score:.3f}")
            print()
            
    except Exception as e:
        print(f"ベクターDBテストでエラー: {e}")
        print("日本語モデルが利用できない可能性があります")
        print("install_japanese_support.py を実行してください")

def main():
    """メインテスト実行"""
    print("建築業務会議転写システム - 日本語機能テスト")
    print("=" * 60)
    
    try:
        # 基本的な日本語処理テスト
        test_japanese_term_extraction()
        test_japanese_minutes()
        test_japanese_tagging()
        
        # ベクターDB（オプション）
        test_vector_db_japanese()
        
        print("=" * 60)
        print("✓ 日本語機能テストが完了しました！")
        print()
        print("注意:")
        print("- ベクターDBで日本語モデルが利用できない場合は、")
        print("  install_japanese_support.py を実行してください")
        print("- 基本的な日本語処理は多言語モデルでも動作します")
        
    except Exception as e:
        print(f"✗ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()