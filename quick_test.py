"""
クイックテストスクリプト
基本機能の動作確認用
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.term_extractor import TermExtractor
from src.vector_db import VectorDB
from src.minutes_generator import MinutesGenerator
from src.tagger import SmartTagger

def test_term_extraction():
    """専門術語抽出のテスト"""
    print("=== 専門術語抽出テスト ===")
    
    extractor = TermExtractor()
    
    # サンプルテキスト
    sample_text = """
    鉄筋コンクリート構造の基礎工事において、RC材料の品質管理が重要である。
    施工図面に基づき、NET査定を実施する必要がある。
    PC構造とSRC構造の比較検討も行う。
    """
    
    terms = extractor._extract_terms_from_text(sample_text)
    print(f"抽出された術語: {terms}")
    print(f"術語数: {len(terms)}")
    print()

def test_vector_db():
    """ベクターデータベースのテスト"""
    print("=== ベクターデータベーステスト ===")
    
    # サンプル術語
    sample_terms = [
        "鉄筋コンクリート", "基礎工事", "施工管理", "品質管理",
        "安全管理", "RC構造", "PC構造", "SRC構造", "図面",
        "仕様書", "検査", "試験", "材料", "コンクリート"
    ]
    
    # ベクターDBを構築
    db = VectorDB()
    print("ベクターDBを構築中...")
    db.build_index(sample_terms)
    print("構築完了")
    
    # 検索テスト
    test_queries = ["コンクリート", "RC", "管理", "図面"]
    
    for query in test_queries:
        results = db.search(query, k=3)
        print(f"'{query}' の検索結果:")
        for term, score in results:
            print(f"  - {term}: {score:.3f}")
        print()

def test_minutes_generation():
    """議事録生成のテスト"""
    print("=== 議事録生成テスト ===")
    
    generator = MinutesGenerator()
    
    # サンプル転写テキスト
    sample_transcript = """
    本日の会議では、RC構造の基礎工事について検討しました。
    田中部長から品質管理の重要性について説明がありました。
    施工図面の修正が必要であることが決定されました。
    山田さんが来週までに図面を確認することになりました。
    安全管理についても課題があることが判明しました。
    緊急に対応が必要な項目があります。
    """
    
    # 議事録生成
    minutes = generator.generate_minutes(sample_transcript)
    
    print("生成された議事録:")
    print(f"要約: {minutes['summary']}")
    print(f"決定事項: {len(minutes['decisions'])}件")
    print(f"行動項目: {len(minutes['action_items'])}件") 
    print(f"課題: {len(minutes['issues'])}件")
    print()

def test_tagging():
    """タグ付けのテスト"""
    print("=== タグ付けテスト ===")
    
    tagger = SmartTagger()
    
    # サンプルコンテンツ
    sample_content = "RC構造の基礎工事について、田中部長が品質管理の重要性を説明した。緊急に図面の修正が必要。"
    
    # タグ付け
    tags = tagger.tag_content(sample_content)
    
    print("タグ付け結果:")
    for key, value in tags.items():
        print(f"  {key}: {value}")
    print()

def test_integration():
    """統合テスト"""
    print("=== 統合テスト ===")
    
    # 1. 術語抽出とベクターDB構築
    print("1. 術語データベース構築...")
    sample_terms = [
        "鉄筋コンクリート", "基礎工事", "施工管理", "品質管理",
        "RC構造", "PC構造", "図面", "仕様書"
    ]
    
    db = VectorDB()
    db.build_index(sample_terms)
    print("  ✓ 完了")
    
    # 2. 議事録生成
    print("2. 議事録生成...")
    generator = MinutesGenerator()
    sample_transcript = """
    RC構造の基礎工事について検討しました。
    品質管理の強化が決定されました。
    田中さんが図面を確認します。
    """
    
    minutes = generator.generate_minutes(sample_transcript)
    print("  ✓ 完了")
    
    # 3. タグ付け
    print("3. タグ付け...")
    tagger = SmartTagger()
    tagged_minutes = tagger.tag_minutes(minutes)
    print("  ✓ 完了")
    
    # 4. 結果表示
    print("\n最終結果:")
    print(f"  決定事項: {len(tagged_minutes['decisions'])}件")
    print(f"  行動項目: {len(tagged_minutes['action_items'])}件")
    print(f"  主要カテゴリ: {tagged_minutes['tag_summary']['main_categories']}")
    print()

def main():
    """メインテスト実行"""
    print("建築業務会議転写システム - クイックテスト")
    print("=" * 50)
    
    try:
        test_term_extraction()
        test_vector_db()
        test_minutes_generation()
        test_tagging()
        test_integration()
        
        print("✓ すべてのテストが正常に完了しました！")
        
    except Exception as e:
        print(f"✗ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()