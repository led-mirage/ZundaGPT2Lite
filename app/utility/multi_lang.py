# ZundaGPT2 / ZundaGPT2 Lite
#
# 言語サポート
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import textwrap

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
        "ERROR_UNKNOWN_OCCURRED": "なんかわからないエラーが発生したのだ",
        "ERROR_GOOGLETTS_FFMPEG_NOT_FOUND": "Google Text-to-Speechを使用するには、あらかじめFFmpegをインストールしておく必要があります\n\nFFmpegをインストールしてパスを通しておいてください",
        "SUMMARIZE_PROMPT": textwrap.dedent("""\
            以下のチャット会話を分かりやすく要約してください。

            【出力形式】
            - タイトル(h2)：会話の主題を端的に表現
            - ジャンル(h3)：会話の分類を一言で
            - 要点（h3）：箇条書き
            - まとめ（h3）：会話の結論や決定事項を簡潔に

            【制約事項】
            - マークダウン形式で出力
            - 重要なキーワードは**強調**
            - 技術的な用語は`コードスタイル`で表示

            ---
            """),
        "GENERATING_RESPONSE": "回答を生成しています…",
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
        "ERROR_UNKNOWN_OCCURRED": "An unknown error has occurred.",
        "ERROR_GOOGLETTS_FFMPEG_NOT_FOUND": "To use Google Text-to-Speech, you need to install FFmpeg beforehand.\n\nPlease install FFmpeg and ensure that it is added to the system path.",
        "SUMMARIZE_PROMPT": textwrap.dedent("""\
            Please summarize the following chat conversation clearly and concisely.

            [Output Format]
            - Title (h2): Briefly express the topic of the conversation
            - Genre (h3): Classify the conversation in one word
            - Key Points (h3): Bullet points
            - Summary (h3): A concise conclusion or decision point from the conversation

            [Constraints]
            - Output in Markdown format
            - Highlight important keywords with **
            - Display technical terms in `code style`

            ---
            """),
        "GENERATING_RESPONSE": "Generating response...",
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
        "ERROR_UNKNOWN_OCCURRED": "Tapahtui tuntematon virhe.",
        "ERROR_GOOGLETTS_FFMPEG_NOT_FOUND": "Google Text-to-Speech -toiminnon käyttö edellyttää FFmpeg-asennusta etukäteen.\n\nAsenna FFmpeg ja varmista, että se on lisätty järjestelmäpolkuun.",
        "SUMMARIZE_PROMPT": textwrap.dedent("""\
            Tiivistä seuraava keskustelu selkeästi ja ytimekkäästi.

            [Output Format]
            - Otsikko (h2): Kuvaa keskustelun aihe lyhyesti
            - Genre (h3): Luokittele keskustelu yhdellä sanalla
            - Avainkohdat (h3): Luettelomerkit
            - Yhteenveto (h3): Ytimekäs johtopäätös tai päätöspiste keskustelusta

            [Constraints]
            - Tulosta Markdown-muodossa
            - Korosta tärkeitä avainsanoja **
            - Näytä tekniset termit `koodityylillä`

            ---
            """),
        "GENERATING_RESPONSE": "Luodaan vastausta...",
    },
    # スペイン語
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
        "ERROR_UNKNOWN_OCCURRED": "Ocurrió un error desconocido.",
        "ERROR_GOOGLETTS_FFMPEG_NOT_FOUND": "Para usar Google Text-to-Speech, necesitas instalar FFmpeg previamente.\n\nPor favor, instala FFmpeg y asegúrate de que se haya agregado a la ruta del sistema.",
        "SUMMARIZE_PROMPT": textwrap.dedent("""\
            Por favor, resume la siguiente conversación de chat de manera clara y concisa.

            [Formato de Salida]
            - Título (h2): Expresa brevemente el tema de la conversación
            - Género (h3): Clasifica la conversación en una palabra
            - Puntos Clave (h3): Viñetas
            - Resumen (h3): Una conclusión o decisión concisa derivada de la conversación

            [Restricciones]
            - Salida en formato Markdown
            - Resalta las palabras clave importantes con **
            - Muestra los términos técnicos en estilo `código`

            ---
            """),
        "GENERATING_RESPONSE": "Generando respuesta...",
    },
    # ドイツ語
    "de": {
        "ERROR_MISSING_OPENAI_API_KEY": "Die Umgebungsvariable OPENAI_API_KEY ist nicht gesetzt.",
        "ERROR_MISSING_AZURE_OPENAI_ENDPOINT": "Die Umgebungsvariable AZURE_OPENAI_ENDPOINT ist nicht gesetzt.",
        "ERROR_MISSING_AZURE_OPENAI_API_KEY": "Die Umgebungsvariable AZURE_OPENAI_API_KEY ist nicht gesetzt.",
        "ERROR_MISSING_GEMINI_API_KEY": "Die Umgebungsvariable GEMINI_API_KEY ist nicht gesetzt.",
        "ERROR_MISSING_ANTHROPIC_API_KEY": "Die Umgebungsvariable ANTHROPIC_API_KEY ist nicht gesetzt.",
        "ERROR_API_ID_IS_INCORRECT": "Die API-ID ist falsch.",
        "ERROR_API_TIMEOUT": "Der API-Aufruf ist abgelaufen.",
        "ERROR_API_AUTHENTICATION_FAILED": "Die API-Authentifizierung ist fehlgeschlagen.",
        "ERROR_API_ENDPOINT_INCORRECT": "Der API-Endpunkt ist falsch.",
        "ERROR_CONVERSATION_CONTENT_INAPPROPRIATE": "Der Inhalt des Gesprächs wurde als unangemessen eingestuft.",
        "ERROR_RATE_LIMIT_REACHED": "Das Ratelimit wurde erreicht.",
        "ERROR_API_ERROR_OCCURRED": "Ein API-Fehler ist aufgetreten.",
        "ERROR_UNKNOWN_OCCURRED": "Ein unbekannter Fehler ist aufgetreten.",
        "ERROR_GOOGLETTS_FFMPEG_NOT_FOUND": "Um Google Text-to-Speech zu verwenden, musst du vorher FFmpeg installieren.\n\nBitte installiere FFmpeg und stelle sicher, dass es zum Systempfad hinzugefügt wurde.",
        "SUMMARIZE_PROMPT": textwrap.dedent("""\
            Bitte fassen Sie das folgende Chat-Gespräch klar und präzise zusammen.

            [Ausgabeformat]
            - Titel (h2): Drücken Sie das Thema des Gesprächs kurz aus
            - Genre (h3): Klassifizieren Sie das Gespräch in einem Wort
            - Hauptpunkte (h3): Aufzählungspunkte
            - Zusammenfassung (h3): Eine prägnante Schlussfolgerung oder Entscheidung aus dem Gespräch

            [Einschränkungen]
            - Ausgabe im Markdown-Format
            - Wichtige Schlüsselwörter mit ** hervorheben
            - Technische Begriffe im `Code-Stil` anzeigen

            ---
            """),
        "GENERATING_RESPONSE": "Antwort wird erstellt...",
    },
    # フランス語
    "fr": {
        "ERROR_MISSING_OPENAI_API_KEY": "La variable d'environnement OPENAI_API_KEY n'est pas définie.",
        "ERROR_MISSING_AZURE_OPENAI_ENDPOINT": "La variable d'environnement AZURE_OPENAI_ENDPOINT n'est pas définie.",
        "ERROR_MISSING_AZURE_OPENAI_API_KEY": "La variable d'environnement AZURE_OPENAI_API_KEY n'est pas définie.",
        "ERROR_MISSING_GEMINI_API_KEY": "La variable d'environnement GEMINI_API_KEY n'est pas définie.",
        "ERROR_MISSING_ANTHROPIC_API_KEY": "La variable d'environnement ANTHROPIC_API_KEY n'est pas définie.",
        "ERROR_API_ID_IS_INCORRECT": "L'ID de l'API est incorrect.",
        "ERROR_API_TIMEOUT": "L'appel API a expiré.",
        "ERROR_API_AUTHENTICATION_FAILED": "L'authentification de l'API a échoué.",
        "ERROR_API_ENDPOINT_INCORRECT": "Le point de terminaison de l'API est incorrect.",
        "ERROR_CONVERSATION_CONTENT_INAPPROPRIATE": "Le contenu de la conversation a été jugé inapproprié.",
        "ERROR_RATE_LIMIT_REACHED": "Limite de débit atteinte.",
        "ERROR_API_ERROR_OCCURRED": "Une erreur API s'est produite.",
        "ERROR_UNKNOWN_OCCURRED": "Une erreur inconnue s'est produite.",
        "ERROR_GOOGLETTS_FFMPEG_NOT_FOUND": "Pour utiliser Google Text-to-Speech, vous devez d'abord installer FFmpeg.\n\nVeuillez installer FFmpeg et vous assurer qu'il est ajouté au chemin système.",
        "SUMMARIZE_PROMPT": textwrap.dedent("""\
            Veuillez résumer clairement et de manière concise la conversation de chat suivante.

            [Format de sortie]
            - Titre (h2) : Exprimer brièvement le sujet de la conversation
            - Genre (h3) : Classifier la conversation en un mot
            - Points clés (h3) : Puces
            - Résumé (h3) : Une conclusion concise ou un point de décision de la conversation

            [Contraintes]
            - Sortie au format Markdown
            - Mettre en évidence les mots-clés importants avec **
            - Afficher les termes techniques en `style de code`

            ---
            """),
        "GENERATING_RESPONSE": "Génération de la réponse...",
    },
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
def get_text_resource(key, lang=None):
    language = current_language
    if lang is not None and lang in text_resources:
        language = lang

    return text_resources.get(language, {}).get(key, key)
