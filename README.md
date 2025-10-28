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
- **ローディングアニメーション**: API呼び出し中に「生成中...」を表示
- **OLED表示**: SSD1306 OLEDディスプレイに日本語で高速横スクロール表示
- **ニュースループ表示**: 次の更新時間（3時間後）まで同じニュースを連続ループ表示
- **定期更新**: 3時間間隔でニュースを自動更新
- **シミュレーションモード**: OLED未接続でもコンソールで動作確認可能

This application provides:

- **RSS Feed Fetching**: Retrieves latest AI news from multiple sites (no API key required)
- **AI Summarization**: Uses OpenAI API (gpt-5-mini) to summarize multiple articles within 250 characters
- **Loading Animation**: Shows "生成中..." message during API calls
- **OLED Display**: Shows Japanese high-speed scrolling text on SSD1306 OLED display
- **News Loop Display**: Continuously loops news until next update (3 hours later)
- **Auto Update**: Automatically refreshes news every 3 hours
- **Simulation Mode**: Works on console even without OLED connection

## 🛠️ 必要な機器 | Hardware Requirements

| 機器 | 説明 |
|------|------|
| Raspberry Pi 5 | メイン処理ユニット |
| SSD1306 OLEDモジュール | 128×64ピクセル I²C接続ディスプレイ（3.3V動作、日本語表示対応） |
| ジャンパーワイヤ | 配線用（オス-オス、4本） |
| ブレッドボード | プロトタイプ作成用 |
| 日本語フォント | NotoSansCJKjp-Regular.otf（セットアップ時にダウンロード） |

### ⚠️ 重要な注意事項

**✅ 3.3V 動作の OLED モジュールを使用**

- 本プロジェクトでは **3.3V 動作の SSD1306 OLED** を使用します
- Raspberry Pi と直接接続可能で、レベル変換モジュールは不要です
- 配線がシンプルになり、信頼性が向上します
- OLEDモジュール購入時は必ず動作電圧（3.3Vまたは5V）を確認してください

## 🔧 セットアップ | Setup

### 1. ハードウェア接続 | Hardware Connection

**3.3V OLED モジュールの接続**（推奨）:
```
[Raspberry Pi 5]       [SSD1306 OLED (3.3V)]
Pin 1  (3.3V)  ------> VCC
Pin 3  (GPIO2) ------> SDA
Pin 5  (GPIO3) ------> SCL
Pin 6  (GND)   ------> GND
```

**接続手順**:
1. Raspberry Piの電源をOFFにする
2. ブレッドボードにOLEDモジュールを配置
3. ジャンパーワイヤで上記のピンを接続
4. 配線を再確認（特にVCCとGNDの接続ミスに注意）
5. Raspberry Piの電源をONにする

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

- **`init_oled()`**: OLEDディスプレイの初期化（シミュレーションモード対応）
- **`fetch_latest_entries()`**: RSSフィードから最新記事を取得
- **`summarize_with_chatgpt()`**: OpenAI API（gpt-5-mini）で複数記事を統合要約
- **`display_loading_animation()`**: API呼び出し中にローディングアニメーションを表示
- **`display_on_oled()`**: OLEDにピクセル単位の高速横スクロール表示
- **`main()`**: メインループ（ニュース取得・要約→ループ表示→定期更新）

### RSSフィードソース | RSS Feed Sources

- **MIT Technology Review AI**: AI関連の最新研究・技術トレンド（英語）
- **TechCrunch AI**: AI産業応用・製品リリース情報（英語）
- **ITmedia AI+**: 国内AI動向の詳細解説（日本語）

### 設定可能な項目 | Configurable Options

- 更新間隔 (UPDATE_INTERVAL) - デフォルト: 180分（3時間）
- 各サイトから取得する記事数 (MAX_ARTICLES) - デフォルト: 3件
- OLED I²Cアドレス (コード内で変更可能) - デフォルト: 0x3C
- スクロール速度 (SCROLL_SPEED_PX) - デフォルト: 8ピクセル/フレーム
- フレーム遅延 (FRAME_DELAY_SEC) - デフォルト: 0.02秒

## 🐛 トラブルシューティング | Troubleshooting

### OLEDが動作しない | OLED Not Working

```bash
# I2Cアドレスを確認 | Check I2C address
sudo i2cdetect -y 1

# 0x3C が表示されない場合は配線を確認
# If 0x3C is not shown, check wiring
```

**注意**: OLED未接続の場合、自動的にシミュレーションモードで動作します。コンソールに `[OLED表示]` プレフィックス付きで出力されます。

### RSSフィード取得エラー | RSS Feed Errors

- インターネット接続を確認
- RSSフィードURLが変更されていないかチェック
- ログファイル（news_display.log）でエラー詳細を確認
- 特定のサイトがブロックされている場合は、FEEDS辞書から削除または別のフィードに置き換え

### OpenAI APIエラー | OpenAI API Errors

- APIキーが正しく設定されているか確認（`.env`ファイル）
- OpenAI APIの利用制限をチェック
- gpt-5-miniモデルが利用可能か確認

### 要約が0文字になる | Summary is 0 Characters

- `max_completion_tokens`パラメータが不足している可能性があります
- gpt-5-miniは推論モデルのため、推論トークン + 出力トークンの両方を確保する必要があります
- デフォルトでは4000トークンを確保していますが、複雑な要約には不足する場合があります
- ログで推論トークン使用量を確認してください

### スクロールが遅い | Scrolling is Slow

- `SCROLL_SPEED_PX`を増やす（デフォルト: 8）
- `FRAME_DELAY_SEC`を減らす（デフォルト: 0.02）
- ただし、値を小さくしすぎると読みにくくなる可能性があります

### ライブラリインストールエラー | Library Installation Errors

```bash
# 必要なライブラリの確認 | Check required libraries
pip list | grep -E "(feedparser|openai|luma|pillow|python-dotenv)"

# すべて再インストール | Reinstall all
pip install -r requirements.txt --force-reinstall
```

### 日本語フォントが表示されない | Japanese Font Not Displayed

```bash
# フォントファイルの存在確認 | Check font file
ls -l assets/fonts/NotoSansCJKjp-Regular.otf

# フォントが無い場合は再ダウンロード | Re-download if missing
cd assets/fonts/
wget https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf
cd ../..
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
- **API統合**: OpenAI API（gpt-5-mini推論モデル）の使用
- **プロンプトエンジニアリング**: 効果的な要約生成プロンプトの設計
- **ハードウェア制御**: Raspberry Pi、I²C通信、OLED制御
- **グラフィックス処理**: Pillowによる画像生成、日本語フォント描画
- **マルチスレッド処理**: threadingによるローディングアニメーション実装
- **エラーハンドリング**: ネットワーク障害対応、シミュレーションモード
- **ログ管理**: ファイル・コンソール両方への適切なログ出力（トークン使用量追跡）
- **環境変数管理**: 機密情報の安全な管理
- **状態管理**: ニュースループ表示のための時間管理とデータ保存

## 📄 ライセンス | License

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

## 🤝 コントリビューション | Contributing

プルリクエストやイシューの報告を歓迎します。初心者向けのシンプルな実装を維持することを重視しています。

## 📚 参考リンク | Reference Links

- [GPT API呼び出しテンプレート (gpt-5)](https://github.com/Murasan201/09-001-gpt-response-minimal) - gpt-5-mini使用の参考実装
- [feedparser Documentation](https://feedparser.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [luma.oled Library](https://luma-oled.readthedocs.io/)
- [Pillow (PIL) Documentation](https://pillow.readthedocs.io/)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [SSD1306 OLED Datasheet](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf)
- [MIT Technology Review AI](https://www.technologyreview.com/tag/artificial-intelligence/)
- [TechCrunch AI](https://techcrunch.com/category/artificial-intelligence/)
- [ITmedia AI+](https://www.itmedia.co.jp/aiplus/)

---

**作成日**: 2024年
**対象**: プログラミング初心者、Raspberry Pi入門者
**難易度**: 初級〜中級