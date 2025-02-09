# <img src="assets/ZundaGPT2.ico" width="48"> ZundaGPT2 Lite

Copyright (c) 2024-2025 led-mirage

[English](Readme.en.md)

## 概要

ZundaGPT2(https://github.com/led-mirage/ZundaGPT2) のライト版なのだ。ZundaGPT2から音声読み上げ機能を省いたバージョンなのだよ。

簡単に言うと、AIとチャットできるチャットクライアントソフトウェアなのだ。

使用できるAIサービスは以下の4つなのだよ。

- OpenAI
- AzureOpenAI
- Google Gemini
- Anthropic Claude

## 最新情報

### バージョン 1.10.0

- ファイル横断検索機能を実装したのだ✨
- ボタンデザインを変更したのだ✨
- フィンランド語とスペイン語に対応したのだ✨

### バージョン 1.9.0

- メッセージをコピーするボタンとコンテキストメニューを追加したのだ✨

### バージョン 1.8.0

- コードブロックにコピーボタンをつけて、簡単にクリップボードにコピーできるようにしたのだ✨

## スクリーンショット

<img src="assets/ZundaGPT2_splash.png" width="200">

<img src="doc/screenshot_1.10.0.png" width="600">

## 動作確認環境

- Windows 11 Pro 23H2、24H2
- Python 3.12.0

## 言語サポート

使用する言語を変更するには`appConfig.json`ファイルの`language`設定を変更すればいいのだ。

```json
"language": "en"
```

設定できる値は以下の通りなのだ。

| 設定値 | 言語 | キャラクター設定ファイル | 実装バージョン |
|-|-|-|-|
| ja | 日本語 | settings.json | 1.6.0 |
| en | 英語 | settings.en.json | 1.6.0 |
| fi | フィンランド語 | settings.fi.json | 1.10.0 |
| es | スペイン語 | settings.es.json | 1.10.0 |

## 必要なもの

このアプリ自体は無料だけど、このアプリを動作させるには以下のいずれかのAPIキーが必要になるのだ。

ここでは軽く触れておくだけにするけど、詳しいことは[こっち](Readme_detail.md)を見てほしいのだ。

### ✅ OpenAIアカウントとAPIキー

OpenAIのAPIを使用する場合は、[OpenAI](https://platform.openai.com/)のアカウントとAPIの利用登録（課金およびAPIキーの作成）が必要なのだ。

### ✅ Google Gemini APIのAPIキー

バージョン0.7.0からGoogle Gemini APIにも対応したのだ。

2024年5月19日時点でGoogle Gemini APIには無料プランが設定されているので、OpenAIのAPIよりも気軽に利用することができるのだ。Google Gemini APIを使用したい場合は、[専用の資料](Readme_gemini.md)を用意したので、それを参照して欲しいのだ。

### ✅ Anthropic APIのAPIキー

バージョン1.4.0からAnthropic API（Claudeシリーズ）にも対応したのだ。

APIを利用するには[Anthropic Console](https://console.anthropic.com/)のアカウントとAPIの利用登録（課金およびAPIキーの作成）が必要なのだ。

2024年12月29日時点の最新のモデルは`Claude 3.5 Sonnet`なのだ。

## 実行方法

### 🛩️ 準備：OSの環境変数を追加

OpenAIのAPIキー、またはGoogle Gemini API、またはAnthropic APIのAPIキーをOSの環境変数に登録しておく必要があるのだ。

| AI | 変数名 | 値 |
|------|------|------|
| OpenAI | OPENAI_API_KEY  | OpenAIで取得したAPIキー |
| Google Gemini | GEMINI_API_KEY  | Googleで取得したAPIキー |
| Anthropic Claude | ANTHROPIC_API_KEY | Anthropicで取得したAPIキー |

Windowsの場合は、Windowsの検索窓で「環境変数を編集」で検索すると設定画面が立ち上がるので、そこでユーザー環境変数を追加すればいいのだ。

<img src="doc/envvar.png" style="width:300px">

### 🛩️ 実行方法①：実行ファイル（EXEファイル）を使う方法

#### 1. プロジェクト用のフォルダの作成

任意の場所にプロジェクト用のフォルダを作成するのだ。

#### 2. アプリのダウンロード

以下のリンクから ZundaGPT2Lite.ZIP をダウンロードして、作成したフォルダに展開するのだ。

https://github.com/led-mirage/ZundaGPT2Lite/releases/tag/v1.10.0

#### 3. 実行

`ZundaGPT2Lite.exe`をダブルクリックすればアプリが起動するのだ。

※起動時にスプラッシュ画面を表示したくない人は、`ZundaGPT2Lite.ns.exe`を替わりに使ってほしいのだ。

#### 4. 注意事項

この実行ファイル（EXEファイル）は PyInstaller というライブラリを使って作成しているんだけど、割と頻繁にウィルス対策ソフトにマルウェアとかウィルスとかに誤認されるのだ。ネットとかを見るとこの問題が結構書かれているので、よくある事象のようだけど、残念なことに根本的な解決策は見つかっていないのだ。

もちろん、このアプリに悪意のあるプログラムは入っていないのだけど、気になる人は下の「Pythonで実行する方法」で実行してほしいのだ。

### 🛩️ 実行方法②：Pythonで実行する方法

#### 1. Pythonのインストール

あらかじめ Python 3.12.0 が動く環境を作っておくのだ。他のバージョンでも動くかもしれないけど、確認はしていないのだよ。

ボクは pyenv-win + venv で仮想環境を作ってそこで開発しているから、そういった方法でも問題ないのだ。

#### 2. プロジェクト用のフォルダの作成

任意の場所にプロジェクト用のフォルダを作成するのだ。

#### 3. ターミナルの起動

ターミナルかコマンドプロンプトを起動して、作成したプロジェクトフォルダに移動するのだ。

#### 4. ソースファイルのダウンロード

ZIPファイルをダウンロードして作成したフォルダに展開するのだ。  
または、Gitが使える方は以下のコマンドを実行してクローンしてもOKなのだ。

```bash
git clone https://github.com/led-mirage/ZundaGPT2Lite.git
```

#### 5. ライブラリのインストール

コマンドプロンプトから以下のコマンドを実行して、必要なライブラリをインストールするのだ。

```bash
pip install -r requirements.txt
```

#### 6. 実行

コマンドプロンプトから以下のコマンドを実行するとアプリが起動するのだ。

```bash
python app\main.py
```

#### 7. 起動用のバッチファイル（オプション）

以下のような起動用のバッチファイルを用意しておくと便利なのだ。

```bash
start pythonw app\main.py
```

Pythonの仮想環境を使用している場合は、以下の例のようにすればOKなのだ。

```bash
call venv\scripts\activate
start pythonw app\main.py
```

## キャラクターの設定

画面右上の⚙️ボタンを押すことで、使用するキャラクターを選択することができるのだ。

いくつかのデフォルトの設定がすでにあるけれど、設定ファイルをコピーして自分で編集することで自分好みのキャラクターを作ることができるのだ。

キャラクターの設定ファイル（settings_xxx.json）は`settings`フォルダの中に格納されているから、それをコピーして編集すればOKなのだ。

詳しい設定方法は[こちら](Readme_detail.md)をみて欲しいのだ。

## 注意事項

### ⚡ OpenAIの利用料金について

このアプリは無料だけど、OpenAI APIを使うには別途料金が発生するのだ（お試し用の無料枠もあるけど）。なので、使い過ぎには注意するのだ。定期的にOpenAIのサイトで現在の利用状況を確認するなどして自己管理して欲しいのだ。

そもそも自動チャージ設定を有効にしなければチャージされた分しか課金されないはずなので、そこまで心配する必要はないけれど、OpenAIのサイトでは月毎の利用上限なども設定できるのでそれらを活用して思わぬ出費を防ぐといいのだ。

### ⚡ Google Gemini APIの利用料金について

[この資料](Readme_gemini.md)にも書いたけど、現時点でGoogle Gemini APIには無料枠があるのだ。だから、基本的には無料枠を使ってアプリを利用すればいいと思うけど、もっとハードに使いたい場合は有料プランを考えてみるのもいいのだ。ただ、有料プランにした場合は、先に書いたOpenAIと同じように使い過ぎには注意して欲しいのだ。

### ⚡ Anthropic APIの利用料金について

Anthropic APIを利用するのにも別途料金（従量制）が発生するのだ。2024年12月29日時点で確認したところ、無料枠というものはなさそうなのだ。クレジットカードで好きな金額を課金するとAPIを利用できるようになるのだ。ただ、他のAPIと同じように使い過ぎには注意して欲しいのだ。

### ⚡ APIキーの重要性について

OpenAIやGoogle Gemini、AnthropicのAPIキーはあなただけのものなので、人に教えたらダメなのだ。流出すると悪い人に勝手に使われてしまう可能性があるのだ。もし流出してしまったら、OpenAIやGoogle、Anthropicのサイトで現在使っているAPIキーを削除して、別のAPIキーを作ればいいのだ。

ただOpenAIでは、APIキーをひとつしか持っていない場合、新しいAPIキーを作ってからじゃないと古いAPIキーを削除できないようなのだ。これはOpenAIの仕様のようなんだけど、ボク的にはちょっといただけない仕様だと思っているのだ。将来的に改善することを願っているけれど、最悪支払い情報（クレジットカード情報）を削除してしまえばいいような気もするのだ。

なにはともあれ、APIキーと利用料金には注意を払って欲しいのだ。

### ⚡ ウィルス対策ソフトの誤認問題

上でも書いているけれど、配布している実行ファイル（EXEファイル）が、マルウェアやウィルスに誤認されてしまうことがあるのだ。問題はPythonのプログラムを一つの実行ファイル（EXEファイル）にまとめることにあるようなのだが、回避方法がないためどうしようもないのだ。

これが嫌な人は（ボクも嫌だけど）、Python本体をインストールしてPythonから普通に実行して欲しいのだ。実行ファイルのほうが手軽だし、そのほうがPythonに詳しくない人にとっては簡単なんだけど、誤認問題がついて回ることは覚えておいて欲しいのだ。

VirusTotalでの[チェック結果](https://www.virustotal.com/gui/file/b486602ea56cb8f3aaeebd6d365f0ca252f812e78c8ed00a7208bba6dbd17a95)は以下の通りなのだ。  
（71個中3個のアンチウィルスエンジンで検出 :2025/02/09 v1.10.0）。

<img src="doc/virustotal_1.10.0.png" width="600">

### ⚡ 免責事項

いまのところ特に問題点は見つかっていないけど、バグなんてものは潜在的に必ずあるし、０になるなんてことはあり得ないのだ。また、もしバグがあってそのせいで貴方に損害を与えたとしても、著作権者はいかなる責任も負いかねるのでその点を理解して使って欲しいのだ。

## 使用しているライブラリ

### 🔖 pywebview 5.3.2

ホームページ： https://github.com/r0x0r/pywebview  
ライセンス：BSD-3-Clause license

### 🔖 openai 1.57.0

ホームページ： https://github.com/openai/openai-python  
ライセンス：Apache License 2.0

### 🔖 google-generativeai 0.8.3

ホームページ： https://github.com/google-gemini/generative-ai-python  
ライセンス：Apache License 2.0

### 🔖 anthropic 0.42.0

ホームページ： https://github.com/anthropics/anthropic-sdk-python  
ライセンス：MIT license

### 🔖 requests 2.32.3

ホームページ： https://requests.readthedocs.io/en/latest/  
ライセンス：Apache License 2.0

### 🔖 MathJax 3.2.2

ホームページ： https://github.com/mathjax/MathJax  
ライセンス：Apache License 2.0

### 🔖 Highlight.js 11.9.0

ホームページ：https://github.com/highlightjs/highlight.js  
ライセンス：BSD-3-Clause license

### 🔖 Marked 12.0.0

ホームページ：https://github.com/markedjs/marked  
ライセンス：MIT license

### 🔖 mark.js 8.11.1

ホームページ：https://github.com/julkue/mark.js  
ライセンス：MIT license

### 🔖 Font Awesome Free 6.7.2

ホームページ：https://fontawesome.com/
ライセンス：Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License

## ライセンス

© 2024-2025 led-mirage

本アプリケーションは [MITライセンス](https://opensource.org/licenses/MIT) の下で公開されているのだ。詳細については、プロジェクトに含まれる LICENSE ファイルを参照して欲しいのだ。

## バージョン履歴

### 1.10.0 (2025/02/09)

- ファイル横断検索機能の実装
- ボタンデザインを変更
- フィンランド語とスペイン語に対応

### 1.9.0 (2025/02/06)

- メッセージをコピーするボタンを追加
- カスタムコンテキストメニューを追加して、選択したテキストをコピーできるようにした
- Fix: 設定ウィンドウをキャンセルしたときに、Welcomeメッセージが表示される問題を修正
- Fix: AIに再回答を依頼したときに、メッセージの順序がおかしくなる問題を修正

### 1.8.0 (2025/02/02)

- コードブロックにクリップボードにコピーするボタンを追加

### 1.7.0 (2025/01/26)

- 設定画面にチャット設定ファイルをオープンする機能を追加
- Fix: 文字列のエスケープ処理が抜けている個所を修正

### 1.6.2 (2025/01/25)

- Fix: 環境変数がセットされていないときのエラー処理を変更

### 1.6.1 (2025/01/18)

- Fix: index.htmlで使っているscriptタグにSRIハッシュを追加

### 1.6.0 (2025/01/18)

- 言語サポート機能の追加（英語）

### 1.5.0 (2025/01/04)

- チャットアイコンを表示する機能を追加

### 1.4.3 (2025/01/02)

- Anthropic APIでエラーが発生したときのメッセージを分かりやすくした

### 1.4.2 (2025/01/01)

- コードブロック中にURLがあった場合に、不要な変換がおこなわれてしまう不具合を修正
- ZundaGPT2に合わせるために、バージョン1.4.1は欠番

### 1.4.0 (2024/12/29)

- Anthropic社のAI、Claudeシリーズに対応
- チャット内容の表示を改善

### 1.3.0 (2024/12/08)

- 起動時に表示されるスプラッシュ画面を追加

### 1.2.2 (2024/12/07)

- 古いライブラリでは動かなくなっていたので、以下のライブラリを最新版にアップデート
- pywebviewのバージョンを5.3.2に更新
- openaiのバージョンを1.57.0に更新
- google-generativeaiのバージョンを0.8.3に更新

### 1.2.1 (2024/07/06)

- 回答表示処理中にブラウザでエラー（OUT OF MEMORYなど）が発生する場合がある問題に対処  
  parsedSentenceメソッド中のMathJax.typesetPromise()をコメントアウト

### 1.2.0 (2024/06/23)

- アプリケーションアイコンの追加
- 印刷する場合、codeブロックの中のテキストを右端で折り返すように修正

### 1.1.1 (2024/06/22)

- 印刷機能の不備を修正するHotfix

### 1.1.0 (2024/06/22)

- 印刷機能の追加
- 画面上部のボタンにツールチップを追加
- PyInstallerのバージョンを6.8.0に更新

### 1.0.1 (2024/06/08)

- openaiのバージョンを1.33.0に更新
- google-generativeaiのバージョンを0.6.0に更新
- appConfig.jsonの初期値を訂正

### 1.0.0 (2024/6/08)

- バージョン番号をZundaGTP2に合わせて1.x.xに改定
- requestsのバージョンを2.32.3に更新

### 0.7.0 (2024/5/19)

- Google Gemini APIに対応

### 0.6.0 (2024/4/29)

- Tex形式の行列式が正しく表示されない問題を解消

### 0.5.0 (2024/4/21)

- Readmeの使用しているライブラリ欄に、pywebviewの記載が洩れていたため追記
- openaiのバージョンを1.12.0から1.23.2に更新
- ChatAPIのタイムアウト値を設定ファイル（app_config.json）に持つように変更
- AIの回答中にあるURLが正しくリンク表示にならない問題に対処

### 0.4.0 (2024/4/7)

- メッセージ送信中止機能を追加
- Ctrl + F でテキストを検索する機能を追加（F3 or Shift + F3で候補移動）
- Welcomeメッセージの追加
- 設定ファイルのフォーマット変更（Welcome関連項目追加）
- Copyrightを動的に設定するように修正
- 英文が右端で折り返さない問題を修正

### 0.3.0 (2024/3/30)

- 再回答ボタンを追加
- チャットログが１つしかない場合に、そのログを削除できないバグを修正

### 0.2.0 (2024/3/24)

- メッセージの削除ボタンを追加

### 0.1.1 (2024/3/16)

- 数式が正常にレンダリングされないバグを修正

### 0.1.0 (2024/3/10)
 
- ファーストリリース
- ZundaGTP2 v0.5.0から分岐
