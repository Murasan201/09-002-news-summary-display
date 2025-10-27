#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ニュース要約掲示板アプリ
News Summary Display App

RSSフィードから最新ニュースを取得し、AIで要約してLCDに表示
"""

import os
import time
import logging
import feedparser
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

# LCD制御用（実際の実行時のみ必要）
try:
    from RPLCD.i2c import CharLCD
    LCD_AVAILABLE = True
except ImportError:
    LCD_AVAILABLE = False
    print("LCDライブラリが見つかりません。シミュレーションモードで実行します。")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_display.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 環境変数を読み込み
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("環境変数 OPENAI_API_KEY を設定してください。")

# OpenAI クライアントの初期化
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 設定値の取得
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 180))
MAX_ARTICLES = int(os.getenv('MAX_ARTICLES', 3))

# 取得するRSSフィード一覧
FEEDS = {
    "MIT Technology Review AI": "https://www.technologyreview.com/tag/artificial-intelligence/feed/",
    "AI News": "https://artificialintelligence-news.com/feed/",
    "ITmedia AI+": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml"
}

def init_lcd():
    """LCDの初期化"""
    if not LCD_AVAILABLE:
        logging.info("LCDはシミュレーションモードで動作します")
        return None

    try:
        lcd = CharLCD(
            i2c_expander='PCF8574',
            address=0x27,
            port=1,
            cols=16,
            rows=2
        )
        lcd.clear()
        lcd.write_string("News Display")
        lcd.crlf()
        lcd.write_string("Starting...")
        time.sleep(2)
        logging.info("LCDを初期化しました")
        return lcd
    except Exception as e:
        logging.error(f"LCD初期化エラー: {e}")
        return None

def fetch_latest_entries(feed_url: str, max_items: int = 3) -> List[str]:
    """
    RSSフィードを解析し、最新記事を取得して
    タイトルと要約のリストを返す
    """
    try:
        feed = feedparser.parse(feed_url)
        entries = []

        for entry in feed.entries[:max_items]:
            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()
            link = entry.get("link", "").strip()
            entries.append(f"- {title}: {summary}")

        logging.info(f"{len(entries)}件の記事を取得しました")
        return entries

    except Exception as e:
        logging.error(f"RSSフィード取得エラー: {e}")
        return []

def summarize_with_chatgpt(site_name: str, items: List[str]) -> str:
    """
    ChatGPTに渡して、箇条書きの要約を生成
    """
    try:
        prompt = (
            f"以下は「{site_name}」の最新AIニュース記事の見出しと概要です。\n"
            "これらを技術トレンドや注目ポイントがひと目でわかるよう、"
            "日本語で250文字以内の箇条書き要約にしてください。\n\n"
            + "\n".join(items)
        )

        response = openai_client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "あなたは有能な技術ニュース要約アシスタントです。"},
                {"role": "user", "content": prompt}
            ]
        )

        text = response.choices[0].message.content.strip()
        logging.info(f"{site_name}の要約を生成しました")
        return text

    except Exception as e:
        logging.error(f"要約生成エラー: {e}")
        return f"{site_name}の要約生成に失敗しました"

def display_on_lcd(lcd, text: str, scroll_delay: float = 0.3):
    """LCDにテキストをスクロール表示する"""
    if lcd is None:
        # シミュレーションモード
        print(f"[LCD表示] {text}")
        return

    try:
        lcd.clear()

        # テキストが16文字以下の場合はそのまま表示
        if len(text) <= 16:
            lcd.write_string(text)
            time.sleep(3)
            return

        # スクロール表示
        text_padded = text + "    "  # スクロール用の余白

        for i in range(len(text_padded) - 15):
            lcd.home()
            display_text = text_padded[i:i+16]
            lcd.write_string(display_text)
            time.sleep(scroll_delay)

        time.sleep(1)

    except Exception as e:
        logging.error(f"LCD表示エラー: {e}")

def main():
    """メイン関数"""
    # LCDを初期化
    lcd = init_lcd()

    logging.info(f"ニュース要約掲示板アプリを開始します（更新間隔: {UPDATE_INTERVAL}分 = {UPDATE_INTERVAL//60}時間）")

    try:
        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            message_blocks = [f"AIニュース要約 ({now})"]

            # 各RSSフィードからニュースを取得・要約
            for site_name, feed_url in FEEDS.items():
                logging.info(f"{site_name} から記事を取得中...")
                entries = fetch_latest_entries(feed_url, MAX_ARTICLES)

                if not entries:
                    message_blocks.append(f"> {site_name} のニュース取得失敗")
                    continue

                summary = summarize_with_chatgpt(site_name, entries)
                message_blocks.append(f"[{site_name}]")
                message_blocks.append(summary)
                message_blocks.append("")

            # 生成したすべての要約を表示
            for block in message_blocks:
                if block:  # 空行をスキップ
                    display_on_lcd(lcd, block)
                    time.sleep(2)

            # 次の更新まで待機
            wait_seconds = UPDATE_INTERVAL * 60
            logging.info(f"{UPDATE_INTERVAL//60}時間後に次の更新を行います...")
            time.sleep(wait_seconds)

    except KeyboardInterrupt:
        logging.info("アプリケーションを終了します")
        if lcd:
            lcd.clear()
            lcd.write_string("Goodbye!")
    except Exception as e:
        logging.error(f"予期しないエラー: {e}")
    finally:
        if lcd:
            lcd.clear()

if __name__ == "__main__":
    main()
