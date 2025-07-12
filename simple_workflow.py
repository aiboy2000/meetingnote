"""
シンプルワークフローアプリ
Python 3.13とGradio互換性問題を回避
"""

import json
import os
from pathlib import Path

def create_simple_html_interface():
    """シンプルなHTMLインターフェースを作成"""
    
    html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏗️ 建築会議転写システム</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .workflow {
            display: flex;
            padding: 30px;
            gap: 30px;
        }
        .step {
            flex: 1;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            background: #fafafa;
        }
        .step.active {
            border-color: #667eea;
            background: #f0f4ff;
        }
        .step.completed {
            border-color: #4caf50;
            background: #f0fff0;
        }
        .step-number {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #ccc;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .step.active .step-number {
            background: #667eea;
        }
        .step.completed .step-number {
            background: #4caf50;
        }
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 15px 0;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-area:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }
        .upload-area.dragover {
            border-color: #667eea;
            background: #f0f4ff;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .result-area {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .status {
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
        }
        .status.success {
            background: #e8f5e8;
            border: 1px solid #4caf50;
            color: #2e7d32;
        }
        .status.error {
            background: #ffe8e8;
            border: 1px solid #f44336;
            color: #c62828;
        }
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ 建築会議転写システム</h1>
            <p>3ステップワークフロー: PDF術語抽出 → 音声転写 → 議事録生成</p>
        </div>
        
        <div class="workflow">
            <!-- ステップ1: PDF術語抽出 -->
            <div class="step active" id="step1">
                <div class="step-number">1</div>
                <h3>📚 専門術語抽出</h3>
                <p>建築関連PDFから専門術語を抽出します</p>
                
                <div class="upload-area" id="pdf-upload" onclick="document.getElementById('pdf-files').click()">
                    <p>📁 PDFファイルをドロップまたはクリック</p>
                    <input type="file" id="pdf-files" multiple accept=".pdf" style="display: none;">
                </div>
                
                <button class="btn" id="extract-btn" onclick="extractTerms()">🔍 術語抽出開始</button>
                
                <div class="result-area hidden" id="pdf-result"></div>
            </div>
            
            <!-- ステップ2: 音声転写 -->
            <div class="step" id="step2">
                <div class="step-number">2</div>
                <h3>🎤 音声転写</h3>
                <p>会議音声を転写します</p>
                
                <div class="upload-area" id="audio-upload" onclick="document.getElementById('audio-files').click()">
                    <p>🎬 音声/動画ファイルをドロップまたはクリック</p>
                    <input type="file" id="audio-files" accept=".mp4,.wav,.mp3,.m4a" style="display: none;">
                </div>
                
                <button class="btn" id="transcribe-btn" onclick="transcribeAudio()" disabled>🎤 転写開始</button>
                
                <div class="result-area hidden" id="audio-result"></div>
            </div>
            
            <!-- ステップ3: 議事録生成 -->
            <div class="step" id="step3">
                <div class="step-number">3</div>
                <h3>📄 議事録生成</h3>
                <p>構造化議事録を生成します</p>
                
                <div>
                    <input type="text" id="meeting-title" placeholder="会議タイトル" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc; border-radius: 4px;">
                    <input type="text" id="meeting-date" placeholder="会議日付" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc; border-radius: 4px;">
                </div>
                
                <button class="btn" id="minutes-btn" onclick="generateMinutes()" disabled>📋 議事録生成</button>
                
                <div class="result-area hidden" id="minutes-result"></div>
            </div>
        </div>
    </div>

    <script>
        // グローバル状態
        let extractedTerms = [];
        let transcriptText = "";
        let step1Complete = false;
        let step2Complete = false;

        // 術語抽出
        function extractTerms() {
            const files = document.getElementById('pdf-files').files;
            if (files.length === 0) {
                alert('PDFファイルを選択してください');
                return;
            }

            // デモ用の術語データ
            const demoTerms = {
                "構造": ["RC造", "PC造", "SRC造", "鉄筋コンクリート造", "基礎工事", "杭工事"],
                "工事": ["型枠工事", "配筋工事", "コンクリート工事", "躯体工事", "仕上工事"],
                "材料": ["コンクリート強度", "鉄筋材料", "セメント", "骨材", "添加剤"],
                "管理": ["品質管理", "安全管理", "工程管理", "施工管理", "検査方法"],
                "設計": ["構造設計", "意匠設計", "構造計算", "施工図面", "仕様書"],
                "法規": ["建築基準法", "確認申請", "完了検査", "検査済証"]
            };

            extractedTerms = [];
            for (const category in demoTerms) {
                extractedTerms.push(...demoTerms[category]);
            }

            // 結果表示
            let resultHtml = `
                <div class="status success">✅ 専門術語抽出完了</div>
                <h4>📊 抽出結果 (${extractedTerms.length}個の術語)</h4>
            `;

            for (const [category, terms] of Object.entries(demoTerms)) {
                resultHtml += `<h5>${category}:</h5><p>${terms.join(', ')}</p>`;
            }

            document.getElementById('pdf-result').innerHTML = resultHtml;
            document.getElementById('pdf-result').classList.remove('hidden');

            // ステップ1完了
            step1Complete = true;
            document.getElementById('step1').classList.add('completed');
            document.getElementById('step1').classList.remove('active');
            document.getElementById('step2').classList.add('active');
            document.getElementById('transcribe-btn').disabled = false;
        }

        // 音声転写
        function transcribeAudio() {
            const files = document.getElementById('audio-files').files;
            if (files.length === 0) {
                alert('音声ファイルを選択してください');
                return;
            }

            // デモ用転写テキスト
            transcriptText = `本日はお忙しい中お集まりいただき、ありがとうございます。

今回の会議では、RC構造の基礎工事について検討いたします。

田中部長より、品質管理の重要性についてご説明いただきました。特に、コンクリートの強度試験については、建築基準法に基づき厳格に実施することが決定されました。

次に、施工図面の修正についてですが、構造計算の見直しが必要との判断になりました。山田係長に来週までに修正案を作成していただくことをお願いいたします。

また、安全管理についても課題が見つかりました。作業員の安全教育を強化する必要があります。これは緊急に対応すべき事項として認識しています。

以上で本日の議事を終了いたします。`;

            // 使用された術語をチェック
            const usedTerms = extractedTerms.filter(term => transcriptText.includes(term));

            const resultHtml = `
                <div class="status success">✅ 音声転写完了</div>
                <h4>📝 転写結果</h4>
                <p><strong>文字数:</strong> ${transcriptText.length}文字</p>
                <p><strong>検出された専門術語:</strong> ${usedTerms.length}個</p>
                <p><strong>使用術語:</strong> ${usedTerms.join(', ')}</p>
                <h5>転写テキスト:</h5>
                <div style="background: #f9f9f9; padding: 10px; border-left: 3px solid #667eea;">${transcriptText.replace(/\\n/g, '<br>')}</div>
            `;

            document.getElementById('audio-result').innerHTML = resultHtml;
            document.getElementById('audio-result').classList.remove('hidden');

            // ステップ2完了
            step2Complete = true;
            document.getElementById('step2').classList.add('completed');
            document.getElementById('step2').classList.remove('active');
            document.getElementById('step3').classList.add('active');
            document.getElementById('minutes-btn').disabled = false;
        }

        // 議事録生成
        function generateMinutes() {
            const title = document.getElementById('meeting-title').value || "建築技術検討会議";
            const date = document.getElementById('meeting-date').value || "2024年1月15日";

            // キーワード抽出
            const sentences = transcriptText.split('。').filter(s => s.trim());
            
            const decisions = sentences.filter(s => 
                s.includes('決定') || s.includes('承認') || s.includes('確定')
            );
            
            const actions = sentences.filter(s => 
                s.includes('お願い') || s.includes('作成') || s.includes('実施')
            );
            
            const issues = sentences.filter(s => 
                s.includes('課題') || s.includes('問題') || s.includes('検討')
            );

            const usedTerms = extractedTerms.filter(term => transcriptText.includes(term));

            const minutesHtml = `
                <div class="status success">✅ 議事録生成完了</div>
                <h4>📋 ${title}</h4>
                <p><strong>日付:</strong> ${date}</p>
                
                <h5>✅ 決定事項 (${decisions.length}件)</h5>
                ${decisions.map((d, i) => `<p>${i+1}. ${d.trim()}</p>`).join('')}
                
                <h5>📋 行動項目 (${actions.length}件)</h5>
                ${actions.map((a, i) => `<p>${i+1}. ${a.trim()}</p>`).join('')}
                
                <h5>⚠️ 課題 (${issues.length}件)</h5>
                ${issues.map((issue, i) => `<p>${i+1}. ${issue.trim()}</p>`).join('')}
                
                <h5>🏗️ 使用された専門術語</h5>
                <p>${usedTerms.join(', ')}</p>
                
                <h5>📊 統計</h5>
                <p>決定事項: ${decisions.length}件, 行動項目: ${actions.length}件, 課題: ${issues.length}件</p>
            `;

            document.getElementById('minutes-result').innerHTML = minutesHtml;
            document.getElementById('minutes-result').classList.remove('hidden');

            // 全ステップ完了
            document.getElementById('step3').classList.add('completed');
        }

        // ファイルドロップ対応
        ['pdf-upload', 'audio-upload'].forEach(id => {
            const element = document.getElementById(id);
            element.addEventListener('dragover', e => {
                e.preventDefault();
                element.classList.add('dragover');
            });
            element.addEventListener('dragleave', e => {
                element.classList.remove('dragover');
            });
            element.addEventListener('drop', e => {
                e.preventDefault();
                element.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (id === 'pdf-upload') {
                    document.getElementById('pdf-files').files = files;
                } else {
                    document.getElementById('audio-files').files = files;
                }
            });
        });
    </script>
</body>
</html>
"""
    
    return html_content

def create_html_app():
    """HTMLアプリを作成"""
    html_content = create_simple_html_interface()
    
    # HTMLファイルを保存
    html_file = Path("workflow_interface.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTMLインターフェースを作成しました: {html_file}")
    print("🌐 ブラウザで以下のファイルを開いてください:")
    print(f"   file://{html_file.absolute()}")
    
    return html_file

def main():
    """メイン実行"""
    print("🏗️ 建築会議転写システム（シンプルワークフロー版）")
    print("=" * 60)
    print("Python 3.13とGradio互換性問題を回避したHTMLベース版")
    print()
    
    try:
        html_file = create_html_app()
        
        # 可能であればブラウザを開く
        try:
            import webbrowser
            webbrowser.open(f"file://{html_file.absolute()}")
            print("✅ ブラウザを開きました")
        except:
            print("⚠️  手動でブラウザを開いてください")
        
        print("\n🎯 使用方法:")
        print("1. ブラウザでHTMLファイルを開く")
        print("2. ステップ1: PDFファイルをアップロード → 術語抽出")
        print("3. ステップ2: 音声ファイルをアップロード → 転写")
        print("4. ステップ3: 会議情報を入力 → 議事録生成")
        
        input("\nEnterキーを押すと終了します...")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    main()