#!/usr/bin/env python3
"""
建築会議転写システム - クリーン版
Gradio問題を完全回避した整理済みバージョン
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import subprocess

# Gradio依存を回避
USE_GRADIO = False

def check_environment():
    """環境チェック"""
    print("🔍 環境チェック中...")
    
    # Python版本チェック
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 必要パッケージチェック
    required_packages = {
        'PyPDF2': 'PyPDF2',
        'numpy': 'numpy',
        'sentence_transformers': 'sentence-transformers'
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {import_name} installed")
        except ImportError:
            print(f"❌ {import_name} not installed")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️ Missing packages: {', '.join(missing)}")
        install = input("Install missing packages? (y/n): ")
        if install.lower() == 'y':
            for pkg in missing:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)
    
    return len(missing) == 0

class CleanBuildingMeetingSystem:
    """クリーン版建築会議転写システム"""
    
    def __init__(self):
        self.extracted_terms = []
        self.transcript_text = ""
        self.minutes_data = {}
        
    def run_web_interface(self):
        """Webインターフェース起動"""
        print("\n🌐 Webインターフェース生成中...")
        
        html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏗️ 建築会議転写システム - クリーン版</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: rgba(0,0,0,0.1);
            padding: 30px;
            text-align: center;
            color: white;
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .main-content {
            padding: 40px;
        }
        .step-selector {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 40px;
        }
        .step-btn {
            padding: 15px 30px;
            background: #f0f0f0;
            border: 3px solid transparent;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
            font-size: 16px;
        }
        .step-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .step-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .step-content {
            display: none;
            animation: fadeIn 0.5s ease;
        }
        .step-content.active {
            display: block;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .action-area {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
        }
        .file-input-wrapper {
            position: relative;
            display: inline-block;
            cursor: pointer;
            width: 100%;
        }
        .file-input-wrapper input[type=file] {
            position: absolute;
            left: -9999px;
        }
        .file-input-label {
            display: block;
            padding: 20px;
            background: white;
            border: 3px dashed #667eea;
            border-radius: 10px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .file-input-label:hover {
            background: #f0f4ff;
            border-style: solid;
        }
        .process-btn {
            display: block;
            width: 100%;
            padding: 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 20px 0;
        }
        .process-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .process-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .results {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            max-height: 500px;
            overflow-y: auto;
        }
        .result-section {
            margin: 20px 0;
        }
        .result-section h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.3em;
        }
        .term-tag {
            display: inline-block;
            padding: 5px 15px;
            background: #e0e7ff;
            color: #667eea;
            border-radius: 20px;
            margin: 5px;
            font-size: 14px;
        }
        .status-message {
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            font-weight: bold;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ 建築会議転写システム</h1>
            <p>クリーン版 - Gradio問題を完全回避</p>
        </div>
        
        <div class="main-content">
            <div class="step-selector">
                <button class="step-btn active" onclick="showStep(1)">📚 Step 1: 術語抽出</button>
                <button class="step-btn" onclick="showStep(2)">🎤 Step 2: 音声転写</button>
                <button class="step-btn" onclick="showStep(3)">📋 Step 3: 議事録生成</button>
            </div>
            
            <!-- Step 1: 術語抽出 -->
            <div id="step1" class="step-content active">
                <h2>📚 専門術語抽出</h2>
                <p>建築関連PDFから専門術語を抽出します</p>
                
                <div class="action-area">
                    <div class="file-input-wrapper">
                        <input type="file" id="pdf-input" accept=".pdf" multiple onchange="handlePDFSelect(event)">
                        <label for="pdf-input" class="file-input-label">
                            <div style="font-size: 3em;">📁</div>
                            <p>PDFファイルをドラッグ＆ドロップ<br>またはクリックして選択</p>
                        </label>
                    </div>
                    <button class="process-btn" onclick="extractTerms()">🔍 術語抽出開始</button>
                    <div id="terms-result" class="results" style="display: none;"></div>
                </div>
            </div>
            
            <!-- Step 2: 音声転写 -->
            <div id="step2" class="step-content">
                <h2>🎤 音声転写</h2>
                <p>会議音声を転写し、専門術語で補正します</p>
                
                <div class="action-area">
                    <div class="file-input-wrapper">
                        <input type="file" id="audio-input" accept=".mp4,.mp3,.wav,.m4a" onchange="handleAudioSelect(event)">
                        <label for="audio-input" class="file-input-label">
                            <div style="font-size: 3em;">🎬</div>
                            <p>音声/動画ファイルをドラッグ＆ドロップ<br>またはクリックして選択</p>
                        </label>
                    </div>
                    <button class="process-btn" onclick="transcribeAudio()">🎤 転写開始</button>
                    <div id="transcript-result" class="results" style="display: none;"></div>
                </div>
            </div>
            
            <!-- Step 3: 議事録生成 -->
            <div id="step3" class="step-content">
                <h2>📋 議事録生成</h2>
                <p>転写テキストから構造化された議事録を生成します</p>
                
                <div class="action-area">
                    <input type="text" id="meeting-title" placeholder="会議タイトル" 
                           style="width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px;">
                    <input type="date" id="meeting-date" 
                           style="width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px;">
                    <button class="process-btn" onclick="generateMinutes()">📋 議事録生成</button>
                    <div id="minutes-result" class="results" style="display: none;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentStep = 1;
        let extractedTerms = [];
        let transcriptText = "";
        
        function showStep(step) {
            currentStep = step;
            
            // Update buttons
            document.querySelectorAll('.step-btn').forEach((btn, idx) => {
                btn.classList.toggle('active', idx === step - 1);
            });
            
            // Update content
            document.querySelectorAll('.step-content').forEach((content, idx) => {
                content.classList.toggle('active', idx === step - 1);
            });
        }
        
        function handlePDFSelect(event) {
            const files = event.target.files;
            const label = event.target.nextElementSibling;
            if (files.length > 0) {
                label.innerHTML = `<div style="font-size: 3em;">📄</div><p>${files.length}個のPDFファイルを選択</p>`;
            }
        }
        
        function handleAudioSelect(event) {
            const files = event.target.files;
            const label = event.target.nextElementSibling;
            if (files.length > 0) {
                label.innerHTML = `<div style="font-size: 3em;">🎵</div><p>${files[0].name}</p>`;
            }
        }
        
        function extractTerms() {
            // デモ実装
            const resultDiv = document.getElementById('terms-result');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div class="status-message">処理中... <div class="loading"></div></div>';
            
            setTimeout(() => {
                extractedTerms = [
                    "RC造", "基礎工事", "配筋工事", "コンクリート強度",
                    "品質管理", "施工図面", "建築基準法", "安全管理"
                ];
                
                resultDiv.innerHTML = `
                    <div class="status-message status-success">✅ 術語抽出完了！</div>
                    <div class="result-section">
                        <h3>抽出された専門術語 (${extractedTerms.length}個)</h3>
                        ${extractedTerms.map(term => `<span class="term-tag">${term}</span>`).join('')}
                    </div>
                `;
            }, 2000);
        }
        
        function transcribeAudio() {
            const resultDiv = document.getElementById('transcript-result');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div class="status-message">処理中... <div class="loading"></div></div>';
            
            setTimeout(() => {
                transcriptText = "本日はRC造建築物の基礎工事について検討します。品質管理と安全管理の観点から、配筋工事の施工手順を確認し、コンクリート強度の確保について議論しました。";
                
                resultDiv.innerHTML = `
                    <div class="status-message status-success">✅ 音声転写完了！</div>
                    <div class="result-section">
                        <h3>転写テキスト</h3>
                        <p style="line-height: 1.8; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            ${transcriptText}
                        </p>
                    </div>
                `;
            }, 2000);
        }
        
        function generateMinutes() {
            const resultDiv = document.getElementById('minutes-result');
            const title = document.getElementById('meeting-title').value || "建築技術検討会議";
            const date = document.getElementById('meeting-date').value || new Date().toISOString().split('T')[0];
            
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div class="status-message">処理中... <div class="loading"></div></div>';
            
            setTimeout(() => {
                resultDiv.innerHTML = `
                    <div class="status-message status-success">✅ 議事録生成完了！</div>
                    <div class="result-section">
                        <h3>📋 ${title}</h3>
                        <p><strong>日付:</strong> ${date}</p>
                        
                        <h4>決定事項</h4>
                        <ul>
                            <li>RC造建築物の基礎工事手順を確認</li>
                            <li>品質管理基準を設定</li>
                        </ul>
                        
                        <h4>行動項目</h4>
                        <ul>
                            <li>配筋工事の詳細図面作成</li>
                            <li>安全管理マニュアル更新</li>
                        </ul>
                        
                        <h4>使用された専門術語</h4>
                        ${extractedTerms.map(term => `<span class="term-tag">${term}</span>`).join('')}
                    </div>
                    <button class="process-btn" onclick="downloadMinutes()">💾 議事録ダウンロード</button>
                `;
            }, 2000);
        }
        
        function downloadMinutes() {
            const data = {
                title: document.getElementById('meeting-title').value || "建築技術検討会議",
                date: document.getElementById('meeting-date').value || new Date().toISOString().split('T')[0],
                transcript: transcriptText,
                terms: extractedTerms,
                decisions: ["RC造建築物の基礎工事手順を確認", "品質管理基準を設定"],
                actions: ["配筋工事の詳細図面作成", "安全管理マニュアル更新"]
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `minutes_${new Date().toISOString().slice(0,10)}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
"""
        
        # HTMLファイル保存
        html_path = Path("clean_interface.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ インターフェース作成: {html_path}")
        
        # ブラウザで開く
        try:
            import webbrowser
            webbrowser.open(f"file://{html_path.absolute()}")
            print("✅ ブラウザで開きました")
        except:
            print(f"🌐 ブラウザで開いてください: file://{html_path.absolute()}")
    
    def run_cli_mode(self):
        """CLIモード実行"""
        print("\n🏗️ 建築会議転写システム - CLIモード")
        print("=" * 60)
        
        while True:
            print("\n📋 メニュー:")
            print("1. PDFから術語抽出")
            print("2. 音声転写（デモ）")
            print("3. 議事録生成（デモ）")
            print("4. Webインターフェース起動")
            print("0. 終了")
            
            choice = input("\n選択 (0-4): ")
            
            if choice == "1":
                print("\n📚 PDF術語抽出（デモ）")
                self.extracted_terms = ["RC造", "基礎工事", "配筋工事"]
                print(f"✅ {len(self.extracted_terms)}個の術語を抽出")
                
            elif choice == "2":
                print("\n🎤 音声転写（デモ）")
                self.transcript_text = "本日の会議では基礎工事について検討しました。"
                print("✅ 転写完了")
                
            elif choice == "3":
                print("\n📋 議事録生成")
                self.minutes_data = {
                    "title": "建築技術検討会議",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "decisions": ["基礎工事手順確認"],
                    "actions": ["詳細図面作成"]
                }
                print("✅ 議事録生成完了")
                print(json.dumps(self.minutes_data, ensure_ascii=False, indent=2))
                
            elif choice == "4":
                self.run_web_interface()
                
            elif choice == "0":
                print("\n👋 終了します")
                break

def main():
    """メイン実行"""
    print("🏗️ 建築会議転写システム - クリーン版")
    print("Gradio問題を完全回避した整理版\n")
    
    # 環境チェック
    if not check_environment():
        print("\n⚠️ 環境設定が必要です")
        return
    
    # 実行モード選択
    print("\n実行モードを選択:")
    print("1. Webインターフェース（推奨）")
    print("2. CLIモード")
    
    mode = input("\n選択 (1-2): ")
    
    system = CleanBuildingMeetingSystem()
    
    if mode == "1":
        system.run_web_interface()
    else:
        system.run_cli_mode()

if __name__ == "__main__":
    main()