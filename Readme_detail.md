# ZundaGPT2 Lite　追加資料

Copyright (c) 2024-2025 led-mirage

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


### ✅ Anthropic APIのAPIキー

バージョン1.4.0からAnthropic API（Claudeシリーズ）にも対応したのだ。APIを利用するには[Anthropic Console](https://console.anthropic.com/)のアカウントとAPIの利用登録（課金およびAPIキーの作成）が必要なのだ。

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

#### ✨ system/language（既定値 ja）

表示用の言語を指定するのだ。

#### ✨ system/font_family（既定値 空文字）

テキストが表示されるときに使用するフォントの種類を指定するのだ。

値が空文字の場合は以下のデフォルト値が使われるのだ。  
Söhne, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif, Helvetica Neue, Arial, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji

#### ✨ system/font_size（既定値 16）

テキストが表示されるときに使用するフォントサイズを指定するのだ。

#### ✨ system/log_level（既定値 INFO）

アプリケーションログを出力する際の閾値を指定するのだ。
指定できるのは、DEBUG、INFO、WARNING、ERROR、CRITICALの５種類なのだ。

#### ✨ gemini/safety_filter_harassment（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。ハラスメントに関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

#### ✨ gemini/safety_filter_hate_speech（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。ヘイトスピーチに関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

#### ✨ gemini/safety_filter_sexually_explicit（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。性表現に関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

#### ✨ gemini/safety_filter_dangerous_content（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。危険な内容に関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

### ⚙️ settings.json

settings.jsonはsettingsフォルダの中に格納されているのだ。声のキャラクターを変えたいときなどは、このファイルを編集するといいのだ。また、このファイルをコピーして別の名前を付けて保存することで、複数の設定を保存しておくことができるのだ。設定を切り替えるには、ウィンドウの設定ボタンを押すといいのだ。

#### ✨ settings/display_name（既定値 ZundaGPT）

ウィンドウの左上に表示されるタイトルなのだ。

#### ✨ settings/description（既定値 既定値）

設定切替画面で表示される説明文なのだ。どんな設定なのかを書いておくといいのだ。

#### ✨ settings/welcome_title（既定値 Welcome）

新しくチャットを始めたときに画面に表示されるメッセージなのだ。

#### ✨ settings/welcome_message（既定値 なんでも聞いてほしいのだ！）

新しくチャットを始めたときに画面に表示されるメッセージなのだ。welcome_titleの下に表示されるのだ。

#### ✨ settings/group（既定値 Default）

設定のグループ分けに使用するのだ。設定ファイルが多くなった時に便利なのだ。

#### ✨ user/name（既定値 あなた）

あなたの名前の設定なのだ。

#### ✨ user/name_color（既定値 #007bff）

あなたの名前の色の設定なのだ。

#### ✨ user/icon（既定値 空文字）

発言者名の横に表示するアイコンの設定なのだ。PNG形式の画像ファイルを指定できるのだ。空文字にするとアイコンは表示されないのだ。

例：chat_icons/user_black.png

chat_iconsフォルダの中にいくつかアイコン用の画像を用意してあるのだ。

#### ✨ assistant/name（既定値 ずんだ）

チャットアシスタントの名前の設定なのだ。

#### ✨ assistant/name_color（既定値 #006400）

チャットアシスタントの名前の色の設定なのだ。

#### ✨ assistant/icon（既定値 空文字）

発言者名の横に表示するアイコンの設定なのだ。PNG形式の画像ファイルを指定できるのだ。空文字にするとアイコンは表示されないのだ。

例：chat_icons/zunda_lime.png

chat_iconsフォルダの中にいくつかアイコン用の画像を用意してあるのだ。

#### ✨ chat/api（既定値 OpenAI）

使用するAPIの設定なのだ。設定できる値は`OpenAI`と`AzureOpenAI`と`Gemini`と`Claude`の４つなのだ。

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

**Claude**

| 変数名 | 値 |
|------|------|
| ANTHROPIC_API_KEY  | Anthropicで取得したAPIキー |

#### ✨ chat/api_key_envvar（既定値 ""）

APIキーを格納する環境変数名をカスタマイズできるのだ。

デフォルトでは上記APIキーが使われるけど、ここで値を指定した場合それが使われるのだ。

#### ✨ chat/api_endpoint_envvar（既定値 ""）

APIエンドポイント格納する環境変数名をカスタマイズできるのだ（AzureOpenAIのみ）。

デフォルトではAZURE_OPENAI_ENDPOINTが使われるけど、ここで値を指定した場合それが使われるのだ。

#### ✨ chat/model（既定値 gpt-3.5-turbo-0125）

使用するAIのモデル名を指定するのだ。使用するAPIによって指定できるモデル名が異なるので注意して欲しいのだ。

**OpenAI**

既定はリーズナブルなGTP-4o miniを使用しているのだ。もっと賢くしたい場合はGPT-4o系も使えるけれど、その分利用量が上がるので注意するのだ。使用できるモデルの一覧と利用料金は以下のリンクで確認できるのだ。

モデルの一覧 … https://platform.openai.com/docs/models  
利用料金 … https://openai.com/pricing#language-models

o1、o1-miniにも対応しているけれど、これらのモデルは`system`メッセージが使えないので、AIのキャラ付けができないので注意して欲しいのだ（settings.jsonの`instruction`は無効になるのだ）。

**AzureOpenAI**

Azure上でモデルをデプロイする際につけてモデル名を指定するのだ。

**Gemini**

Geminiでは以下のモデル名を指定できるのだ。詳しくは、[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

- gemini-1.0-pro-latest
- gemini-1.5-flash-latest
- gemini-1.5-pro-latest

**Claude**

Anthropicの場合、2024年12月29日時点で、以下のモデルを指定できるのだ。

- Claude 3.5 Sonnet 2024-10-22
- Claude 3.5 Sonnet 2024-06-20
- Claude 3.5 Haiku
- Claude 3 Opus
- Claude 3 Sonnet
- Claude 3 Haiku

#### ✨ chat/instraction（既定値 君は優秀なアシスタント…以下略）

AIのキャラづけの設定なのだ。ここで、AIの台詞をずんだもんっぽくするようお願いしているのだ。ここを変更することで、ずんだもん以外のキャラクターっぽい回答を生成することも可能なのだ。

#### ✨ chat/bad_response（既定値 答えられないのだ）

何らかの原因でAIが回答できなかった場合に表示するセリフを設定するのだ。無理なお願いをするとAIが答えてくれない場合があるから気を付けるといいのだ。

#### ✨ chat/history_size（既定値 6）

AIに送信する過去の会話の履歴数を設定するのだ。この値が大きいほど前の回答、質問を考慮した回答をAIが生成するようになって、会話のつながりがよくなるのだ。ただ、その分利用料金も増えるので注意が必要なのだ。

この設定がある理由を考えればわかるけど、OpenAIのAIは過去の会話を覚えていないのだ。質問をするたびに、過去の会話もAIに送信することで、AIは会話のつながりを知ることができるのだ。ただ利用料金は送信するデータ量が増えるとその分加算されるので、バランスをとることが大事なのだ。

#### ✨ claude_options/max_tokens（既定値 4096）

claudeの最大出力トークン数を指定するのだ。この値が大きいほどclaudeは長い回答を生成できるようになるのだよ。

#### ✨ claude_options/extended_thinking（既定値 false）

claude 3.7 SonnetのExtended Thinkingモードの有効・無効を設定するのだ。この値をtrueにするとより深く考えるようになるけど、出力時間も長くなるから注意して欲しいのだよ。

#### ✨ claude_options/budget_tokens（既定値 2048）

claude 3.7 SonnetのExtended Thinkingモードが有効のときの予算トークン数を指定するのだ。この値が大きいほどClaudeは深く考えるようになるのだ。ただ大きくすると出費も増えるから注意して欲しいのだ。この値は1024以上で、max_tokensよりも小さい値を指定する必要があるのだ。

## 通信先

このアプリの通信先は以下の通りなのだ。

### 🌐 OpenAI API（HTTPS）

chat/apiに`OpenAI`を指定した場合は、チャットの回答を取得するために OpenAIのサーバーと通信を行うのだ。通信方法は、OpenAIのライブラリを使用しているのだ。

### 🌐 Azure OpenAI Service（HTTPS）

chat/apiに`AzureOpenAI`を指定した場合は、チャットの回答を取得するために Microsoft Azure OpenAI Serviceと通信を行うのだ。通信方法は、OpenAIのライブラリを使用しているのだ。

### 🌐 Google Gemini API（HTTPS）

chat/apiに`Gemini`を指定した場合は、チャットの回答を取得するために Googleのサーバーと通信を行うのだ。通信方法は、Googleのライブラリを使用しているのだ。

### 🌐 Anthropic API（HTTPS）

chat/apiに`Claude`を指定した場合は、チャットの回答を取得するために Anthropicのサーバーと通信を行うのだ。通信方法は、Anthropicのライブラリを使用しているのだ。

### ➰ pywebview（TCP）

このアプリではGUIをpywebviewで作ってるんだけど、UI(HTML)とバックエンドのPythonプログラムとの連携をとるのにTCPでリスニングしているみたい。詳しいことはわからないのだ。

## ファイル入出力

### 🗒️ 設定ファイル（appConfig.json）

システムの設定を記載したファイル。初回起動時に自動的に作成されるのだ。

### 🗒️ 設定ファイル（settings.json）

チャットするキャラクターの情報を記載したファイル。これも、初回起動時に自動的に作成されるのだ。

### 🗒️ チャットログファイル（chatlog-yyyymmdd-hhmmss.json）

チャットの内容を記載したファイル。ファイル名の日時はチャットを開始した日時なのだ。
