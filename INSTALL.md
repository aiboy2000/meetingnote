# 建築業務会議転写システム - インストールガイド

## システム要件

- Python 3.8以上
- 16GB以上のRAM推奨
- GPU（オプション、Whisper高速化用）

## インストール手順

### 1. 仮想環境の作成

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. MeCab（日本語形態素解析）のインストール

#### Ubuntu/Debian
```bash
sudo apt-get install mecab libmecab-dev mecab-ipadic-utf8
```

#### macOS
```bash
brew install mecab mecab-ipadic
```

#### Windows
- https://github.com/ikegami-yukino/mecab/releases からダウンロードしてインストール

### 4. 動作確認

```bash
# 構文チェック
python syntax_test.py

# 基本機能テスト（依存パッケージインストール後）
python quick_test.py
```

## 使用方法

### Webインターフェース版

```bash
python main.py
```

ブラウザで http://localhost:7860 にアクセス

### コマンドライン版（開発中）

```bash
python cli.py --input audio.mp4 --output minutes.json
```

## データの準備

1. **専門術語PDF**: `data/pdfs/` に建築関連のPDFファイルを配置
2. **会議音声**: MP4、WAV、MP3形式をサポート

## トラブルシューティング

### GPU使用時の設定

```bash
# CUDA対応PyTorchをインストール
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### メモリ不足の場合

- Whisperモデルサイズを "base" または "small" に変更
- バッチサイズを調整

### MeCab関連エラー

```bash
pip install mecab-python3
```

## ディレクトリ構造

```
meetingnote/
├── src/                    # コアモジュール
│   ├── term_extractor.py   # 専門術語抽出
│   ├── vector_db.py        # ベクター検索
│   ├── transcriber.py      # 音声転写
│   ├── minutes_generator.py # 議事録生成
│   └── tagger.py          # タグ付け
├── data/                   # データディレクトリ
│   ├── pdfs/              # 専門術語PDF
│   └── vector_index/      # ベクターDB
├── main.py                # Webアプリ
├── quick_test.py          # テストスクリプト
└── requirements.txt       # 依存パッケージ
```

## 開発者向け

### 新機能追加

1. `src/` 下に新しいモジュールを作成
2. `main.py` でインターフェースに統合
3. `quick_test.py` にテストを追加

### デバッグ

```bash
# ログレベルを DEBUG に設定
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m src.term_extractor  # 個別モジュールテスト
```