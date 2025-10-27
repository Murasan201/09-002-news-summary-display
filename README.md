# ニュース要約掲示板アプリ | News Summary Display App

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)

プログラミング初心者向けのニュース要約表示アプリです。複数のニュースサイトからRSSフィードを取得し、OpenAI APIで要約し、Raspberry PiのSSD1306 OLEDディスプレイに日本語で横スクロール表示します。

A news summarization display app for programming beginners. Fetches RSS feeds from multiple news sites, summarizes them using OpenAI API, and displays in Japanese on SSD1306 OLED connected to Raspberry Pi.

## 📋 概要 | Overview

このアプリは以下の機能を提供します：

- **RSSフィード取得**: 複数のニュースサイトから最新AI関連記事を取得（APIキー不要）
- **AI要約**: OpenAI API（gpt-5-mini）で複数記事を統合し250文字以内に要約
- **OLED表示**: SSD1306 OLEDディスプレイに日本語で横スクロール表示
- **定期更新**: 3時間間隔でニュースを自動更新
- **シミュレーションモード**: OLED未接続でもコンソールで動作確認可能

This application provides:

- **RSS Feed Fetching**: Retrieves latest AI news from multiple sites (no API key required)
- **AI Summarization**: Uses OpenAI API (gpt-5-mini) to summarize multiple articles within 250 characters
- **OLED Display**: Shows Japanese scrolling text on SSD1306 OLED display
- **Auto Update**: Automatically refreshes news every 3 hours
- **Simulation Mode**: Works on console even without OLED connection

## 🛠️ 必要な機器 | Hardware Requirements

| 機器 | 説明 |
|------|------|
| Raspberry Pi 5 | メイン処理ユニット |
| SSD1306 OLEDモジュール | 128×64ピクセル I²C接続ディスプレイ（日本語表示対応） |
| BSS138レベル変換モジュール | 4チャンネル双方向（3.3V⇔5V変換）※5V OLED使用時のみ |
| ジャンパーワイヤ | 配線用（オス-オス、10本程度） |
| ブレッドボード | プロトタイプ作成用 |

### ⚠️ 重要な注意事項

**🔴 5V OLED を Raspberry Pi に直結しないでください！**

- Raspberry Pi の GPIO は **3.3V** です
- 5V OLED と直結すると、通信できないだけでなく **GPIO を破損する可能性** があります
- **必ずレベル変換モジュール（BSS138方式）を使用** してください
- 3.3V 動作の OLED モジュールの使用を推奨

## 🔧 セットアップ | Setup

### 1. ハードウェア接続 | Hardware Connection

**レベル変換使用時**（5V OLED の場合）:
```
[Raspberry Pi 5]       [レベル変換]        [5V OLED]
Pin 1  (3.3V)  ------> LV
Pin 3  (GPIO2) ------> LV-SDA  ----> HV-SDA  ----> SDA
Pin 5  (GPIO3) ------> LV-SCL  ----> HV-SCL  ----> SCL
Pin 6  (GND)   ------> GND     <---- GND     <---- GND
                       HV      <---- VCC (5V from Pin 2)
```

**3.3V OLED の場合**（レベル変換不要、推奨）:
```
[Raspberry Pi 5]       [3.3V OLED]
Pin 1  (3.3V)  ------> VCC
Pin 3  (GPIO2) ------> SDA
Pin 5  (GPIO3) ------> SCL
Pin 6  (GND)   ------> GND
```

**注意**: 5V OLEDの場合、レベル変換なしで直接接続すると、Raspberry Pi GPIOピンが破損する可能性があります。

### 2. システム設定 | System Configuration

```bash
# I2Cを有効化 | Enable I2C
sudo raspi-config
# Interface Options → I2C → Yes

# 必要パッケージをインストール | Install required packages
sudo apt update
sudo apt install python3-pip python3-venv i2c-tools

# I2C接続確認 | Verify I2C connection
# OLEDが接続されていれば 0x3C または 0x3D が表示されます
# If OLED is connected, you should see 0x3C or 0x3D
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

# 日本語フォントをダウンロード | Download Japanese font
cd assets/fonts/
wget https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf
wget https://raw.githubusercontent.com/googlefonts/noto-cjk/main/LICENSE
cd ../..
```

### 4. APIキー設定 | API Key Configuration

**必要なAPIキー**: OpenAI APIキーのみ（RSSフィード取得にAPIキーは不要）

```bash
# 環境設定ファイルを作成 | Create environment file
cp .env.template .env
```

`.env`ファイルを編集してAPIキーを設定：

```env
# OpenAI: https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key_here

# 更新間隔（分） | Update interval (minutes)
UPDATE_INTERVAL=180

# 各サイトから取得する記事数 | Number of articles per site
MAX_ARTICLES=3
```

**OpenAI APIキーの取得方法**:
1. https://platform.openai.com/api-keys にアクセス
2. アカウント作成またはログイン
3. "Create new secret key" をクリック
4. 生成されたキーを`.env`ファイルに設定

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

### 主要関数 | Main Functions

- **`init_lcd()`**: LCDディスプレイの初期化（シミュレーションモード対応）
- **`fetch_latest_entries()`**: RSSフィードから最新記事を取得
- **`summarize_with_chatgpt()`**: OpenAI API（gpt-5-mini）で複数記事を統合要約
- **`display_on_lcd()`**: LCDに横スクロール表示
- **`main()`**: メインループ（RSSフィード取得→要約→表示を繰り返し）

### RSSフィードソース | RSS Feed Sources

- **MIT Technology Review AI**: AI関連の最新研究・技術トレンド（英語）
- **AI News**: AI産業応用・製品リリース情報（英語）
- **ITmedia AI+**: 国内AI動向の詳細解説（日本語）

### 設定可能な項目 | Configurable Options

- 更新間隔 (UPDATE_INTERVAL) - デフォルト: 180分（3時間）
- 各サイトから取得する記事数 (MAX_ARTICLES) - デフォルト: 3件
- LCD I²Cアドレス (コード内で変更可能) - デフォルト: 0x27

## 🐛 トラブルシューティング | Troubleshooting

### LCDが動作しない | LCD Not Working

```bash
# I2Cアドレスを確認 | Check I2C address
sudo i2cdetect -y 1

# コード内のアドレス（0x27）を実際のアドレスに変更
# Change address (0x27) in code to actual address
```

**注意**: LCD未接続の場合、自動的にシミュレーションモードで動作します。コンソールに `[LCD表示]` プレフィックス付きで出力されます。

### RSSフィード取得エラー | RSS Feed Errors

- インターネット接続を確認
- RSSフィードURLが変更されていないかチェック
- ログファイル（news_display.log）でエラー詳細を確認

### OpenAI APIエラー | OpenAI API Errors

- APIキーが正しく設定されているか確認（`.env`ファイル）
- OpenAI APIの利用制限をチェック
- gpt-5-miniモデルが利用可能か確認

### ライブラリインストールエラー | Library Installation Errors

```bash
# 必要なライブラリの確認 | Check required libraries
pip list | grep -E "(feedparser|openai|RPLCD|smbus2|python-dotenv)"

# すべて再インストール | Reinstall all
pip install -r requirements.txt --force-reinstall
```

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

- **RSSフィード解析**: feedparserライブラリによるXML解析
- **API統合**: OpenAI API（gpt-5-mini）の使用
- **プロンプトエンジニアリング**: 効果的な要約生成プロンプトの設計
- **ハードウェア制御**: Raspberry Pi、I²C通信、LCD制御
- **エラーハンドリング**: ネットワーク障害対応、シミュレーションモード
- **ログ管理**: ファイル・コンソール両方への適切なログ出力
- **環境変数管理**: 機密情報の安全な管理

## 📄 ライセンス | License

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

## 🤝 コントリビューション | Contributing

プルリクエストやイシューの報告を歓迎します。初心者向けのシンプルな実装を維持することを重視しています。

## 📚 参考リンク | Reference Links

- [feedparser Documentation](https://feedparser.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [RPLCD Library](https://rplcd.readthedocs.io/)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [MIT Technology Review AI](https://www.technologyreview.com/tag/artificial-intelligence/)
- [AI News](https://artificialintelligence-news.com/)
- [ITmedia AI+](https://www.itmedia.co.jp/aiplus/)

---

**作成日**: 2024年
**対象**: プログラミング初心者、Raspberry Pi入門者
**難易度**: 初級〜中級