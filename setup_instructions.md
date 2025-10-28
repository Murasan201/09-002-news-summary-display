# ニュース要約掲示板アプリ - セットアップ手順

## 1. 必要なハードウェア
- Raspberry Pi 5本体
- microSDカード（Raspberry Pi OSインストール済み）
- SSD1306 OLEDディスプレイモジュール（I²C接続、128×64ピクセル）
  - 3.3V動作版を推奨（5V版の場合はレベル変換モジュールが必要）
- BSS138双方向ロジックレベル変換モジュール（5V版OLEDを使用する場合のみ）
- ジャンパーワイヤ（オス-オス、4～10本程度）
- ブレッドボード（汎用サイズ）
- 電源（公式5V/3A電源アダプタ推奨）

## 2. ハードウェア接続

### 2.1 3.3V版OLEDを使用する場合（推奨）

**Raspberry Pi 5 ⇔ SSD1306 OLED (3.3V版)**

| Raspberry Pi 5 | SSD1306 OLED |
|----------------|--------------|
| 3.3V (Pin 1)   | VCC          |
| GND (Pin 6)    | GND          |
| SDA (Pin 3)    | SDA          |
| SCL (Pin 5)    | SCL          |

### 2.2 5V版OLEDを使用する場合

⚠️ **重要**: Raspberry Pi（3.3V）と5V版OLED間に必ずレベル変換モジュールを使用してください。直接接続するとRaspberry Pi GPIOピンが破損する可能性があります。

**Raspberry Pi 5 (3.3V側) ⇔ レベル変換モジュール ⇔ SSD1306 OLED (5V版)**

| Raspberry Pi 5 | レベル変換（LV側）| レベル変換（HV側）| SSD1306 OLED |
|----------------|------------------|------------------|--------------|
| 3.3V (Pin 1)   | LV               | -                | -            |
| 5V (Pin 2)     | -                | HV               | VCC          |
| GND (Pin 6)    | GND              | GND              | GND          |
| SDA (Pin 3)    | LV1              | HV1              | SDA          |
| SCL (Pin 5)    | LV2              | HV2              | SCL          |

### 2.3 配線手順

**3.3V版OLEDの場合:**
1. 電源を切った状態で配線を行う
2. OLEDモジュールをブレッドボードに設置
3. Raspberry PiとOLEDを直接接続（3.3V、GND、SDA、SCL）
4. 配線を確認後、電源を投入

**5V版OLEDの場合:**
1. 電源を切った状態で配線を行う
2. レベル変換モジュールをブレッドボードに設置
3. Raspberry Piとレベル変換モジュールのLV側を接続（3.3V、GND、SDA、SCL）
4. レベル変換モジュールのHV側とOLEDを接続（5V、GND、SDA、SCL）
5. 配線を確認後、電源を投入

## 3. ソフトウェアセットアップ

### 3.1 I2Cを有効化
```bash
sudo raspi-config
# Interface Options → I2C → Yes
```

### 3.2 必要なシステムパッケージをインストール
```bash
sudo apt update
sudo apt install python3-pip python3-venv i2c-tools
```

### 3.3 I2C接続を確認
```bash
sudo i2cdetect -y 1
# OLED のアドレス（通常 0x3c）が表示されることを確認
```

### 3.4 Python仮想環境を作成
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.5 必要なライブラリをインストール

このプロジェクトでは、RSS解析、AI API利用、OLED制御、画像処理、環境変数管理に関連するPythonライブラリを使用します。

#### RSSフィード解析ライブラリのインストール
```bash
pip3 install feedparser
```

#### OpenAI APIクライアントライブラリのインストール
```bash
pip3 install openai
```

#### OLED制御ライブラリのインストール
```bash
pip3 install luma.oled
```

#### 画像処理・フォント描画ライブラリのインストール
```bash
pip3 install pillow
```

#### 環境変数管理ライブラリのインストール
```bash
pip3 install python-dotenv
```

#### または一括インストール
```bash
pip install -r requirements.txt
```

#### インストール確認
```bash
pip list | grep -E "(feedparser|openai|luma|pillow|python-dotenv)"
```

各ライブラリが表示されれば、インストールが正常に完了しています。

## 4. フォントファイルの配置

OLEDに日本語を表示するため、日本語フォントファイルを配置します。

### 4.1 フォントディレクトリの作成

```bash
mkdir -p assets/fonts
```

### 4.2 フォントファイルの配置

以下のいずれかの方法でフォントファイルを配置します：

**方法1: Noto Sans CJK JPをダウンロード（推奨）**
```bash
cd assets/fonts
wget https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf
cd ../..
```

**方法2: システムフォントを使用**
```bash
# システムにインストールされているフォントを使用する場合
# コード内のFONT_PATHを適宜変更してください
# 例: /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
```

フォントファイルが `assets/fonts/NotoSansCJKjp-Regular.otf` に配置されていることを確認してください。

## 5. 環境変数の設定

APIキーなどの機密情報を安全に管理するため、環境変数設定ファイルを作成します。

### 5.1 テンプレートファイルの作成

```bash
nano .env.template
```

テンプレートファイルに以下の内容を記載します：

```env
# ニュース要約掲示板アプリ - APIキー設定
# News Summary Display App - API Keys Configuration

# OpenAI のAPIキー（https://platform.openai.com/ で取得）
# OpenAI API Key (Get from https://platform.openai.com/)
OPENAI_API_KEY=your_openai_api_key_here

# ニュース更新間隔（分）
# News update interval (minutes)
UPDATE_INTERVAL=180

# 各サイトから取得する記事数
# Number of articles to fetch per site
MAX_ARTICLES=3
```

このテンプレートファイルは、実際の設定ファイルを作成する際の雛形となります。

### 5.2 実際の設定ファイルを作成

```bash
cp .env.template .env
```

### 5.3 OpenAI APIキーの取得

OpenAI APIは、高性能な自然言語処理機能を提供するサービスで、ニュース記事の要約生成に最適です。gpt-5-miniモデルを使用することで、日本語の文章も正確に理解し、適切な要約文を生成できます。

APIキーを取得するには、OpenAI Platformの公式サイト（https://platform.openai.com/api-keys）にアクセスします。Googleアカウントやメールアドレスでアカウントを作成し、必要に応じて電話番号認証を完了します。ログイン後、「Create new secret key」ボタンから新しいAPI keyを生成できます。

OpenAI APIは使用量に応じた従量課金制ですが、新規アカウントには無料クレジットが付与されます。gpt-5-miniモデルは低コストで動作するため、学習目的での利用には十分対応できます。

### 5.4 環境変数ファイルの編集

`.env`ファイルに、取得したOpenAI APIキーを設定します：

```bash
nano .env
```

以下のように実際のAPIキーを設定：

```env
OPENAI_API_KEY=実際のOpenAIAPIキー
UPDATE_INTERVAL=180
MAX_ARTICLES=3
```

**UPDATE_INTERVAL**は更新間隔を分単位で指定します。180分（3時間）に設定することで、OpenAI APIの利用料金を抑えながら定期的に最新ニュースを取得できます。**MAX_ARTICLES**は各ニュースサイトから取得する記事数を指定します。

**重要**: `.env`ファイルは`.gitignore`により自動的にGit管理から除外されます。APIキーが誤ってGitHubにアップロードされることはありません。

## 6. プログラムの実行とテスト

作成したアプリケーションを実際に実行し、動作確認を行います。

### 6.1 実行前の確認事項

#### ハードウェア接続の確認
OLEDがRaspberry Piに正しく接続されているか、I²Cが有効化されているかをチェックします。

```bash
sudo i2cdetect -y 1
```

このコマンドで「3c」のアドレスが表示されることを確認します。

#### フォントファイルの確認
日本語フォントファイルが正しく配置されているかを確認します。

```bash
ls -l assets/fonts/NotoSansCJKjp-Regular.otf
```

フォントファイルが存在することを確認します。

#### 環境変数の確認
`.env`ファイルに正しいAPIキーが設定されているかをチェックします。

```bash
cat .env
```

APIキーが「your_openai_api_key_here」のままになっていないことを確認します。

#### ライブラリインストールの確認
必要なPythonライブラリが正しくインストールされているかをチェックします。

```bash
pip list | grep -E "(feedparser|openai|luma|pillow|python-dotenv)"
```

すべてのライブラリが表示されることを確認します。

### 6.2 テスト実行
```bash
python3 news_summary_display.py
```

正常に実行された場合、以下のような出力が表示されます：

```
2024-01-15 08:00:01 - INFO - I²C初期化完了: アドレス 0x3C, ポート 1
2024-01-15 08:00:01 - INFO - OLED初期化完了: 128×64
2024-01-15 08:00:01 - INFO - フォント読み込み完了: assets/fonts/NotoSansCJKjp-Regular.otf
2024-01-15 08:00:01 - INFO - ニュース要約掲示板アプリを開始します（更新間隔: 180分 = 3時間）
2024-01-15 08:00:02 - INFO - MIT Technology Review AI から記事を取得中...
2024-01-15 08:00:03 - INFO - 3件の記事を取得しました
2024-01-15 08:00:05 - INFO - MIT Technology Review AIの要約を生成しました
```

OLEDが接続されている場合は、実際のディスプレイにニュース要約が横スクロール表示されます。

OLEDライブラリが見つからない場合は、シミュレーションモードで動作します：

```
OLEDライブラリが見つかりません。シミュレーションモードで実行します。
インストール: pip install luma.oled pillow
2024-01-15 08:00:01 - INFO - OLEDはシミュレーションモードで動作します
[OLED表示] AIニュース要約 2024-01-15 08:00
[OLED表示] [MIT Technology Review AI]
[OLED表示] 最新のAI研究では、大規模言語モデルの効率化と新しい機械学習手法が注目されています。
```

### 6.3 動作確認のポイント

1. **RSSフィード取得**: ログに「○件の記事を取得しました」と表示されることを確認
2. **AI要約生成**: ログに「○○の要約を生成しました」と表示されることを確認
3. **OLED表示**: シミュレーションモードの場合はコンソールに、実機の場合はOLEDに表示されることを確認

### 6.4 バックグラウンド実行
```bash
nohup python3 news_summary_display.py &
```

### 6.5 自動起動設定（オプション）
```bash
# systemdサービスファイルを作成
sudo nano /etc/systemd/system/news-display.service
```

サービスファイルの内容：
```ini
[Unit]
Description=News Summary Display App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/news-summary-display
ExecStart=/home/pi/news-summary-display/venv/bin/python news_summary_display.py
Restart=always

[Install]
WantedBy=multi-user.target
```

サービスを有効化：
```bash
sudo systemctl daemon-reload
sudo systemctl enable news-display.service
sudo systemctl start news-display.service
```

## 7. トラブルシューティング

### OLED が動作しない場合
- I²C接続を確認
- `sudo i2cdetect -y 1` でアドレスを確認（通常0x3c）
- コード内のI²Cアドレス（0x3c）を実際のアドレスに変更
- 配線を確認（3.3V版と5V版で配線が異なります）
- レベル変換モジュールの動作確認（5V版OLEDの場合）

**注意**: OLED未接続の場合、自動的にシミュレーションモードで動作します。コンソールに `[OLED表示]` プレフィックス付きで出力されます。

### フォントが表示されない場合
- フォントファイルが正しく配置されているか確認
  ```bash
  ls -l assets/fonts/NotoSansCJKjp-Regular.otf
  ```
- フォントファイルのパスがコード内の設定と一致しているか確認
- デフォルトフォントで代替表示されている場合は、フォントファイルを配置してください

### RSSフィード取得エラーが発生する場合
- インターネット接続を確認
- RSSフィードURLが変更されていないかチェック
- ログファイル（news_display.log）でエラー詳細を確認

### OpenAI API エラーが発生する場合
- APIキーが正しく設定されているか確認（`.env`ファイル）
- OpenAI APIの利用制限をチェック
- gpt-5-miniモデルが利用可能か確認

### ライブラリインストールエラーが発生する場合
```bash
# 必要なライブラリの確認
pip list | grep -E "(feedparser|openai|luma|pillow|python-dotenv)"

# すべて再インストール
pip install -r requirements.txt --force-reinstall
```

### 権限エラーが発生する場合
- GPIO/I²C権限があるか確認
- `sudo usermod -a -G i2c,spi,gpio pi` でユーザーをグループに追加