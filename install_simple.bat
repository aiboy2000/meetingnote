@echo off
chcp 65001 >nul
title 建築会議転写システム - 簡単インストーラー

echo.
echo ========================================
echo 🏗️ 建築会議転写システム
echo    Windows簡単インストーラー
echo ========================================
echo.

:: 管理者権限チェック
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️ 管理者権限で実行することを推奨します
    echo 右クリック → "管理者として実行" を選択してください
    echo.
    pause
)

:: Python確認
echo 🔍 Python環境をチェック中...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ❌ Pythonが見つかりません
    echo.
    echo 📋 Pythonインストール手順:
    echo 1. https://www.python.org/downloads/release/python-31210/ にアクセス
    echo 2. "Windows installer (64-bit)" をダウンロード
    echo 3. インストール時に "Add python.exe to PATH" をチェック
    echo 4. インストール後、このスクリプトを再実行
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python検出: %PYTHON_VERSION%

:: 作業ディレクトリ作成
set INSTALL_DIR=%USERPROFILE%\Desktop\building-meeting-transcriber
echo.
echo 📁 インストールディレクトリ: %INSTALL_DIR%

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo ✅ ディレクトリ作成完了
) else (
    echo ✅ 既存ディレクトリを使用
)

cd /d "%INSTALL_DIR%"

:: GitHubからダウンロード
set PROJECT_DIR=%INSTALL_DIR%\meetingnote

if not exist "%PROJECT_DIR%" (
    echo.
    echo 📥 プロジェクトファイルをダウンロード中...
    
    :: Gitが利用可能かチェック
    git --version >nul 2>&1
    if %errorLevel% equ 0 (
        echo 🔄 Git使用してクローン中...
        git clone https://github.com/aiboy2000/meetingnote.git
        if %errorLevel% equ 0 (
            echo ✅ GitHubからクローン完了
        ) else (
            echo ❌ Gitクローンに失敗
            goto MANUAL_DOWNLOAD
        )
    ) else (
        :MANUAL_DOWNLOAD
        echo.
        echo ⚠️ Gitが見つかりません。手動ダウンロードが必要です
        echo.
        echo 📋 手動ダウンロード手順:
        echo 1. https://github.com/aiboy2000/meetingnote にアクセス
        echo 2. "Code" ボタン → "Download ZIP" をクリック
        echo 3. ZIPファイルを %INSTALL_DIR% に展開
        echo 4. フォルダ名を "meetingnote" に変更
        echo 5. 完了後、何かキーを押してください
        echo.
        pause
        
        if not exist "%PROJECT_DIR%" (
            echo ❌ プロジェクトフォルダが見つかりません
            echo 手動ダウンロードを完了してから再実行してください
            pause
            exit /b 1
        )
    )
) else (
    echo ✅ 既存のプロジェクトを使用
)

cd /d "%PROJECT_DIR%"

:: 仮想環境作成
echo.
echo 🔧 仮想環境をセットアップ中...

if not exist "meeting_env" (
    python -m venv meeting_env
    if %errorLevel% equ 0 (
        echo ✅ 仮想環境作成完了
    ) else (
        echo ❌ 仮想環境作成に失敗
        pause
        exit /b 1
    )
) else (
    echo ✅ 既存の仮想環境を使用
)

:: 仮想環境有効化
call meeting_env\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo ❌ 仮想環境の有効化に失敗
    pause
    exit /b 1
)

echo ✅ 仮想環境有効化完了

:: パッケージインストール
echo.
echo 📦 必要パッケージをインストール中...

:: pipアップグレード
python -m pip install --upgrade pip --quiet

:: 基本パッケージ
echo Installing: Gradio...
python -m pip install gradio==4.44.0 --quiet
if %errorLevel% equ 0 (
    echo OK: Gradio install completed
) else (
    echo ERROR: Gradio install failed
)

:: オプションパッケージ
echo.
set /p INSTALL_EXTRA="Install additional packages (PDF processing etc.)? (y/n): "
if /i "%INSTALL_EXTRA%"=="y" (
    echo Installing additional packages...
    python -m pip install pdfplumber pandas requests --quiet
    echo OK: Additional packages completed
)

:: インストール確認
echo.
echo Testing installation...
python -c "import gradio; print('OK: Gradio test successful')" 2>nul
if %errorLevel% neq 0 (
    echo ERROR: Gradio test failed
)

:: 起動スクリプト作成
echo.
echo 📜 起動スクリプトを作成中...

set START_SCRIPT=%INSTALL_DIR%\start_app.bat
echo @echo off > "%START_SCRIPT%"
echo chcp 65001 ^>nul >> "%START_SCRIPT%"
echo cd /d "%PROJECT_DIR%" >> "%START_SCRIPT%"
echo call meeting_env\Scripts\activate.bat >> "%START_SCRIPT%"
echo echo 🏗️ 建築会議転写システムを起動中... >> "%START_SCRIPT%"
echo python workflow_app.py >> "%START_SCRIPT%"
echo pause >> "%START_SCRIPT%"

echo ✅ 起動スクリプト作成: %START_SCRIPT%

:: デスクトップショートカット作成
set /p CREATE_SHORTCUT="デスクトップにショートカットを作成しますか？ (y/n): "
if /i "%CREATE_SHORTCUT%"=="y" (
    :: PowerShellでショートカット作成
    powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\建築会議転写システム.lnk'); $Shortcut.TargetPath = '%START_SCRIPT%'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = '建築会議転写システム'; $Shortcut.Save()" 2>nul
    if %errorLevel% equ 0 (
        echo ✅ デスクトップショートカット作成完了
    ) else (
        echo ⚠️ ショートカット作成に失敗（権限不足の可能性）
    )
)

:: 完了メッセージ
echo.
echo ========================================
echo 🎉 インストール完了！
echo ========================================
echo.
echo 📍 インストール場所: %PROJECT_DIR%
echo 🚀 起動スクリプト: %START_SCRIPT%
echo.
echo 💡 起動方法:
echo   1. デスクトップの "建築会議転写システム" をダブルクリック
echo   2. または %START_SCRIPT% をダブルクリック
echo.
echo 📖 詳細マニュアル: WINDOWS_INSTALL_GUIDE.md
echo 🆘 問題が発生した場合: python check_env.py を実行
echo.

:: テスト実行オプション
set /p RUN_TEST="今すぐテスト実行しますか？ (y/n): "
if /i "%RUN_TEST%"=="y" (
    echo.
    echo 🚀 アプリケーションを起動中...
    python workflow_app.py
)

echo.
echo インストール完了！何かキーを押すと終了します...
pause >nul