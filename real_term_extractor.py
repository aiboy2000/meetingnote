"""
实际运行版 - 建筑专门术语抽出系统
No Demo Data - Real PDF Processing Only
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
import PyPDF2
import pickle

class RealTermExtractor:
    def __init__(self):
        """实际数据专门术语抽出器初始化"""
        self.extracted_terms = {}
        self.term_db_path = "extracted_terms_database.json"
        self.search_index_path = "term_search_index.json"
        
        # 建築専門用語パターン（正規表現）
        self.term_patterns = {
            "構造関連": [
                r'RC[造構法工事施工]*', r'PC[造構法工事施工]*', r'SRC[造構法工事施工]*',
                r'鉄筋[コンクリート造構法工事]*', r'基礎[工事構造設計施工]*', 
                r'杭[工事基礎施工打設]*', r'直接基礎', r'布基礎', r'独立基礎', r'べた基礎',
                r'躯体[工事構造施工]*', r'柱[構造部材設計]*', r'梁[構造部材設計]*', 
                r'スラブ[構造床版]*', r'壁[構造耐力壁]*', r'階段[構造設計]*',
                r'耐震[構造設計診断]*', r'制震[構造設計装置]*', r'免震[構造設計装置]*',
                r'構造[設計計算解析]*', r'荷重[設計計算]*', r'応力[計算解析]*'
            ],
            "工事関連": [
                r'型枠[工事作業施工設置]*', r'配筋[工事作業施工]*', 
                r'コンクリート[工事打設養生]*', r'仕上[工事作業施工]*',
                r'防水[工事作業施工材料]*', r'左官[工事作業施工]*',
                r'塗装[工事作業施工]*', r'内装[工事作業施工]*', r'外装[工事作業施工]*',
                r'設備[工事配管施工]*', r'電気[工事配線施工]*', r'給排水[工事配管施工]*',
                r'空調[工事設備施工]*', r'衛生[設備工事]*', r'昇降機[設備工事]*',
                r'足場[工事安全施工]*', r'養生[作業安全]*', r'解体[工事作業]*'
            ],
            "材料関連": [
                r'コンクリート[強度品質調合Fc\d+]*', r'鉄筋[材料規格D\d+SD\d+]*',
                r'セメント[種類普通高炉早強]*', r'骨材[粗細川砂利砕石]*',
                r'添加剤[AE減水高性能]*', r'防水[材料シートアスファルト]*',
                r'断熱[材料保温グラスウール]*', r'仕上[材料塗装クロス]*',
                r'建具[材料アルミ木製樹脂]*', r'ガラス[材料複層強化]*',
                r'タイル[材料仕上]*', r'石材[材料仕上]*', r'金属[材料建材]*'
            ],
            "管理関連": [
                r'品質[管理検査試験]*', r'安全[管理対策教育]*', 
                r'工程[管理スケジュール計画]*', r'施工[管理監理]*',
                r'検査[方法試験中間完了]*', r'試験[方法強度品質]*',
                r'測定[方法計測]*', r'記録[管理保管写真]*', r'報告[書類提出]*',
                r'監理[業務確認]*', r'監督[業務指導]*', r'検収[業務確認]*'
            ],
            "設計関連": [
                r'構造[設計計算]*', r'意匠[設計デザイン]*', r'設備[設計機械電気]*',
                r'施工[図面詳細]*', r'仕様[書規定基準]*', r'詳細[図面設計]*',
                r'断面[図詳細構造]*', r'平面[図設計配置]*', r'立面[図設計外観]*',
                r'配置[図敷地計画]*', r'矩計[図詳細]*', r'展開[図内装]*'
            ],
            "法規関連": [
                r'建築基準法[第\d+条項款]*', r'確認[申請済証]*', r'完了[検査済証]*',
                r'検査[済証中間完了]*', r'建築[確認許可]*', r'消防[法令規定]*',
                r'都市計画[法令規定]*', r'条例[地方自治体]*', r'建設業法',
                r'労働安全衛生法', r'廃棄物処理法', r'環境[基準法令]*'
            ],
            "測定・試験": [
                r'強度[試験測定N/mm²MPa]*', r'スランプ[試験測定cm]*',
                r'空気量[測定試験%]*', r'温度[測定管理℃]*', r'湿度[測定管理%]*',
                r'騒音[測定dB]*', r'振動[測定計測]*', r'厚さ[測定mm]*',
                r'寸法[測定精度公差]*', r'レベル[測定標高]*', r'通り[測定芯]*'
            ],
            "機械・設備": [
                r'クレーン[重機建設機械]*', r'ポンプ[車コンクリート]*',
                r'ミキサー[車コンクリート]*', r'バックホウ[重機掘削]*',
                r'ブルドーザー[重機整地]*', r'ローラー[重機締固]*',
                r'発電機[設備電源]*', r'コンプレッサー[設備空気]*'
            ]
        }
        
        # 専門用語の最小・最大長制限
        self.min_term_length = 2
        self.max_term_length = 15
        
    def extract_from_pdf(self, pdf_path):
        """PDFファイルから実際に専門術語を抽出"""
        print(f"📖 PDFファイル解析開始: {os.path.basename(pdf_path)}")
        
        try:
            # PDFテキスト抽出
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                print(f"📄 総ページ数: {len(pdf_reader.pages)}")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        full_text += page_text + "\n"
                        print(f"   ページ {page_num}: {len(page_text)}文字抽出")
                    except Exception as e:
                        print(f"   ⚠️ ページ {page_num} 読み込みエラー: {e}")
                        continue
            
            if not full_text.strip():
                print("❌ PDFからテキストを抽出できませんでした")
                return None
            
            print(f"📝 総抽出文字数: {len(full_text)}文字")
            
            # 専門術語抽出実行
            extracted_terms = self._extract_terms_by_patterns(full_text)
            
            # 追加の術語抽出（文脈ベース）
            context_terms = self._extract_context_terms(full_text)
            if context_terms:
                extracted_terms["文脈抽出"] = context_terms
            
            # 結果統計
            total_count = sum(len(terms) for terms in extracted_terms.values())
            print(f"✅ 専門術語抽出完了: {total_count}個")
            
            return extracted_terms, full_text
            
        except FileNotFoundError:
            print(f"❌ ファイルが見つかりません: {pdf_path}")
            return None
        except Exception as e:
            print(f"❌ PDF読み込みエラー: {e}")
            return None
    
    def _extract_terms_by_patterns(self, text):
        """パターンマッチングによる専門術語抽出"""
        extracted = {}
        
        for category, patterns in self.term_patterns.items():
            found_terms = set()
            
            for pattern in patterns:
                # 正規表現マッチング
                matches = re.findall(pattern, text, re.IGNORECASE)
                
                # 長さフィルタリング
                valid_matches = [
                    match for match in matches 
                    if self.min_term_length <= len(match) <= self.max_term_length
                ]
                
                found_terms.update(valid_matches)
            
            if found_terms:
                extracted[category] = sorted(list(found_terms))
                print(f"   🔹 {category}: {len(found_terms)}個")
        
        return extracted
    
    def _extract_context_terms(self, text):
        """文脈ベースの追加術語抽出"""
        # 建築関連キーワード
        building_keywords = [
            '工法', '構法', '設計', '施工', '監理', '管理', '検査', '試験',
            '材料', '部材', '構造', '基礎', '躯体', '仕上', '設備', '機械',
            '品質', '安全', '工程', '図面', '仕様', '規格', '基準'
        ]
        
        context_terms = set()
        
        # 文を分割して処理
        sentences = re.split(r'[。\n]', text)
        
        for sentence in sentences:
            # 建築キーワードを含む文から術語を抽出
            for keyword in building_keywords:
                if keyword in sentence:
                    # 単語抽出（ひらがな・カタカナ・漢字・英数字）
                    words = re.findall(r'[一-龯ァ-ヶー\w]+', sentence)
                    
                    for word in words:
                        # 長さとキーワード条件チェック
                        if (self.min_term_length <= len(word) <= self.max_term_length and
                            any(kw in word for kw in building_keywords) and
                            not word.isdigit()):
                            context_terms.add(word)
        
        return sorted(list(context_terms))[:30]  # 上位30個まで
    
    def save_to_database(self, terms_dict, pdf_path, full_text):
        """抽出結果をデータベースに保存"""
        # メインデータベース
        db_data = {
            "extraction_info": {
                "source_file": str(pdf_path),
                "file_size": os.path.getsize(pdf_path),
                "extracted_at": datetime.now().isoformat(),
                "text_length": len(full_text)
            },
            "terms_by_category": terms_dict,
            "statistics": {
                "total_terms": sum(len(terms) for terms in terms_dict.values()),
                "categories_count": len(terms_dict),
                "terms_per_category": {
                    category: len(terms) 
                    for category, terms in terms_dict.items()
                }
            }
        }
        
        # JSON保存
        with open(self.term_db_path, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)
        print(f"💾 メインデータベース保存: {self.term_db_path}")
        
        # 検索用インデックス作成
        search_index = []
        for category, terms in terms_dict.items():
            for term in terms:
                search_index.append({
                    "term": term,
                    "category": category,
                    "length": len(term),
                    "readings": self._generate_readings(term)
                })
        
        with open(self.search_index_path, 'w', encoding='utf-8') as f:
            json.dump(search_index, f, ensure_ascii=False, indent=2)
        print(f"🔍 検索インデックス保存: {self.search_index_path}")
        
        return db_data
    
    def _generate_readings(self, term):
        """術語の読み方候補を生成（簡易版）"""
        # 基本的な読み方パターン
        readings = [term]
        
        # カタカナ変換候補
        katakana_map = {
            'コンクリート': ['concrete', 'ｺﾝｸﾘｰﾄ'],
            'アスファルト': ['asphalt', 'ｱｽﾌｧﾙﾄ'],
            'セメント': ['cement', 'ｾﾒﾝﾄ']
        }
        
        for key, variants in katakana_map.items():
            if key in term:
                readings.extend(variants)
        
        return list(set(readings))
    
    def create_search_interface(self, db_data):
        """検索インターフェース生成"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏗️ 建築専門術語検索システム</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 1.1em; }}
        .search-section {{
            padding: 40px;
        }}
        .search-container {{
            position: relative;
            margin-bottom: 30px;
        }}
        .search-box {{
            width: 100%;
            padding: 20px 60px 20px 20px;
            font-size: 18px;
            border: 3px solid #e0e0e0;
            border-radius: 15px;
            outline: none;
            transition: all 0.3s ease;
        }}
        .search-box:focus {{
            border-color: #667eea;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        }}
        .search-icon {{
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 24px;
            color: #667eea;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 14px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .categories {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 30px;
        }}
        .category-btn {{
            padding: 12px 20px;
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        .category-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .category-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        .results-container {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            min-height: 400px;
        }}
        .results-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e9ecef;
        }}
        .results-count {{
            font-size: 18px;
            font-weight: bold;
            color: #495057;
        }}
        .sort-select {{
            padding: 8px 15px;
            border: 1px solid #ced4da;
            border-radius: 8px;
            background: white;
        }}
        .terms-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }}
        .term-card {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
        }}
        .term-card:hover {{
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .term-name {{
            font-size: 18px;
            font-weight: bold;
            color: #212529;
            margin-bottom: 8px;
        }}
        .term-category {{
            display: inline-block;
            padding: 4px 12px;
            background: #667eea;
            color: white;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 500;
        }}
        .term-length {{
            float: right;
            color: #6c757d;
            font-size: 12px;
        }}
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }}
        .no-results-icon {{
            font-size: 4em;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ 建築専門術語検索システム</h1>
            <p>ファイル: {os.path.basename(db_data['extraction_info']['source_file'])}</p>
            <p>抽出日時: {db_data['extraction_info']['extracted_at'][:19]}</p>
        </div>
        
        <div class="search-section">
            <div class="search-container">
                <input type="text" id="search-input" class="search-box" 
                       placeholder="🔍 検索したい術語を入力してください...">
                <div class="search-icon">🔍</div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{db_data['statistics']['total_terms']}</div>
                    <div class="stat-label">総術語数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{db_data['statistics']['categories_count']}</div>
                    <div class="stat-label">カテゴリ数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="filtered-count">-</div>
                    <div class="stat-label">検索結果</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(db_data['extraction_info']['text_length'])}</div>
                    <div class="stat-label">文字数</div>
                </div>
            </div>
            
            <div class="categories">
                <div class="category-btn active" data-category="all">すべて</div>
"""
        
        # カテゴリボタン追加
        for category in db_data['terms_by_category'].keys():
            count = len(db_data['terms_by_category'][category])
            html_content += f'<div class="category-btn" data-category="{category}">{category} ({count})</div>\n'
        
        html_content += f"""
            </div>
            
            <div class="results-container">
                <div class="results-header">
                    <div class="results-count" id="results-count">すべての術語を表示</div>
                    <select class="sort-select" id="sort-select">
                        <option value="name">名前順</option>
                        <option value="category">カテゴリ順</option>
                        <option value="length">文字数順</option>
                    </select>
                </div>
                <div class="terms-grid" id="results-grid"></div>
            </div>
        </div>
    </div>

    <script>
        // データ
        const termsData = {json.dumps(db_data, ensure_ascii=False)};
        
        let currentCategory = 'all';
        let currentSort = 'name';
        let allTerms = [];
        
        // 術語データ平坦化
        for (const [category, terms] of Object.entries(termsData.terms_by_category)) {{
            for (const term of terms) {{
                allTerms.push({{
                    term: term,
                    category: category,
                    length: term.length
                }});
            }}
        }}
        
        // 検索とフィルタリング
        function updateResults() {{
            const query = document.getElementById('search-input').value.toLowerCase();
            
            let filtered = allTerms.filter(item => {{
                const matchesQuery = query === '' || item.term.toLowerCase().includes(query);
                const matchesCategory = currentCategory === 'all' || item.category === currentCategory;
                return matchesQuery && matchesCategory;
            }});
            
            // ソート
            filtered.sort((a, b) => {{
                switch(currentSort) {{
                    case 'name': return a.term.localeCompare(b.term);
                    case 'category': return a.category.localeCompare(b.category);
                    case 'length': return b.length - a.length;
                    default: return 0;
                }}
            }});
            
            displayResults(filtered);
            updateCounts(filtered.length);
        }}
        
        // 結果表示
        function displayResults(results) {{
            const grid = document.getElementById('results-grid');
            
            if (results.length === 0) {{
                grid.innerHTML = `
                    <div class="no-results">
                        <div class="no-results-icon">🔍</div>
                        <h3>検索結果がありません</h3>
                        <p>検索条件を変更してお試しください</p>
                    </div>
                `;
                return;
            }}
            
            grid.innerHTML = results.map(item => `
                <div class="term-card">
                    <div class="term-name">
                        ${{item.term}}
                        <span class="term-length">${{item.length}}文字</span>
                    </div>
                    <span class="term-category">${{item.category}}</span>
                </div>
            `).join('');
        }}
        
        // カウント更新
        function updateCounts(filteredCount) {{
            document.getElementById('filtered-count').textContent = filteredCount;
            document.getElementById('results-count').textContent = `${{filteredCount}}件の術語`;
        }}
        
        // イベントリスナー
        document.getElementById('search-input').addEventListener('input', updateResults);
        
        document.getElementById('sort-select').addEventListener('change', (e) => {{
            currentSort = e.target.value;
            updateResults();
        }});
        
        document.querySelector('.categories').addEventListener('click', (e) => {{
            if (e.target.classList.contains('category-btn')) {{
                document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
                currentCategory = e.target.dataset.category;
                updateResults();
            }}
        }});
        
        // 初期化
        updateResults();
    </script>
</body>
</html>
"""
        
        return html_content

def main():
    """メイン実行関数"""
    print("🏗️ 実際運行版 - 建築専門術語抽出システム")
    print("=" * 60)
    print("⚠️  注意: デモデータは使用しません。実際のPDFファイルが必要です。")
    print()
    
    extractor = RealTermExtractor()
    
    # PDFファイルパス入力
    while True:
        print("📁 PDFファイルのパスを入力してください:")
        print("   (例: C:\\Documents\\建築仕様書.pdf)")
        pdf_path = input("PDFファイルパス: ").strip().strip('"')
        
        if not pdf_path:
            print("❌ パスが入力されていません")
            continue
            
        if not os.path.exists(pdf_path):
            print(f"❌ ファイルが見つかりません: {pdf_path}")
            continue
            
        if not pdf_path.lower().endswith('.pdf'):
            print("❌ PDFファイルを指定してください")
            continue
            
        break
    
    # 術語抽出実行
    print(f"\n🚀 術語抽出開始...")
    result = extractor.extract_from_pdf(pdf_path)
    
    if not result:
        print("❌ 術語抽出に失敗しました")
        return
    
    terms_dict, full_text = result
    
    if not terms_dict:
        print("❌ 専門術語が見つかりませんでした")
        print("   PDFの内容が建築関連でない可能性があります")
        return
    
    # 結果表示
    print(f"\n✅ 術語抽出完了!")
    total_terms = sum(len(terms) for terms in terms_dict.values())
    print(f"📊 総抽出術語数: {total_terms}個")
    print(f"📋 カテゴリ数: {len(terms_dict)}個")
    
    for category, terms in terms_dict.items():
        print(f"\n🔹 {category} ({len(terms)}個):")
        # 各カテゴリから最大10個表示
        display_terms = terms[:10]
        for term in display_terms:
            print(f"   • {term}")
        if len(terms) > 10:
            print(f"   ... 他{len(terms) - 10}個")
    
    # データベース保存
    print(f"\n💾 データベース保存中...")
    db_data = extractor.save_to_database(terms_dict, pdf_path, full_text)
    
    # 検索インターフェース作成
    print(f"\n🌐 検索インターフェース作成中...")
    html_content = extractor.create_search_interface(db_data)
    
    interface_file = Path("building_terms_search.html")
    with open(interface_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 検索インターフェース作成完了: {interface_file}")
    
    # ブラウザで開く
    try:
        import webbrowser
        webbrowser.open(f"file://{interface_file.absolute()}")
        print("✅ ブラウザで検索画面を開きました")
    except:
        print("⚠️ 手動でブラウザを開いてください")
        print(f"   ファイル: {interface_file.absolute()}")
    
    print(f"\n📁 保存されたファイル:")
    print(f"   • 術語データベース: {extractor.term_db_path}")
    print(f"   • 検索インデックス: {extractor.search_index_path}")
    print(f"   • 検索インターフェース: {interface_file}")
    
    print(f"\n🎯 次のステップ:")
    print(f"   1. 検索インターフェースで術語を確認")
    print(f"   2. 音声転写システムで術語データベースを活用")
    print(f"   3. 議事録生成で専門術語を自動補正")

if __name__ == "__main__":
    main()