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

### ⚙️ appConfig.json

#### 📌 system カテゴリ

##### ✨ log_folder（既定値 log）

チャットのログファイルを保存するフォルダを指定するのだ。この値が空文字の場合はログは保存されないのだ。

##### ✨ log_level（既定値 ERROR）

アプリケーションログを出力する際の閾値を指定するのだ。
指定できるのは、DEBUG、INFO、WARNING、ERROR、CRITICALの５種類なのだ。

##### ✨ settings_file（既定値 settings.json）

新規チャットを開始したときに使われるキャラクター設定ファイルを指定するのだ。GUIから変更できるのだ。

##### ✨ window_width（既定値 600）

ウィンドウの幅の初期値なのだ。

##### ✨ window_height（既定値 800）

ウィンドウの高さの初期値なのだ。

##### ✨ chat_api_timeout（既定値 30）

Chat APIのタイムアウト値を秒数で指定するのだ。

##### ✨ language（既定値 ja）

表示用の言語を指定するのだ。

##### ✨ font_family（既定値 空文字）

テキストが表示されるときに使用するフォントの種類を指定するのだ。

値が空文字の場合は以下のデフォルト値が使われるのだ。  
Söhne, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif, Helvetica Neue, Arial, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji

##### ✨ font_size（既定値 16）

テキストが表示されるときに使用するフォントサイズを指定するのだ。

##### ✨ theme（既定値 light）

UIのテーマを指定するのだ。`light` または `dark` を指定できるのだ。

#### 📌 gemini カテゴリ

##### ✨ safety_filter_harassment（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。ハラスメントに関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

##### ✨ safety_filter_hate_speech（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。ヘイトスピーチに関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

##### ✨ safety_filter_sexually_explicit（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。性表現に関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

#### ✨ safety_filter_dangerous_content（既定値 BLOCK_MEDIUM_AND_ABOVE）

Gemini用の安全性フィルタ設定なのだ。危険な内容に関するしきい値を設定できるのだ。詳しくは[こちらの資料](Readme_gemini.md)を参照して欲しいのだ。

### ⚙️ settings.json

settings.jsonはsettingsフォルダの中に格納されているのだ。声のキャラクターを変えたいときなどは、このファイルを編集するといいのだ。また、このファイルをコピーして別の名前を付けて保存することで、複数の設定を保存しておくことができるのだ。設定を切り替えるには、ウィンドウの設定ボタンを押すといいのだ。

#### 📌 settings カテゴリ

##### ✨ display_name（既定値 ZundaGPT）

ウィンドウの左上に表示されるタイトルなのだ。

##### ✨ description（既定値 既定値）

設定切替画面で表示される説明文なのだ。どんな設定なのかを書いておくといいのだ。

##### ✨ welcome_title（既定値 Welcome）

新しくチャットを始めたときに画面に表示されるメッセージなのだ。

##### ✨ welcome_message（既定値 なんでも聞いてほしいのだ！）

新しくチャットを始めたときに画面に表示されるメッセージなのだ。welcome_titleの下に表示されるのだ。

##### ✨ welcome_icon_visible（既定値 true）

Welcome画面にアイコンを表示するかどうかの設定。  
設定例：true or false

##### ✨ group（既定値 Default）

設定のグループ分けに使用するのだ。設定ファイルが多くなった時に便利なのだ。

#### 📌 user カテゴリ

##### ✨ name（既定値 あなた）

あなたの名前の設定なのだ。

##### ✨ name_color（既定値 #007bff）

あなたの名前の色の設定なのだ。

##### ✨ icon（既定値 空文字）

発言者名の横に表示するアイコンの設定なのだ。PNG形式の画像ファイルを指定できるのだ。空文字にするとアイコンは表示されないのだ。

例：chat_icons/user_black.png

chat_iconsフォルダの中にいくつかアイコン用の画像を用意してあるのだ。

#### 📌 assistant カテゴリ

##### ✨ name（既定値 ずんだ）

チャットアシスタントの名前の設定なのだ。

##### ✨ name_color（既定値 #006400）

チャットアシスタントの名前の色の設定なのだ。

##### ✨ icon（既定値 空文字）

発言者名の横に表示するアイコンの設定なのだ。PNG形式の画像ファイルを指定できるのだ。空文字にするとアイコンは表示されないのだ。

例：chat_icons/zunda_lime.png

chat_iconsフォルダの中にいくつかアイコン用の画像を用意してあるのだ。

#### 📌 chat カテゴリ

##### ✨ api（既定値 OpenAI）

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

##### ✨ api_key_envvar（既定値 ""）

APIキーを格納する環境変数名をカスタマイズできるのだ。

デフォルトでは上記APIキーが使われるけど、ここで値を指定した場合それが使われるのだ。

##### ✨ api_endpoint_envvar（既定値 ""）

APIエンドポイント格納する環境変数名をカスタマイズできるのだ（AzureOpenAIのみ）。

デフォルトではAZURE_OPENAI_ENDPOINTが使われるけど、ここで値を指定した場合それが使われるのだ。

##### ✨ api_base_url（既定値 ""）

OpenAI互換APIを使用する場合に、APIのベースURLを指定するのだ。

デフォルトでは空文字列になっていて、OpenAI互換APIを使用しない場合は何も設定しなくていいのだ。

##### ✨ model（既定値 gpt-4.1-mini）

使用するAIのモデル名を指定するのだ。  
高性能なモデルほど賢いけれど、その分利用料も上がるので注意して欲しいのだ。

利用できるモデルの一覧と料金は以下のリンクで確認できるのだ。  
※ ZundaGPT2で利用可能なモデルはReadme.mdに記載されているのだ。  

- **OpenAI**
    - https://platform.openai.com/docs/pricing
- **AzureOpenAI**
    - Azureの場合は、デプロイする際につけたモデル名を指定するのだ。
- **Gemini**
    - https://ai.google.dev/gemini-api/docs/models?hl=ja
- **Claude**
    - https://docs.anthropic.com/ja/docs/about-claude/models/overview

##### ✨ instraction（既定値 君は優秀なアシスタント…以下略）

AIのキャラづけの設定なのだ。ここで、AIの台詞をずんだもんっぽくするようお願いしているのだ。ここを変更することで、ずんだもん以外のキャラクターっぽい回答を生成することも可能なのだ。

##### ✨ bad_response（既定値 答えられないのだ）

何らかの原因でAIが回答できなかった場合に表示するセリフを設定するのだ。無理なお願いをするとAIが答えてくれない場合があるから気を付けるといいのだ。

##### ✨ history_size（既定値 6）

AIに送信する過去の会話の履歴数を設定するのだ。この値が大きいほど前の回答、質問を考慮した回答をAIが生成するようになって、会話のつながりがよくなるのだ。ただ、その分利用料金も増えるので注意が必要なのだ。

この設定がある理由を考えればわかるけど、OpenAIのAIは過去の会話を覚えていないのだ。質問をするたびに、過去の会話もAIに送信することで、AIは会話のつながりを知ることができるのだ。ただ利用料金は送信するデータ量が増えるとその分加算されるので、バランスをとることが大事なのだ。

##### ✨ history_char_limit（既定値 0）

送信する会話の履歴を文字数で制限する設定なのだ。history_size以内でもこの制限値を超えた場合はその部分でカットされるのだ。この値が0の場合は制限はかからないのだ。

#### 📌 custom_style カテゴリ

##### ✨ enable（既定値 false）

カスタムスタイルを有効にする場合は`true`にしてね。
有効にするとキャラクター毎の背景画像などを設定できるようになるのだ。

##### ✨ background_image（既定値 空文字）

背景画像を設定する場合に指定するのだ。

インターネットの画像を指定する場合は、こんな風にURLを書くのだ。
```
"https://github.com/led-mirage/ZundaGPT2Lite/blob/main/doc/wallpaper/cloud.jpg?raw=true"
```

ローカルPC内にある画像を指定する場合は、こんな風にそのパスを書くのだ。
```
"C:\\Users\\USERNAME\\Pictures\\cloud.jpg"
```

##### ✨ background_image_opacity（既定値 "0.8"）

背景画像の透過度を指定するのだ。  
1.0が透過なしで、0.0に近づくほど透過するようになるのだよ。

##### ✨ body_bgcolor（既定値 空文字）

アプリ全体の背景色。  
背景画像の透過率を高くすると、この背景色が透けて見えるようになるのだ。  
設定例："white"、"#fff"、"rgb(255, 255, 255)"

##### ✨ header_color（既定値 空文字）

ヘッダ部分の文字色。  
設定例："black"、"#000"、"rgb(0, 0, 0)"

##### ✨ welcome_title_color（既定値 空文字）

Welcomeタイトルの文字色。  
設定例："black"、"#000"、"rgb(0, 0, 0)"

##### ✨ welcome_message_color（既定値 空文字）

Welcomeメッセージの文字色。  
設定例："black"、"#000"、"rgb(0, 0, 0)"

##### ✨ speaker_name_text_shadow（既定値 空文字）

キャラクター名テキストの影の色。  
設定例："0 0 10px 3px rgba(0,0,0,0.2)"

##### ✨ message_text_bgcolor（既定値 空文字）

チャットメッセージ表示エリアの背景色。
設定例："rgba(255,255,255,0.5)"

##### ✨ message_text_color（既定値 空文字）

チャットメッセージテキストの表示色。
設定例："black"、"#000"、"rgb(0, 0, 0)"

##### ✨ message_text_shadow（既定値 空文字）

チャットメッセージテキストの影の色。  
設定例："0 0 10px 3px rgba(0,0,0,0.2)"

##### ✨ message_text_border_radius（既定値 空文字）

チャットメッセージ表示エリアの角の丸みの半径。  
設定例："10px"

##### ✨ message_text_em_color（既定値 空文字）

強調文字（斜体）のテキスト色。
設定例："red"、"#f00"、"rgb(255, 0, 0)"

#### 📌 claude_options カテゴリ

##### ✨ max_tokens（既定値 4096）

claudeの最大出力トークン数を指定するのだ。この値が大きいほどclaudeは長い回答を生成できるようになるのだよ。

##### ✨ extended_thinking（既定値 false）

claude 3.7 SonnetのExtended Thinkingモードの有効・無効を設定するのだ。この値をtrueにするとより深く考えるようになるけど、出力時間も長くなるから注意して欲しいのだよ。

##### ✨ budget_tokens（既定値 2048）

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
