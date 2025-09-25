# ニュース要約掲示板アプリ | News Summary Display App

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)

プログラミング初心者向けのニュース要約表示アプリです。最新ニュースをOpenAI APIで要約し、Raspberry PiのLCD1602ディスプレイに横スクロール表示します。

A news summarization display app for programming beginners. Fetches latest news, summarizes them using OpenAI API, and displays on LCD1602 connected to Raspberry Pi.

## 📋 概要 | Overview

このアプリは以下の機能を提供します：

- **最新ニュース取得**: NewsAPIから日本の最新ニュースを取得
- **AI要約**: OpenAI APIを使用してニュースを100文字程度に要約
- **LCD表示**: LCD1602ディスプレイに横スクロールで表示
- **定期更新**: 設定可能な間隔でニュースを自動更新
- **エラーハンドリング**: ネットワーク障害やAPI制限に対応

This application provides:

- **Latest News Fetching**: Retrieves Japan's latest news from NewsAPI
- **AI Summarization**: Uses OpenAI API to summarize news in ~100 characters
- **LCD Display**: Shows scrolling text on LCD1602 display
- **Auto Update**: Automatically refreshes news at configurable intervals
- **Error Handling**: Handles network failures and API limitations

## 🛠️ 必要な機器 | Hardware Requirements

| 機器 | 説明 |
|------|------|
| Raspberry Pi 5 | メイン処理ユニット |
| LCD1602 | 16文字x2行 I²C接続ディスプレイ |
| ジャンパーワイヤ | 配線用 |
| ブレッドボード | プロトタイプ作成用 |

## 🔧 セットアップ | Setup

### 1. ハードウェア接続 | Hardware Connection

```
LCD1602 → Raspberry Pi
VCC     → 5V (Pin 2)
GND     → GND (Pin 6)
SDA     → SDA (Pin 3, GPIO 2)
SCL     → SCL (Pin 5, GPIO 3)
```

### 2. システム設定 | System Configuration

```bash
# I2Cを有効化 | Enable I2C
sudo raspi-config
# Interface Options → I2C → Yes

# 必要パッケージをインストール | Install required packages
sudo apt update
sudo apt install python3-pip python3-venv i2c-tools

# I2C接続確認 | Verify I2C connection
sudo i2cdetect -y 1
```

### 3. プロジェクトセットアップ | Project Setup

```bash
# リポジトリをクローン | Clone repository
git clone https://github.com/Murasan201/09-001-news-summary-display.git
cd 09-001-news-summary-display

# 仮想環境作成 | Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 依存関係をインストール | Install dependencies
pip install -r requirements.txt
```

### 4. APIキー設定 | API Key Configuration

```bash
# 環境設定ファイルを作成 | Create environment file
cp .env.template .env
```

`.env`ファイルを編集してAPIキーを設定：

```env
# NewsAPI: https://newsapi.org/
NEWS_API_KEY=your_newsapi_key_here

# OpenAI: https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key_here

# 更新間隔（分） | Update interval (minutes)
UPDATE_INTERVAL=30

# 取得ニュース件数 | Number of news articles
NEWS_COUNT=5
```

## 🚀 実行方法 | Usage

### 基本実行 | Basic Execution

```bash
python3 news_summary_display.py
```

### バックグラウンド実行 | Background Execution

```bash
nohup python3 news_summary_display.py &
```

### 自動起動設定 | Auto-start Configuration

systemdサービスとして設定:

```bash
sudo nano /etc/systemd/system/news-display.service
```

```ini
[Unit]
Description=News Summary Display App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/09-001-news-summary-display
ExecStart=/home/pi/09-001-news-summary-display/venv/bin/python news_summary_display.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable news-display.service
sudo systemctl start news-display.service
```

## 📁 プロジェクト構成 | Project Structure

```
09-001-news-summary-display/
├── README.md                           # このファイル
├── requirements.txt                    # Python依存関係
├── .env.template                       # 環境変数テンプレート
├── setup_instructions.md              # 詳細セットアップ手順
├── news_summary_display.py             # メインアプリケーション
├── 09-001_ニュース要約掲示板アプリ_要件定義書.md  # 要件定義書
└── CLAUDE.md                          # 開発ルール
```

## 🔧 主な機能 | Key Features

### NewsDisplayAppクラス | NewsDisplayApp Class

- **`get_latest_news()`**: NewsAPIから最新ニュースを取得
- **`summarize_text()`**: OpenAI APIでテキストを要約
- **`display_on_lcd()`**: LCDに横スクロール表示
- **`run_display_cycle()`**: 1回の表示サイクルを実行
- **`run()`**: メインループ

### 設定可能な項目 | Configurable Options

- 更新間隔 (UPDATE_INTERVAL)
- 取得ニュース件数 (NEWS_COUNT)
- LCD I²Cアドレス (コード内で変更可能)

## 🐛 トラブルシューティング | Troubleshooting

### LCDが動作しない | LCD Not Working

```bash
# I2Cアドレスを確認 | Check I2C address
sudo i2cdetect -y 1

# コード内のアドレス（0x27）を実際のアドレスに変更
# Change address (0x27) in code to actual address
```

### APIエラー | API Errors

- APIキーが正しく設定されているか確認
- インターネット接続を確認
- API利用制限をチェック

### 権限エラー | Permission Errors

```bash
# ユーザーをグループに追加 | Add user to groups
sudo usermod -a -G i2c,spi,gpio pi
```

## 📊 ログ | Logging

アプリケーションは詳細なログを出力します：

- **ファイル**: `news_display.log`
- **コンソール**: リアルタイム出力
- **レベル**: INFO, WARNING, ERROR

## 🎓 学習目的 | Educational Purpose

このプロジェクトは以下の技術を学習できます：

- **API統合**: NewsAPI、OpenAI APIの使用
- **ハードウェア制御**: Raspberry Pi、I²C通信
- **エラーハンドリング**: ネットワーク障害対応
- **ログ管理**: 適切なログ出力
- **環境変数管理**: 設定の外部化

## 📄 ライセンス | License

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

## 🤝 コントリビューション | Contributing

プルリクエストやイシューの報告を歓迎します。初心者向けのシンプルな実装を維持することを重視しています。

## 📚 参考リンク | Reference Links

- [NewsAPI Documentation](https://newsapi.org/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [RPLCD Library](https://rplcd.readthedocs.io/)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)

---

**作成日**: 2024年
**対象**: プログラミング初心者、Raspberry Pi入門者
**難易度**: 初級〜中級