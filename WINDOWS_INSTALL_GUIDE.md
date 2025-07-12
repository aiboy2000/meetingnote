# 建築会議転写システム - Windows完全インストールガイド

## 📋 システム要件

- **OS**: Windows 10/11 (64bit)
- **Python**: 3.12.10 (推奨)
- **RAM**: 8GB以上 (16GB推奨)
- **ストレージ**: 10GB以上の空き容量
- **ネットワーク**: インターネット接続（パッケージダウンロード用）

---

## 🚀 Step 1: Python 3.12.10のインストール

### 1.1 Python公式サイトからダウンロード

1. **ブラウザで以下のURLにアクセス**:
   ```
   https://www.python.org/downloads/release/python-31210/
   ```

2. **ダウンロードファイルを選択**:
   - **64bit Windows**: `Windows installer (64-bit)` をクリック
   - ファイル名: `python-3.12.10-amd64.exe`

### 1.2 Pythonインストール実行

1. **ダウンロードしたファイルを右クリック** → 「管理者として実行」

2. **インストーラー設定**:
   ```
   ✅ Add python.exe to PATH  （重要！必ずチェック）
   ✅ Install for all users
   ```

3. **「Install Now」をクリック**

4. **インストール完了後、「Close」をクリック**

### 1.3 インストール確認

PowerShellまたはコマンドプロンプトを開いて確認:

```powershell
# PowerShellを管理者として開く
python --version
# 出力例: Python 3.12.10

pip --version
# 出力例: pip 24.0 from C:\Users\...\Python\Python312\lib\site-packages\pip (python 3.12)
```

---

## 🔧 Step 2: 開発環境のセットアップ

### 2.1 プロジェクトディレクトリ作成

```powershell
# デスクトップに作業フォルダを作成
cd Desktop
mkdir building-meeting-transcriber
cd building-meeting-transcriber
```

### 2.2 GitHubからプロジェクトクローン

```powershell
# Gitが未インストールの場合は https://git-scm.com からインストール
git clone https://github.com/aiboy2000/meetingnote.git
cd meetingnote
```

### 2.3 仮想環境の作成と有効化

```powershell
# 仮想環境作成
python -m venv meeting_env

# 仮想環境を有効化
meeting_env\Scripts\activate

# 有効化確認（プロンプトに (meeting_env) が表示される）
# (meeting_env) PS C:\Users\...\meetingnote>
```

---

## 📦 Step 3: 必要パッケージのインストール

### 3.1 pipのアップグレード

```powershell
python -m pip install --upgrade pip
```

### 3.2 基本パッケージのインストール

```powershell
# 基本パッケージ（軽量版）
pip install gradio==4.44.0

# 確認
python -c "import gradio; print(f'Gradio {gradio.__version__} インストール成功')"
```

### 3.3 追加パッケージ（オプション）

```powershell
# PDF処理用
pip install pdfplumber

# 音声処理用（Whisperなど）
pip install openai-whisper

# データ処理用
pip install pandas numpy

# 機械学習用
pip install sentence-transformers transformers

# ベクトル検索用
pip install faiss-cpu
```

**⚠️ 注意**: すべてのパッケージを一度にインストールするとエラーが発生する可能性があります。必要に応じて段階的にインストールしてください。

---

## 🧪 Step 4: アプリケーションのテスト

### 4.1 環境チェック

```powershell
python check_env.py
```

期待される出力:
```
🐍 Python: 3.12.10
   ✅ サポートされているバージョンです

📦 gradio: 4.44.0
🔍 Gradio互換性チェック:
   現在のバージョン: 4.44.0
   ✅ 新しいバージョンです（推奨）
```

### 4.2 基本機能テスト

#### シンプル版テスト
```powershell
python stable_app.py
```

ブラウザが自動で開き、`http://127.0.0.1:7860` でアプリにアクセスできるはずです。

#### ワークフロー版テスト（推奨）
```powershell
python workflow_app.py
```

### 4.3 HTML版テスト（フォールバック）

Gradioで問題が発生した場合:

```powershell
python simple_workflow.py
```

HTMLファイルが生成され、ブラウザで開くことができます。

---

## 🎯 Step 5: 実際の使用

### 5.1 ワークフロー版の使用（推奨）

```powershell
# 仮想環境を有効化
meeting_env\Scripts\activate

# アプリケーション起動
python workflow_app.py
```

**使用手順**:
1. **ステップ1**: PDFファイルをアップロード → 専門術語抽出
2. **ステップ2**: 音声/動画ファイルをアップロード → 転写
3. **ステップ3**: 会議情報入力 → 議事録生成

### 5.2 サンプルデータでのテスト

アプリ内の「サンプルデータ読み込み」ボタンを使用して、すぐに機能を確認できます。

---

## 🔧 トラブルシューティング

### ❌ 問題1: 「python コマンドが見つからない」

**解決法**:
```powershell
# PATHを確認
echo $env:PATH

# Pythonの場所を確認
where python

# 見つからない場合は、Pythonを再インストールし、「Add to PATH」を確認
```

### ❌ 問題2: 「pip install でエラー」

**解決法**:
```powershell
# pipを最新に更新
python -m pip install --upgrade pip

# 個別にインストール
pip install --no-cache-dir gradio==4.44.0

# Microsoft Visual C++ Build Toolsが必要な場合
# https://visualstudio.microsoft.com/visual-cpp-build-tools/ からダウンロード
```

### ❌ 問題3: 「Gradioが起動しない」

**解決法**:
```powershell
# 古いGradioをアンインストール
pip uninstall gradio -y

# 安定版をインストール
pip install gradio==4.44.0

# それでもダメな場合はHTML版を使用
python simple_workflow.py
```

### ❌ 問題4: 「仮想環境が有効化されない」

**解決法**:
```powershell
# 実行ポリシーを変更（管理者権限が必要）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 仮想環境を再作成
rmdir /s meeting_env
python -m venv meeting_env
meeting_env\Scripts\activate
```

### ❌ 問題5: 「ポート7860が使用中」

**解決法**:
```powershell
# 使用中のポートを確認
netstat -an | findstr :7860

# アプリ起動時に別のポートを指定
# workflow_app.py の最後の部分で server_port=7861 に変更
```

---

## 📋 日常使用のクイックスタート

### 毎回の起動手順

```powershell
# 1. プロジェクトフォルダに移動
cd Desktop\building-meeting-transcriber\meetingnote

# 2. 仮想環境を有効化
meeting_env\Scripts\activate

# 3. アプリケーション起動
python workflow_app.py

# 4. ブラウザで http://127.0.0.1:7860 にアクセス
```

### バッチファイルを作成（便利な起動方法）

`start_app.bat` というファイルを作成:

```batch
@echo off
cd /d "C:\Users\%USERNAME%\Desktop\building-meeting-transcriber\meetingnote"
call meeting_env\Scripts\activate
python workflow_app.py
pause
```

このバッチファイルをダブルクリックするだけでアプリが起動します。

---

## 🎁 おまけ: 高度な設定

### FFmpegのインストール（音声処理の高度化）

1. **Chocolateyをインストール** (管理者権限のPowerShell):
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **FFmpegをインストール**:
   ```powershell
   choco install ffmpeg
   ```

### MeCab（日本語形態素解析）のインストール

1. **MeCab for Windowsをダウンロード**:
   ```
   https://github.com/ikegami-yukino/mecab/releases
   ```

2. **インストール後**:
   ```powershell
   pip install mecab-python3
   pip install fugashi[unidic]
   ```

---

## ✅ インストール完了チェックリスト

- [ ] Python 3.12.10がインストール済み
- [ ] `python --version` でバージョン確認済み
- [ ] 仮想環境が作成・有効化済み
- [ ] Gradio 4.44.0がインストール済み
- [ ] `python stable_app.py` で動作確認済み
- [ ] `python workflow_app.py` で動作確認済み
- [ ] ブラウザでアプリにアクセス可能
- [ ] サンプルデータでテスト済み

---

## 📞 サポート

問題が発生した場合:

1. **ログを確認**: エラーメッセージをコピーして保存
2. **環境チェック**: `python check_env.py` を実行
3. **GitHub Issues**: https://github.com/aiboy2000/meetingnote/issues で報告

**よくある質問と解決法はこのドキュメントのトラブルシューティングセクションを参照してください。**

---

🎉 **インストール完了！建築会議の効率化をお楽しみください！**