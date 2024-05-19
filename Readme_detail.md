# ZundaGPT2 Lite　追加資料

Copyright (c) 2024 led-mirage

## はじめに

この追加資料では、より詳しい情報を記載しているのだ。

- [アプリを動かすのに必要なもの](#アプリを動かすのに必要なもの)
- [設定ファイル](#設定ファイル)
- [通信先](#通信先)

## アプリを動かすのに必要なもの

### ✅ OpenAIアカウントとAPIキー

チャットの部分はOpenAIのAIを使用しているので、OpenAIのアカウントとAPIの利用登録（課金およびAPIキーの作成）が必要なのだ。

アカウントを作成すると、作ってから３ヵ月間有効な無料枠（$18）があるようなので、それを使ってもいいのだ。ボクの場合は利用開始から３ヵ月以上経ってしまっていたので、無料枠は利用できなくて、仕方ないから$10課金したのだ。

APIキーの作成は特に難しくないのだ。OpenAI APIの設定画面に入って、左側の`API Keys`というメニューから新しいAPIキーを作成すればいいのだ。作成するときに表示されるAPIキーは、作成後には２度と表示できないからメモ帳などにコピペして保存しておくといいのだ。このキーはあとから設定に必要になるのだ。

OpenAI … https://platform.openai.com/

### ✅ Google Gemini APIのAPIキー

バージョン0.7.0からGoogle Gemini APIにも対応したので、OpenAIの代わりにGoogle Gemini APIを使用することもできるのだ。

現時点でGoogle Gemini APIには無料プランが設定されているので、OpenAIのAPIよりも気軽に利用することができるのだ。Google Gemini APIを使用したい場合は、[専用の資料](Readme_gemini.md)を用意したので、それを参照して欲しいのだ。

## 設定ファイル

設定ファイルは２つあるのだ。ひとつはシステムの設定が書かれているapp_config.json。もうひとつはチャットするキャラクターの情報が書かれているsettings.jsonなのだ。

### ⚙️ app_config.json

#### ✨ system/log_folder（既定値 log）

チャットのログファイルを保存するフォルダを指定するのだ。この値が空文字の場合はログは保存されないのだ。

#### ✨ system/settings_file（既定値 settings.json）

新規チャットを開始したときに使われるキャラクター設定ファイルを指定するのだ。GUIから変更できるのだ。

#### ✨ system/window_width（既定値 600）

ウィンドウの幅の初期値なのだ。

#### ✨ system/window_height（既定値 800）

ウィンドウの高さの初期値なのだ。

#### ✨ system/chat_api_timeout（既定値 30）

Chat APIのタイムアウト値を秒数で指定するのだ。

#### ✨ gemini/safty_filter_harassment（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。ハラスメントに関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

#### ✨ gemini/safty_filter_hate_speech（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。ヘイトスピーチに関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

#### ✨ gemini/safty_filter_sexually_explicit（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。性表現に関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

#### ✨ gemini/safty_filter_dangerous_content（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。危険な内容に関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

### ⚙️ settings.json

settings.jsonはsettingsフォルダの中に格納されているのだ。声のキャラクターを変えたいときなどは、このファイルを編集するといいのだ。また、このファイルをコピーして別の名前を付けて保存することで、複数の設定を保存しておくことができるのだ。設定を切り替えるには、ウィンドウの設定ボタンを押すといいのだ。

#### ✨ user/name（既定値 あなた）

あなたの名前の設定なのだ。

#### ✨ user/name_color（既定値 #007bff）

あなたの名前の色の設定なのだ。

#### ✨ assistant/name（既定値 ずんだ）

チャットアシスタントの名前の設定なのだ。

#### ✨ assistant/name_color（既定値 #006400）

チャットアシスタントの名前の色の設定なのだ。

#### ✨ chat/api（既定値 OpenAI）

使用するAPIの設定なのだ。設定できる値は`OpenAI`と`AzureOpenAI`と`Gemini`の３つなのだ。

使用するAPIによって設定しないといけない環境変数が異なるから注意して欲しいのだ。

**OpenAI**

| 変数名 | 値 |
|------|------|
| OPENAI_API_KEY  | OpenAIで取得したAPIキー |

**AzureOpenAI**

| 変数名 | 値 |
|------|------|
| AZURE_OPENAI_ENDPOINT | Azure OpenAI Serviceの通信先（エンドポイント）|
| AZURE_OPENAI_API_KEY  | Azureで取得したAPIキー |

**Gemini**

| 変数名 | 値 |
|------|------|
| GEMINI_API_KEY  | Googleで取得したAPIキー |

#### ✨ chat/model（既定値 gpt-3.5-turbo-0125）

使用するAIのモデル名を指定するのだ。使用するAPIによって指定できるモデル名が異なるので注意して欲しいのだ。

**OpenAI**

既定はリーズナブルなGTP3.5を使用しているのだ。もっと賢くしたい場合はGPT4.0系も使えるけれど、その分利用量が上がるので注意するのだ。使用できるモデルの一覧と利用料金は以下のリンクで確認できるのだ。

モデルの一覧 … https://platform.openai.com/docs/models  
利用料金 … https://openai.com/pricing#language-models

**AzureOpenAI**

Azure上でモデルをデプロイする際につけてモデル名を指定するのだ。

**Gemini**

Geminiでは以下のモデル名を指定できるのだ。詳しくは、[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

- gemini-1.0-pro-latest
- gemini-1.5-flash-latest
- gemini-1.5-pro-latest

#### ✨ chat/instraction（既定値 君は優秀なアシスタント…以下略）

AIのキャラづけの設定なのだ。ここで、AIの台詞をずんだもんっぽくするようお願いしているのだ。ここを変更することで、ずんだもん以外のキャラクターっぽい回答を生成することも可能なのだ。

#### ✨ chat/bad_response（既定値 答えられないのだ）

何らかの原因でAIが回答できなかった場合に表示するセリフを設定するのだ。無理なお願いをするとAIが答えてくれない場合があるから気を付けるといいのだ。

#### ✨ chat/history_size（既定値 6）

AIに送信する過去の会話の履歴数を設定するのだ。この値が大きいほど前の回答、質問を考慮した回答をAIが生成するようになって、会話のつながりがよくなるのだ。ただ、その分利用料金も増えるので注意が必要なのだ。

この設定がある理由を考えればわかるけど、OpenAIのAIは過去の会話を覚えていないのだ。質問をするたびに、過去の会話もAIに送信することで、AIは会話のつながりを知ることができるのだ。ただ利用料金は送信するデータ量が増えるとその分加算されるので、バランスをとることが大事なのだ。

## 通信先

このアプリの通信先は以下の通りなのだ。

### 🌐 OpenAI API（HTTPS）

chat/apiに`OpenAI`を指定した場合は、チャットの回答を取得するために OpenAIのサーバーと通信を行うのだ。通信方法は、OpenAIのライブラリを使用しているのだ。

### 🌐 Azure OpenAI Service（HTTPS）

chat/apiに`AzureOpenAI`を指定した場合は、チャットの回答を取得するために Microsoft Azure OpenAI Serviceと通信を行うのだ。通信方法は、OpenAIのライブラリを使用しているのだ。

### 🌐 Google Gemini API（HTTPS）

chat/apiに`Gemini`を指定した場合は、チャットの回答を取得するために Googleのサーバーと通信を行うのだ。通信方法は、Googleのライブラリを使用しているのだ。

### ➰ pywebview（TCP）

このアプリではGUIをpywebviewで作ってるんだけど、UI(HTML)とバックエンドのPythonプログラムとの連携をとるのにTCPでリスニングしているみたい。詳しいことはわからないのだ。

## ファイル入出力

### 🗒️ 設定ファイル（appConfig.json）

システムの設定を記載したファイル。初回起動時に自動的に作成されるのだ。

### 🗒️ 設定ファイル（settings.json）

チャットするキャラクターの情報を記載したファイル。これも、初回起動時に自動的に作成されるのだ。

### 🗒️ チャットログファイル（chatlog-yyyymmdd-hhmmss.json）

チャットの内容を記載したファイル。ファイル名の日時はチャットを開始した日時なのだ。
