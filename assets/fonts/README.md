# フォントファイルの配置方法

このディレクトリには、日本語表示用のフォントファイルを配置します。

## 推奨フォント

### Noto Sans CJK JP（推奨）

**ライセンス**: SIL Open Font License (OFL-1.1)（商用利用可）

**ダウンロード方法**:

1. **Google Fonts 経由**（最も簡単）:
   ```bash
   cd assets/fonts/
   wget https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf
   ```

2. **GitHub リポジトリから直接**:
   - リポジトリ: https://github.com/googlefonts/noto-cjk
   - `Sans/OTF/Japanese/` ディレクトリから必要なウェイトをダウンロード
   - `NotoSansCJKjp-Regular.otf` を推奨

**ライセンスファイル**:
```bash
cd assets/fonts/
wget https://raw.githubusercontent.com/googlefonts/noto-cjk/main/LICENSE
```

---

### M PLUS 1p（代替フォント）

**ライセンス**: SIL Open Font License (OFL-1.1)

**ダウンロード方法**:
1. Google Fonts: https://fonts.google.com/specimen/M+PLUS+1p
2. GitHub: https://github.com/coz-m/MPLUS_FONTS

---

## ファイル配置後の確認

以下のコマンドで配置されているフォントファイルを確認：

```bash
ls -lh assets/fonts/
```

期待される出力例：
```
-rw-r--r-- 1 pi pi  16M Jan 15 12:00 NotoSansCJKjp-Regular.otf
-rw-r--r-- 1 pi pi 4.4K Jan 15 12:00 LICENSE
```

---

## トラブルシューティング

### フォントが見つからないエラー

```
[フォント読み込み]エラー: cannot open resource
```

**対処方法**:
1. フォントファイルのパスを確認
   ```bash
   ls -l assets/fonts/NotoSansCJKjp-Regular.otf
   ```

2. スクリプトからの相対パスが正しいか確認
   - プロジェクトルートから実行する場合: `assets/fonts/NotoSansCJKjp-Regular.otf`

3. ファイルの権限を確認
   ```bash
   chmod 644 assets/fonts/NotoSansCJKjp-Regular.otf
   ```

---

## 注意事項

- **容量**: Noto Sans CJK JP は約15-17MBと大きいですが、日本語の全文字をカバーするために必要です
- **ライセンス**: OFLライセンスのため、商用利用・改変・再配布が可能です
- **ライセンス文書の同梱**: フォントを使用する際は、LICENSE ファイルも必ず同梱してください
