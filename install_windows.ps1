# 建築会議転写システム - Windows自動インストールスクリプト
# PowerShell実行ポリシーの設定が必要: Set-ExecutionPolicy RemoteSigned

param(
    [string]$InstallPath = "$env:USERPROFILE\Desktop\building-meeting-transcriber",
    [switch]$SkipPython,
    [switch]$Minimal
)

# 色付きテキスト出力関数
function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Write-Success { param([string]$Text) Write-ColorText "✅ $Text" "Green" }
function Write-Info { param([string]$Text) Write-ColorText "🔍 $Text" "Cyan" }
function Write-Warning { param([string]$Text) Write-ColorText "⚠️ $Text" "Yellow" }
function Write-Error { param([string]$Text) Write-ColorText "❌ $Text" "Red" }

# メイン処理開始
Write-ColorText "🏗️ 建築会議転写システム - 自動インストーラー" "Magenta"
Write-ColorText "=" * 60 "Magenta"

# 管理者権限チェック
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "管理者権限での実行を推奨します"
    Write-Info "右クリック → '管理者として実行' でPowerShellを起動してください"
}

# Step 1: Python 3.12.10の確認とインストール案内
Write-Info "Step 1: Python環境チェック"

try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion -match "Python 3\.12\.") {
        Write-Success "Python 3.12.x が見つかりました: $pythonVersion"
    } elseif ($pythonVersion -match "Python 3\.(\d+)\.") {
        $majorVersion = $matches[1]
        if ([int]$majorVersion -ge 8 -and [int]$majorVersion -le 12) {
            Write-Warning "Python $pythonVersion が見つかりました（3.12推奨）"
            Write-Info "現在のバージョンでも動作しますが、3.12.10が最適です"
        } else {
            Write-Error "非対応のPythonバージョン: $pythonVersion"
            Write-Info "Python 3.12.10をインストールしてください"
            Write-Info "ダウンロード: https://www.python.org/downloads/release/python-31210/"
            exit 1
        }
    } else {
        throw "Python not found"
    }
} catch {
    if (-not $SkipPython) {
        Write-Error "Pythonが見つかりません"
        Write-Info "Python 3.12.10のインストールが必要です"
        Write-Info ""
        Write-Info "📋 手動インストール手順:"
        Write-Info "1. https://www.python.org/downloads/release/python-31210/ にアクセス"
        Write-Info "2. 'Windows installer (64-bit)' をダウンロード"
        Write-Info "3. インストール時に 'Add python.exe to PATH' をチェック"
        Write-Info "4. インストール後、新しいPowerShellでこのスクリプトを再実行"
        
        $install = Read-Host "Pythonインストール後にEnterを押してください（スキップする場合は 'skip' を入力）"
        if ($install -eq "skip") {
            Write-Warning "Pythonインストールをスキップしました"
        } else {
            # 再チェック
            try {
                $pythonVersion = python --version 2>$null
                Write-Success "Python検出: $pythonVersion"
            } catch {
                Write-Error "Pythonがまだ見つかりません。手動でインストールしてください"
                exit 1
            }
        }
    }
}

# Step 2: プロジェクトディレクトリの作成
Write-Info "Step 2: プロジェクトディレクトリ設定"

if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-Success "作成: $InstallPath"
} else {
    Write-Info "既存のディレクトリを使用: $InstallPath"
}

Set-Location $InstallPath

# Step 3: GitHubからクローン
Write-Info "Step 3: プロジェクトファイル取得"

$projectPath = Join-Path $InstallPath "meetingnote"

if (-not (Test-Path $projectPath)) {
    try {
        git --version | Out-Null
        Write-Info "Gitを使用してクローン中..."
        git clone https://github.com/aiboy2000/meetingnote.git
        Write-Success "GitHubからクローン完了"
    } catch {
        Write-Warning "Gitが見つかりません。手動ダウンロードを案内します"
        Write-Info "1. https://github.com/aiboy2000/meetingnote にアクセス"
        Write-Info "2. 'Code' → 'Download ZIP' をクリック"
        Write-Info "3. ZIPを $InstallPath に展開"
        Write-Info "4. フォルダ名を 'meetingnote' に変更"
        
        Read-Host "ダウンロード完了後、Enterを押してください"
    }
} else {
    Write-Info "既存のプロジェクトを使用"
}

if (-not (Test-Path $projectPath)) {
    Write-Error "プロジェクトファイルが見つかりません"
    exit 1
}

Set-Location $projectPath

# Step 4: 仮想環境の作成
Write-Info "Step 4: 仮想環境セットアップ"

$venvPath = "meeting_env"

if (-not (Test-Path $venvPath)) {
    Write-Info "仮想環境を作成中..."
    python -m venv $venvPath
    Write-Success "仮想環境作成完了"
} else {
    Write-Info "既存の仮想環境を使用"
}

# 仮想環境のactivateスクリプトパス
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    Write-Info "仮想環境を有効化中..."
    & $activateScript
    Write-Success "仮想環境有効化完了"
} else {
    Write-Error "仮想環境のactivateスクリプトが見つかりません"
}

# Step 5: パッケージインストール
Write-Info "Step 5: 必要パッケージのインストール"

# pipアップグレード
Write-Info "pipを更新中..."
python -m pip install --upgrade pip --quiet

if ($Minimal) {
    Write-Info "最小構成でインストール中..."
    $packages = @("gradio==4.44.0")
} else {
    Write-Info "完全構成でインストール中..."
    $packages = @(
        "gradio==4.44.0",
        "pdfplumber",
        "pandas",
        "numpy",
        "requests"
    )
}

foreach ($package in $packages) {
    Write-Info "インストール中: $package"
    try {
        python -m pip install $package --quiet
        Write-Success "完了: $package"
    } catch {
        Write-Warning "スキップ: $package (エラーが発生しました)"
    }
}

# Step 6: インストール確認
Write-Info "Step 6: インストール確認"

try {
    python -c "import gradio; print(f'Gradio {gradio.__version__}')" 2>$null
    Write-Success "Gradio動作確認OK"
} catch {
    Write-Error "Gradioの動作確認に失敗"
}

# Step 7: 起動スクリプト作成
Write-Info "Step 7: 起動スクリプト作成"

$batchContent = @"
@echo off
cd /d "$projectPath"
call $venvPath\Scripts\activate
echo 🏗️ 建築会議転写システムを起動中...
python workflow_app.py
pause
"@

$batchPath = Join-Path $InstallPath "start_app.bat"
Set-Content -Path $batchPath -Value $batchContent -Encoding UTF8
Write-Success "起動スクリプト作成: $batchPath"

# Step 8: デスクトップショートカット作成（オプション）
$createShortcut = Read-Host "デスクトップにショートカットを作成しますか？ (y/n)"
if ($createShortcut -eq "y") {
    try {
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\建築会議転写システム.lnk")
        $Shortcut.TargetPath = $batchPath
        $Shortcut.WorkingDirectory = $projectPath
        $Shortcut.Description = "建築会議転写システム"
        $Shortcut.Save()
        Write-Success "デスクトップショートカット作成完了"
    } catch {
        Write-Warning "ショートカット作成に失敗しました"
    }
}

# 完了メッセージ
Write-ColorText "" 
Write-ColorText "🎉 インストール完了！" "Green"
Write-ColorText "=" * 50 "Green"
Write-Success "プロジェクトパス: $projectPath"
Write-Success "起動スクリプト: $batchPath"

Write-Info "🚀 起動方法:"
Write-Info "1. $batchPath をダブルクリック"
Write-Info "2. または以下のコマンドを実行:"
Write-ColorText "   cd `"$projectPath`"" "White"
Write-ColorText "   $venvPath\Scripts\activate" "White"
Write-ColorText "   python workflow_app.py" "White"

Write-Info "🧪 テスト実行:"
$runTest = Read-Host "今すぐテスト実行しますか？ (y/n)"
if ($runTest -eq "y") {
    Write-Info "アプリケーションを起動中..."
    python workflow_app.py
}

Write-ColorText "📖 詳細なマニュアル: WINDOWS_INSTALL_GUIDE.md を参照" "Cyan"
Write-ColorText "🆘 問題が発生した場合: python check_env.py を実行" "Cyan"