# トラブルシューティング
# Troubleshooting Guide

このドキュメントでは、ニュース要約掲示板アプリの開発・実行時に発生したエラーと、その解決方法を記録しています。

---

## エラー1: 外部管理環境エラー (Externally Managed Environment)

### 発生タイミング
ライブラリのインストール時

### 実行したコマンド
```bash
pip install -r requirements.txt
```

### エラーメッセージ
```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.

    If you wish to install a non-Debian package, please install
    python3-xyz-pip and use the command xyz-pip install instead.

    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
```

### 原因
Debian/Ubuntu系のLinuxディストリビューションでは、Python 3.11以降、システムのPythonパッケージ管理を保護するため、`pip`でのシステムワイドなインストールが制限されています。これは、システムの安定性を保つための仕様です（PEP 668）。

### 解決方法
仮想環境（virtual environment）を作成し、その中でライブラリをインストールします。

#### 手順1: 仮想環境の作成
```bash
python3 -m venv venv
```

これにより、プロジェクトディレクトリ内に`venv`という名前の仮想環境が作成されます。

#### 手順2: 仮想環境のpipを使用してライブラリをインストール
```bash
./venv/bin/pip install -r requirements.txt
```

#### 手順3: インストール結果の確認
```
Collecting feedparser (from -r requirements.txt (line 5))
  Downloading feedparser-6.0.11-py3-none-any.whl.metadata (2.4 kB)
Collecting openai (from -r requirements.txt (line 8))
  Downloading openai-1.55.3-py3-none-any.whl.metadata (25 kB)
Collecting RPLCD>=1.3.0 (from -r requirements.txt (line 11))
  Downloading RPLCD-1.3.1-py2.py3-none-any.whl.metadata (6.4 kB)
Collecting smbus2>=0.4.0 (from -r requirements.txt (line 14))
  Downloading smbus2-0.5.0-py3-none-any.whl.metadata (6.3 kB)
Collecting python-dotenv (from -r requirements.txt (line 17))
  Downloading python_dotenv-1.0.1-py3-none-any.whl.metadata (23 kB)
...（依存関係のインストール）...
Successfully installed RPLCD-1.3.1 ... python-dotenv-1.0.1 ...
```

### プログラム実行時の注意
仮想環境を作成した場合、プログラム実行時も仮想環境内のPythonを使用する必要があります。

```bash
# 正しい実行方法
./venv/bin/python3 news_summary_display.py

# または、仮想環境を有効化してから実行
source venv/bin/activate
python3 news_summary_display.py
```

---

## エラー2: OpenAI APIキー認証エラー (401 Unauthorized)

### 発生タイミング
プログラム実行時（初回テスト実行時）

### エラーメッセージ
```
2025-10-26 13:24:18,607 - ERROR - 要約生成エラー: Error code: 401 - {'error': {'message': 'Incorrect API key provided: your_ope***key_here. You can find your API key at https://platform.openai.com/account/api-keys.', 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_api_key'}}
```

### 原因
`.env`ファイルに設定されているOpenAI APIキーがプレースホルダー（`your_openai_api_key_here`）のままで、実際のAPIキーに置き換えられていませんでした。

### 解決方法
OpenAI APIキーを取得し、`.env`ファイルに正しく設定します。

#### 手順1: OpenAI APIキーの取得
1. https://platform.openai.com/ にアクセス
2. アカウントにログイン
3. API Keys セクションで新しいAPIキーを作成

#### 手順2: .envファイルの編集
`.env`ファイルを開き、`OPENAI_API_KEY`の値を実際のAPIキーに置き換えます。

```env
# 修正前（プレースホルダー）
OPENAI_API_KEY=your_openai_api_key_here

# 修正後（実際のAPIキー）
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxx
```

#### 手順3: 動作確認
プログラムを再実行し、RSS取得とAPI呼び出しが正常に動作することを確認します。

```bash
./venv/bin/python3 news_summary_display.py
```

### セキュリティ上の注意
- `.env`ファイルは`.gitignore`に追加し、Gitリポジトリにコミットしないようにしてください
- APIキーを他人と共有しないでください
- APIキーが漏洩した場合は、すぐにOpenAIのダッシュボードで無効化し、新しいキーを生成してください

---

## エラー3: Temperature パラメータ非サポートエラー (400 Bad Request)

### 発生タイミング
OpenAI API呼び出し時（gpt-5-miniモデル使用時）

### エラーメッセージ
```
2025-10-26 13:28:47,152 - ERROR - 要約生成エラー: Error code: 400 - {'error': {'message': "Unsupported value: 'temperature' does not support 0.3 with this model. Only the default (1) value is supported.", 'type': 'invalid_request_error', 'param': 'temperature', 'code': 'unsupported_value'}}
```

### 原因
gpt-5-miniモデルでは、`temperature`パラメータにデフォルト値（1）以外を指定することができません。コード内で`temperature=0.3`を指定していたため、エラーが発生しました。

一般的なOpenAI APIモデル（GPT-4系など）では`temperature`パラメータに0〜2の範囲の値を指定できますが、gpt-5-miniではこのパラメータのカスタマイズがサポートされていません。

### 解決方法
`temperature`パラメータを削除し、デフォルト値を使用します。

#### コード修正箇所
`news_summary_display.py`の`summarize_with_chatgpt`関数内のAPI呼び出し部分を修正します。

**修正前:**
```python
response = openai_client.chat.completions.create(
    model="gpt-5-mini",
    temperature=0.3,  # ← この行が原因
    messages=[
        {"role": "system", "content": "あなたは有能な技術ニュース要約アシスタントです。"},
        {"role": "user", "content": prompt}
    ]
)
```

**修正後:**
```python
response = openai_client.chat.completions.create(
    model="gpt-5-mini",
    # temperature パラメータを削除（デフォルト値1を使用）
    messages=[
        {"role": "system", "content": "あなたは有能な技術ニュース要約アシスタントです。"},
        {"role": "user", "content": prompt}
    ]
)
```

#### 動作確認
修正後、プログラムを実行すると、正常に要約が生成されることを確認できます。

```bash
./venv/bin/python3 news_summary_display.py
```

**成功時のログ出力例:**
```
2025-10-26 13:30:51,725 - INFO - LCDを初期化しました
2025-10-26 13:30:51,725 - INFO - ニュース要約掲示板アプリを開始します（更新間隔: 180分 = 3時間）
2025-10-26 13:30:51,725 - INFO - MIT Technology Review AI から記事を取得中...
2025-10-26 13:30:52,174 - INFO - 3件の記事を取得しました
2025-10-26 13:31:18,129 - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2025-10-26 13:31:18,136 - INFO - MIT Technology Review AIの要約を生成しました
2025-10-26 13:31:18,136 - INFO - AI News から記事を取得中...
2025-10-26 13:31:21,537 - INFO - 3件の記事を取得しました
2025-10-26 13:31:33,500 - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2025-10-26 13:31:33,502 - INFO - AI Newsの要約を生成しました
2025-10-26 13:31:33,502 - INFO - ITmedia AI+ から記事を取得中...
2025-10-26 13:31:33,756 - INFO - 3件の記事を取得しました
2025-10-26 13:31:50,122 - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2025-10-26 13:31:50,127 - INFO - ITmedia AI+の要約を生成しました
```

### 補足: temperatureパラメータとは
`temperature`は、AIモデルの出力のランダム性を制御するパラメータです。
- **低い値（例: 0.3）**: 決定論的で一貫性のある出力
- **高い値（例: 1.5）**: よりクリエイティブで多様な出力
- **デフォルト値（1）**: バランスの取れた出力

gpt-5-miniでは、モデルの最適化により、このパラメータの調整が制限されています。

---

## まとめ

このプロジェクトで発生した3つのエラーは、いずれも初心者が遭遇しやすい典型的な問題です。

1. **エラー1（外部管理環境）**: 現代のLinuxシステムにおける標準的な制限で、仮想環境の使用が推奨されています
2. **エラー2（APIキー未設定）**: 環境変数の設定ミスによる典型的な認証エラーです
3. **エラー3（Temperature非サポート）**: 新しいモデル（gpt-5-mini）特有の仕様で、公式ドキュメントの確認が重要です

これらのトラブルシューティング経験は、Pythonプロジェクト開発における重要なノウハウとなります。
