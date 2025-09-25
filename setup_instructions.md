# ニュース要約掲示板アプリ - セットアップ手順

## 1. 必要なハードウェア
- Raspberry Pi 5
- LCD1602ディスプレイモジュール（I²C接続）
- ジャンパーワイヤ
- ブレッドボード

## 2. ハードウェア接続
LCD1602とRaspberry Piの接続：
- VCC → 5V (Pin 2)
- GND → GND (Pin 6)
- SDA → SDA (Pin 3, GPIO 2)
- SCL → SCL (Pin 5, GPIO 3)

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
# LCD のアドレス（通常 0x27 または 0x3f）が表示されることを確認
```

### 3.4 Python仮想環境を作成
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.5 必要なライブラリをインストール
```bash
pip install -r requirements.txt
```

## 4. APIキーの設定

### 4.1 .envファイルを作成
```bash
cp .env.template .env
```

### 4.2 APIキーを取得・設定
1. NewsAPI: https://newsapi.org/ でアカウント作成、APIキー取得
2. OpenAI: https://platform.openai.com/ でアカウント作成、APIキー取得
3. `.env`ファイルを編集してAPIキーを設定

```env
NEWS_API_KEY=your_actual_newsapi_key
OPENAI_API_KEY=your_actual_openai_api_key
```

## 5. 実行

### 5.1 テスト実行
```bash
python3 news_summary_display.py
```

### 5.2 バックグラウンド実行
```bash
nohup python3 news_summary_display.py &
```

### 5.3 自動起動設定（オプション）
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

## 6. トラブルシューティング

### LCD が動作しない場合
- I2C接続を確認
- `sudo i2cdetect -y 1` でアドレスを確認
- コード内のI2Cアドレス（0x27）を実際のアドレスに変更

### API エラーが発生する場合
- APIキーが正しく設定されているか確認
- インターネット接続を確認
- API利用制限に達していないか確認

### 権限エラーが発生する場合
- GPIO/I2C権限があるか確認
- `sudo usermod -a -G i2c,spi,gpio pi` でユーザーをグループに追加