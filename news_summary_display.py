#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ニュース要約掲示板アプリ
News Summary Display App

RSSフィードから最新ニュースを取得し、AIで要約してOLEDに表示
"""

import os
import sys
import time
import logging
import feedparser
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

# OLED制御用（実際の実行時のみ必要）
try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    from PIL import Image, ImageDraw, ImageFont
    OLED_AVAILABLE = True
except ImportError:
    OLED_AVAILABLE = False
    print("OLEDライブラリが見つかりません。シミュレーションモードで実行します。")
    print("インストール: pip install luma.oled pillow")

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

# OLED設定（コード冒頭の定数で設定）
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_I2C_ADDRESS = 0x3C
OLED_I2C_PORT = 1

# フォント設定
FONT_PATH = "assets/fonts/NotoSansCJKjp-Regular.otf"
FONT_SIZE_TITLE = 12
FONT_SIZE_BODY = 10
LINE_SPACING = 2
SCROLL_SPEED_PX = 2
FRAME_DELAY_SEC = 0.05

# 取得するRSSフィード一覧
FEEDS = {
    "MIT Technology Review AI": "https://www.technologyreview.com/tag/artificial-intelligence/feed/",
    "AI News": "https://artificialintelligence-news.com/feed/",
    "ITmedia AI+": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml"
}

def init_oled():
    """OLEDディスプレイの初期化"""
    if not OLED_AVAILABLE:
        logging.info("OLEDはシミュレーションモードで動作します")
        return None, None, None

    try:
        # I²Cインターフェースの初期化
        serial = i2c(port=OLED_I2C_PORT, address=OLED_I2C_ADDRESS)
        logging.info(f"I²C初期化完了: アドレス 0x{OLED_I2C_ADDRESS:02X}, ポート {OLED_I2C_PORT}")

        # SSD1306デバイスの初期化
        device = ssd1306(serial, width=OLED_WIDTH, height=OLED_HEIGHT)
        device.contrast(255)  # コントラスト最大
        logging.info(f"OLED初期化完了: {OLED_WIDTH}×{OLED_HEIGHT}")

        # 日本語フォントの読み込み
        try:
            font_title = ImageFont.truetype(FONT_PATH, FONT_SIZE_TITLE)
            font_body = ImageFont.truetype(FONT_PATH, FONT_SIZE_BODY)
            logging.info(f"フォント読み込み完了: {FONT_PATH}")
        except IOError as e:
            logging.error(f"フォント読み込みエラー: {e}")
            logging.error(f"対処方法: フォントファイルを {FONT_PATH} に配置してください")
            # フォントが無い場合はデフォルトフォント使用
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()

        # 起動メッセージを表示
        image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
        draw = ImageDraw.Draw(image)
        draw.text((10, 20), "News Display", font=font_title, fill=255)
        draw.text((10, 40), "Starting...", font=font_body, fill=255)
        device.display(image)
        time.sleep(2)

        return device, font_title, font_body

    except Exception as e:
        logging.error(f"OLED初期化エラー: {e}")
        logging.error("対処方法: I²C設定と配線を確認してください")
        logging.error("ヒント: sudo i2cdetect -y 1 でデバイスを確認")
        return None, None, None

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

def display_on_oled(device, font, text: str, y_position: int = 0, scroll: bool = True):
    """
    OLEDにテキストを表示する（スクロールまたは固定表示）

    Args:
        device: OLEDデバイス
        font: 使用するフォント
        text: 表示するテキスト
        y_position: 表示位置（Y座標）
        scroll: True=スクロール表示、False=固定表示
    """
    if device is None:
        # シミュレーションモード
        print(f"[OLED表示] {text}")
        return

    try:
        # テキストの幅を計算
        dummy_image = Image.new("1", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_image)
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        # テキストが画面幅より短い場合は固定表示
        if text_width <= OLED_WIDTH or not scroll:
            image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
            draw = ImageDraw.Draw(image)
            draw.text((2, y_position), text, font=font, fill=255)
            device.display(image)
            time.sleep(3)
            return

        # スクロール表示
        x_position = OLED_WIDTH
        while x_position + text_width > 0:
            image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
            draw = ImageDraw.Draw(image)
            draw.text((x_position, y_position), text, font=font, fill=255)
            device.display(image)
            x_position -= SCROLL_SPEED_PX
            time.sleep(FRAME_DELAY_SEC)

        time.sleep(0.5)

    except Exception as e:
        logging.error(f"OLED表示エラー: {e}")


def display_multiline_on_oled(device, font, lines: List[str]):
    """
    OLEDに複数行のテキストを表示する

    Args:
        device: OLEDデバイス
        font: 使用するフォント
        lines: 表示するテキストのリスト
    """
    if device is None:
        # シミュレーションモード
        for line in lines:
            print(f"[OLED表示] {line}")
        return

    try:
        image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
        draw = ImageDraw.Draw(image)

        y_pos = 2
        for line in lines:
            if y_pos + FONT_SIZE_BODY > OLED_HEIGHT:
                break
            draw.text((2, y_pos), line, font=font, fill=255)
            y_pos += FONT_SIZE_BODY + LINE_SPACING

        device.display(image)
        time.sleep(5)

    except Exception as e:
        logging.error(f"OLED複数行表示エラー: {e}")

def main():
    """メイン関数"""
    # OLEDを初期化
    device, font_title, font_body = init_oled()

    logging.info(f"ニュース要約掲示板アプリを開始します（更新間隔: {UPDATE_INTERVAL}分 = {UPDATE_INTERVAL//60}時間）")

    try:
        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            # ヘッダーを表示
            display_on_oled(device, font_title, f"AIニュース要約 {now}", y_position=25, scroll=True)
            time.sleep(1)

            # 各RSSフィードからニュースを取得・要約
            for site_name, feed_url in FEEDS.items():
                logging.info(f"{site_name} から記事を取得中...")
                entries = fetch_latest_entries(feed_url, MAX_ARTICLES)

                if not entries:
                    display_on_oled(device, font_body, f"{site_name}: 取得失敗", y_position=25, scroll=True)
                    time.sleep(2)
                    continue

                # サイト名を表示
                display_on_oled(device, font_title, f"[{site_name}]", y_position=25, scroll=True)
                time.sleep(1)

                # 要約を生成して表示
                summary = summarize_with_chatgpt(site_name, entries)

                # 要約を複数行に分割して表示
                summary_lines = summary.split('\n')
                for line in summary_lines:
                    if line.strip():  # 空行をスキップ
                        display_on_oled(device, font_body, line.strip(), y_position=25, scroll=True)
                        time.sleep(1)

                time.sleep(2)

            # 次の更新まで待機
            wait_seconds = UPDATE_INTERVAL * 60
            logging.info(f"{UPDATE_INTERVAL//60}時間後に次の更新を行います...")

            # 待機メッセージを表示
            display_on_oled(device, font_body, f"次回更新: {UPDATE_INTERVAL//60}時間後", y_position=25, scroll=False)
            time.sleep(wait_seconds)

    except KeyboardInterrupt:
        logging.info("アプリケーションを終了します")
        if device:
            image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
            draw = ImageDraw.Draw(image)
            draw.text((30, 25), "Goodbye!", font=font_title, fill=255)
            device.display(image)
            time.sleep(2)
            device.clear()
    except Exception as e:
        logging.error(f"予期しないエラー: {e}")
    finally:
        if device:
            device.clear()

if __name__ == "__main__":
    main()
