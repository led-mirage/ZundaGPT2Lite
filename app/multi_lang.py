# ZundaGPT2 Lite
#
# 多言語対応文字リソース
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

# テキストリソースの定義
text_resources = {
    # 日本語
    "ja": {
        "ERROR_MISSING_OPENAI_API_KEY": "環境変数 OPENAI_API_KEY が設定されていません。",
        "ERROR_MISSING_AZURE_OPENAI_ENDPOINT": "環境変数 AZURE_OPENAI_ENDPOINT が設定されていません。",
        "ERROR_MISSING_AZURE_OPENAI_API_KEY": "環境変数 AZURE_OPENAI_API_KEY が設定されていません。",
        "ERROR_MISSING_GEMINI_API_KEY": "環境変数 GEMINI_API_KEY が設定されていません。",
        "ERROR_MISSING_ANTHROPIC_API_KEY": "環境変数 ANTHROPIC_API_KEY が設定されていません。",
        "ERROR_API_ID_IS_INCORRECT": "API IDが間違っています。",
        "ERROR_API_TIMEOUT": "APIの呼び出しがタイムアウトしたのだ",
        "ERROR_API_AUTHENTICATION_FAILED": "APIの認証に失敗したのだ",
        "ERROR_API_ENDPOINT_INCORRECT": "APIのエンドポイントが間違っているのだ",
        "ERROR_CONVERSATION_CONTENT_INAPPROPRIATE": "会話の内容が不適切だと判断されたのだ",
        "ERROR_RATE_LIMIT_REACHED": "レート制限に達したのだ",
        "ERROR_API_ERROR_OCCURRED": "APIエラーが発生したのだ",
        "ERROR_UNKNOWN_OCCURED": "なんかわからないエラーが発生したのだ",
    },
    # 英語
    "en": {
        "ERROR_MISSING_OPENAI_API_KEY": "The environment variable OPENAI_API_KEY is not set.",
        "ERROR_MISSING_AZURE_OPENAI_ENDPOINT": "The environment variable AZURE_OPENAI_ENDPOINT is not set.",
        "ERROR_MISSING_AZURE_OPENAI_API_KEY": "The environment variable AZURE_OPENAI_API_KEY is not set.",
        "ERROR_MISSING_GEMINI_API_KEY": "The environment variable GEMINI_API_KEY is not set.",
        "ERROR_MISSING_ANTHROPIC_API_KEY": "The environment variable ANTHROPIC_API_KEY is not set.",
        "ERROR_API_ID_IS_INCORRECT": "API ID is incorrect.",
        "ERROR_API_TIMEOUT": "The API call timed out.",
        "ERROR_API_AUTHENTICATION_FAILED": "Failed to authenticate the API.",
        "ERROR_API_ENDPOINT_INCORRECT": "The API endpoint is incorrect.",
        "ERROR_CONVERSATION_CONTENT_INAPPROPRIATE": "The content of the conversation was deemed inappropriate.",
        "ERROR_RATE_LIMIT_REACHED": "Rate limit reached.",
        "ERROR_API_ERROR_OCCURRED": "An API error occurred.",
        "ERROR_UNKNOWN_OCCURED": "An unknown error has occurred.",
    },
    # フィンランド語
    "fi": {
        "ERROR_MISSING_OPENAI_API_KEY": "Ympäristömuuttujaa OPENAI_API_KEY ei ole asetettu.",
        "ERROR_MISSING_AZURE_OPENAI_ENDPOINT": "Ympäristömuuttujaa AZURE_OPENAI_ENDPOINT ei ole asetettu.",
        "ERROR_MISSING_AZURE_OPENAI_API_KEY": "Ympäristömuuttujaa AZURE_OPENAI_API_KEY ei ole asetettu.",
        "ERROR_MISSING_GEMINI_API_KEY": "Ympäristömuuttujaa GEMINI_API_KEY ei ole asetettu.",
        "ERROR_MISSING_ANTHROPIC_API_KEY": "Ympäristömuuttujaa ANTHROPIC_API_KEY ei ole asetettu.",
        "ERROR_API_ID_IS_INCORRECT": "API-tunnus on virheellinen.",
        "ERROR_API_TIMEOUT": "API-kutsu aikakatkaistiin.",
        "ERROR_API_AUTHENTICATION_FAILED": "API:n todennus epäonnistui.",
        "ERROR_API_ENDPOINT_INCORRECT": "API:n päätepiste on virheellinen.",
        "ERROR_CONVERSATION_CONTENT_INAPPROPRIATE": "Keskustelun sisältö todettiin sopimattomaksi.",
        "ERROR_RATE_LIMIT_REACHED": "Nopeusraja on saavutettu.",
        "ERROR_API_ERROR_OCCURRED": "API-virhe tapahtui.",
        "ERROR_UNKNOWN_OCCURED": "Tapahtui tuntematon virhe.",
    },
    # スペイン語語
    "es": {
        "ERROR_MISSING_OPENAI_API_KEY": "La variable de entorno OPENAI_API_KEY no está configurada.",
        "ERROR_MISSING_AZURE_OPENAI_ENDPOINT": "La variable de entorno AZURE_OPENAI_ENDPOINT no está configurada.",
        "ERROR_MISSING_AZURE_OPENAI_API_KEY": "La variable de entorno AZURE_OPENAI_API_KEY no está configurada.",
        "ERROR_MISSING_GEMINI_API_KEY": "La variable de entorno GEMINI_API_KEY no está configurada.",
        "ERROR_MISSING_ANTHROPIC_API_KEY": "La variable de entorno ANTHROPIC_API_KEY no está configurada.",
        "ERROR_API_ID_IS_INCORRECT": "El ID de la API es incorrecto.",
        "ERROR_API_TIMEOUT": "La llamada a la API se agotó.",
        "ERROR_API_AUTHENTICATION_FAILED": "Falló la autenticación de la API.",
        "ERROR_API_ENDPOINT_INCORRECT": "El endpoint de la API es incorrecto.",
        "ERROR_CONVERSATION_CONTENT_INAPPROPRIATE": "El contenido de la conversación fue considerado inapropiado.",
        "ERROR_RATE_LIMIT_REACHED": "Se alcanzó el límite de solicitudes.",
        "ERROR_API_ERROR_OCCURRED": "Ocurrió un error en la API.",
        "ERROR_UNKNOWN_OCCURED": "Ocurrió un error desconocido.",
    }
}

# 現在の言語を保存する変数
current_language = "ja"

# 言語を設定する関数
def set_current_language(language):
    global current_language
    current_language = language
    if language in text_resources:
        current_language = language
    else:
        print(f"Warning: '{language}' is not a valid language code. Defaulting to 'en'.")
        current_language = "en"

# テキストリソースを取得する関数
def get_text_resource(key):
    return text_resources.get(current_language, {}).get(key, key)
