# ツムツム自動プレイツール

これはSakulabハッカソン2023の作品です。

## 作品情報
### 「ツムツム」ってどんなゲーム？
1分の制限時間内に同じキャラクターの「ツム（ぬいぐるみ）」を3つ以上なぞって消していくパズルゲームです。

一度になぞったツムの数が多いほど、稼げるコインやスコアが高くなります。

誰でも簡単に楽しめて爽快感が味わえます。

### ツールの説明
今回作成したのは、ツムツム自動プレイツールです。

- スコアが伸びない
- プレイする時間がないけど、レベルアップ・コイン稼ぎをしたい
- レベルが高い状態になってからプレイしたい

これらの悩みをこの自動ツールで解決できます。

このツールでは、ツムツムのプレイ画面を画像認識し、最もなぞれる数が多いツムを経路探索し、自動でなぞります。

## 使用方法
①[Nox Player](https://jp.bignox.com/)をダウンロード

②[ツムツム](https://jp.bignox.com/appcenter/linecorp-lgtmtm-tumutumupcplay.html)をインストール

③ツムツムのスタートボタンを押す。

④下のプログラムを実行
```bash
tumu_auto.py
```
## バージョン
### Pythonのバージョン
Python 3.10.9

### インストール
- win32gui

- pyautogui

- graphillion

- OpenCV

- Nox Player 7.0.5.8

## 参考文献
- 画像から円を検出し、色でグループ化して最長経路を繋げてみる.2023-6-16

  https://marimox.net/circle(2023-10-21)

- Pythonで選択したウィンドウのスクリーンショットを撮るには？.2022-01-11

  https://xn--eckl3qmbc2cv902cnwa746d81h183l.com/instructor-blog/220111how-to-take-a-screenshot-of-the-selected-window-in-python/(2023-10-21)

## 作成者
鈴木秀佳

明治大学 櫻井研究室