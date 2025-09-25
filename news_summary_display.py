#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ニュース要約掲示板アプリ
News Summary Display App

プログラミング初心者向けのシンプルな実装
Simple implementation for programming beginners
"""

import os
import time
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional

# 環境変数読み込み用
from dotenv import load_dotenv

# OpenAI API用
from openai import OpenAI

# LCD制御用（実際の実行時のみ必要）
try:
    from RPLCD.i2c import CharLCD
    LCD_AVAILABLE = True
except ImportError:
    LCD_AVAILABLE = False
    print("LCD ライブラリが見つかりません。シミュレーションモードで実行します。")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_display.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class NewsDisplayApp:
    """ニュース要約表示アプリのメインクラス"""

    def __init__(self):
        """初期化処理"""
        # 環境変数を読み込み
        load_dotenv()

        # APIキーの取得
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        # 設定値の取得
        self.update_interval = int(os.getenv('UPDATE_INTERVAL', 30))
        self.news_count = int(os.getenv('NEWS_COUNT', 5))

        # APIキーの確認
        if not self.news_api_key or not self.openai_api_key:
            raise ValueError("APIキーが設定されていません。.envファイルを確認してください。")

        # OpenAI クライアントの初期化
        self.openai_client = OpenAI(api_key=self.openai_api_key)

        # LCD の初期化（利用可能な場合）
        self.lcd = self._init_lcd()

        logging.info("ニュース要約掲示板アプリを初期化しました")

    def _init_lcd(self) -> Optional[CharLCD]:
        """LCD の初期化"""
        if not LCD_AVAILABLE:
            logging.info("LCD はシミュレーションモードで動作します")
            return None

        try:
            # LCD1602 の初期化（I2Cアドレスは環境により異なる場合があります）
            lcd = CharLCD(
                i2c_expander='PCF8574',
                address=0x27,  # 一般的なI2Cアドレス
                port=1,
                cols=16,
                rows=2
            )
            lcd.clear()
            lcd.write_string("News Display")
            lcd.crlf()
            lcd.write_string("Starting...")
            time.sleep(2)
            logging.info("LCD を初期化しました")
            return lcd
        except Exception as e:
            logging.error(f"LCD 初期化エラー: {e}")
            return None

    def get_latest_news(self) -> List[Dict]:
        """最新ニュースを取得する"""
        try:
            # NewsAPI のエンドポイント
            url = "https://newsapi.org/v2/top-headlines"

            # リクエストパラメータ
            params = {
                'apiKey': self.news_api_key,
                'country': 'jp',  # 日本のニュース
                'pageSize': self.news_count,
                'category': 'general'
            }

            # APIリクエスト実行
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data['status'] != 'ok':
                raise Exception(f"NewsAPI エラー: {data.get('message', 'Unknown error')}")

            articles = data.get('articles', [])
            logging.info(f"{len(articles)}件のニュースを取得しました")

            return articles

        except requests.exceptions.RequestException as e:
            logging.error(f"ニュース取得エラー: {e}")
            return []
        except Exception as e:
            logging.error(f"予期しないエラー: {e}")
            return []

    def summarize_text(self, title: str, description: str) -> str:
        """OpenAI API を使ってテキストを要約する"""
        try:
            # 要約するテキストを準備
            text_to_summarize = f"タイトル: {title}\n内容: {description}"

            # OpenAI API に要約を依頼
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはニュースを簡潔に要約する専門家です。100文字以内でわかりやすく要約してください。"
                    },
                    {
                        "role": "user",
                        "content": text_to_summarize
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )

            summary = response.choices[0].message.content.strip()
            logging.info(f"要約を生成しました: {summary[:50]}...")

            return summary

        except Exception as e:
            logging.error(f"要約生成エラー: {e}")
            # エラー時は元のタイトルを返す
            return title

    def display_on_lcd(self, text: str, scroll_delay: float = 0.3):
        """LCD にテキストをスクロール表示する"""
        if self.lcd is None:
            # シミュレーションモード: コンソールに出力
            print(f"[LCD表示] {text}")
            return

        try:
            self.lcd.clear()

            # テキストが16文字以下の場合はそのまま表示
            if len(text) <= 16:
                self.lcd.write_string(text)
                time.sleep(3)
                return

            # スクロール表示
            text_padded = text + "    "  # スクロール用の余白

            for i in range(len(text_padded) - 15):
                self.lcd.home()
                display_text = text_padded[i:i+16]
                self.lcd.write_string(display_text)
                time.sleep(scroll_delay)

            # 少し停止
            time.sleep(1)

        except Exception as e:
            logging.error(f"LCD 表示エラー: {e}")

    def format_news_for_display(self, articles: List[Dict]) -> List[str]:
        """ニュース記事を表示用に整形する"""
        formatted_news = []

        for i, article in enumerate(articles, 1):
            title = article.get('title', '不明なタイトル')
            description = article.get('description', '')

            # 要約を生成
            summary = self.summarize_text(title, description)

            # 表示用のテキストを作成
            display_text = f"[{i}] {title} | 要約: {summary}"
            formatted_news.append(display_text)

            logging.info(f"記事{i}を整形しました")

        return formatted_news

    def run_display_cycle(self):
        """1回の表示サイクルを実行する"""
        try:
            logging.info("ニュース取得を開始します...")

            # 最新ニュースを取得
            articles = self.get_latest_news()

            if not articles:
                error_msg = "ニュースを取得できませんでした"
                logging.warning(error_msg)
                self.display_on_lcd(error_msg)
                return

            # 表示用に整形
            formatted_news = self.format_news_for_display(articles)

            # 各ニュースをLCDに表示
            for news_text in formatted_news:
                self.display_on_lcd(news_text)
                time.sleep(2)  # 次のニュースまで少し待機

            logging.info("表示サイクルを完了しました")

        except Exception as e:
            logging.error(f"表示サイクル実行エラー: {e}")
            self.display_on_lcd("エラーが発生しました")

    def run(self):
        """メインループを実行する"""
        logging.info(f"ニュース要約掲示板アプリを開始します（更新間隔: {self.update_interval}分）")

        try:
            while True:
                # 表示サイクルを実行
                self.run_display_cycle()

                # 次の更新まで待機
                wait_seconds = self.update_interval * 60
                logging.info(f"{self.update_interval}分後に次の更新を行います...")
                time.sleep(wait_seconds)

        except KeyboardInterrupt:
            logging.info("アプリケーションを終了します")
            if self.lcd:
                self.lcd.clear()
                self.lcd.write_string("Goodbye!")
        except Exception as e:
            logging.error(f"予期しないエラー: {e}")
        finally:
            if self.lcd:
                self.lcd.clear()

def main():
    """メイン関数"""
    try:
        # アプリケーションを作成・実行
        app = NewsDisplayApp()
        app.run()

    except Exception as e:
        logging.error(f"アプリケーション起動エラー: {e}")
        print(f"エラーが発生しました: {e}")
        print("設定を確認してください：")
        print("1. .env ファイルにAPIキーが正しく設定されているか")
        print("2. requirements.txt のライブラリがインストールされているか")

if __name__ == "__main__":
    main()