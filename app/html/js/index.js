import { setFontFamilyAndSize, setCopyright, showBody, setClickEventHandler } from "./util.js";
import { setCurrentLanguage, getTextResource } from "./text-resources.js";

let g_userName = "あなた";
let g_userColor = "#007bff";
let g_userIcon = "";
let g_assistantName = "ずんだ";
let g_assistantColor = "#006400";
let g_assistantIcon = "";
let g_nextMessageIndex = 0;
let g_searchTextIndex = 0;
let g_searchTextTotal = 0;
let g_welcomeTitle = "";
let g_welcomeMessage = "";
let g_aiAgentAvailable = false;
let g_aiAgentCreationError = "";

// 初期化
document.addEventListener("DOMContentLoaded", function() {
    // ツールボタンのクリックイベントハンドラの登録
    setClickEventHandler("prev-button", prevChat);
    setClickEventHandler("next-button", nextChat);
    setClickEventHandler("new-button", newChat);
    setClickEventHandler("cross-search-button", crossFileSearch);
    setClickEventHandler("delete-button", deleteChat);
    setClickEventHandler("print-button", printDocument);
    setClickEventHandler("settings-button", settings);

    const textarea = document.getElementById("message");
    textarea.addEventListener("input", autoResize, false);

    const button = document.getElementById("submit-button");
    button.addEventListener("click", function() {
        submit();
        autoResize.call(textarea);
    }, false);

    document.getElementById("message").addEventListener("keydown", function(event) {
        // Enterが押されたが、Shiftが押されていない場合
        if (event.key === "Enter" && !event.shiftKey) {
            const button = document.getElementById("submit-button");
            if (button) {
                if (!button.classList.contains("submit-button-disabled")) {
                    event.preventDefault(); // デフォルトのEnterによる改行を防ぐ
                    submit(); // 送信処理を実行
                    autoResize.call(textarea);
                }
            }
        }
    });

    // キーダウンイベントハンドラの登録
    document.addEventListener("keydown", handleKeyDown);

    // コンテキストメニューイベントハンドラの登録
    document.addEventListener("contextmenu", handleContextMenu);

    autoResize.call(textarea);

    function autoResize() {
        this.style.height = "auto";
        this.style.height = this.scrollHeight - rem2px(2) + "px";
    }
});

// キーダウンイベントハンドラ
function handleKeyDown(event) {
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.keyCode === 70) { // Ctrl + Shift + F
        crossFileSearch();
    }
    else if ((event.ctrlKey || event.metaKey) && event.keyCode === 70) { // Ctrl + F
        searchText();
    }
    else if (event.keyCode == 27) { // ESC
        var instance = new Mark(document.body);
        g_searchTextIndex = g_searchTextTotal = 0;
        instance.unmark();
    }
    else if (event.keyCode == 114) { // F3
        if (g_searchTextTotal > 0) {
            if (event.shiftKey) {
                g_searchTextIndex--;
                if (g_searchTextIndex < 0) {
                    g_searchTextIndex = g_searchTextTotal - 1;
                }
            }
            else {
                g_searchTextIndex++;
                if (g_searchTextIndex >= g_searchTextTotal) {
                    g_searchTextIndex = 0;
                }
            }
            highlightSearchResult();
        }
    }
}

// コンテキストメニューイベントハンドラ
function handleContextMenu(event) {
    event.preventDefault();

    // 既に表示されているメニューがあれば消す
    const existingMenu = document.querySelector('.contextmenu');
    if (existingMenu) {
        document.body.removeChild(existingMenu);
    }

    let menuContent = "";
    menuContent += `<button id="copy"><i class="fa-regular fa-copy"></i> ${getTextResource("copyContextMenu")}</button><br>`;
    menuContent += `<button id="search"><i class="fa-solid fa-magnifying-glass"></i> ${getTextResource("searchContextMenu")}</button><br>`;
    menuContent += `<button id="summary"><i class="fa-solid fa-compress"></i> ${getTextResource("summaryContextMenu")}</button><br>`;

    const menu = document.createElement("div");
    menu.className = "contextmenu";
    menu.style.visibility = "hidden";
    menu.innerHTML = menuContent;
    document.body.appendChild(menu);
    const menuWidth = menu.offsetWidth;
    const menuHeight = menu.offsetHeight;
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    let xPos = event.pageX;
    let yPos = event.pageY;
    if (xPos + menuWidth > windowWidth) {
        xPos = windowWidth - menuWidth - 10;
    } 
    if (yPos + menuHeight > windowHeight) {
        yPos = windowHeight - menuHeight - 10;
    }
    menu.style.left = `${xPos}px`;
    menu.style.top = `${yPos}px`;
    menu.style.visibility = "visible";

    const copyButton = document.getElementById("copy");
    if (copyButton) {
        copyButton.addEventListener("click", async function(clickEvent) {
            const selectedText = window.getSelection().toString();
            if (selectedText) {
                document.body.removeChild(menu);
                //navigator.clipboard.writeText(selectedText);
                await pywebview.api.copytext_to_clipboard(selectedText);
                showToast(clickEvent, getTextResource("textCopiedMessage"));
            }
            else {
                copyChatAllMessages();
                showToast(clickEvent, getTextResource("allMessageCopiedMessage"));
            }
        });
    }

    const searchButton = document.getElementById("search");
    if (searchButton) {
        searchButton.addEventListener("click", function() {
            document.body.removeChild(menu);
            // 少しタイミングを遅らせないとメニューが消えない
            setTimeout(function() {
                const selectedText = window.getSelection().toString();
                searchText(selectedText);
            }, 100);
        });
    }

    const summaryButton = document.getElementById("summary");
    if (summaryButton) {
        summaryButton.addEventListener("click", function(clickEvent) {
            document.body.removeChild(menu);
            // 少しタイミングを遅らせないとメニューが消えない
            setTimeout(function() {
                summarizeChat(clickEvent);
            }, 100);
        });
    }

    // どこかクリックされたらコンテキストメニューを消す
    document.addEventListener("click", function() {
        if (document.body.contains(menu)) {
            document.body.removeChild(menu);
        }
    }, { once: true });
}

// remをpxに変換
function rem2px(rem) {
    var rootFontSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
    return rem * rootFontSize;
}

// IME対策
// IMEがONの状態かつフォーカスがテキストボックスにある状態で、
// 別のアプリを見るなどしてウィンドウのフォーカスが失われ再度戻ってきたときに、
// IMEの変換がテキストボックス内でできなくなる現象に対処
window.onfocus = function() {
    document.getElementById("message").blur();
}

// pywebviewの初期化完了
window.addEventListener("pywebviewready", async function() {
    try {
        const appConfig = await pywebview.api.get_app_config_js();
        initUIComponents(appConfig);

        await pywebview.api.page_loaded();

        if (document.querySelectorAll(".chat-message").length === 0) {
            addWelcome();
        }
    }
    catch (error) {
        console.error("Error: " + error)
    }
})

// コンポーネントの初期化
function initUIComponents(appConfig) {
    setCurrentLanguage(appConfig.language);
    setFontFamilyAndSize(appConfig.fontFamily, appConfig.fontSize);
    setCopyright(appConfig.copyright);

    let button = document.getElementById("submit-button");
    if (button) {
        button.textContent = getTextResource("submitButton");
    }

    button = document.getElementById("prev-button");
    if (button) {
        const tooltip = button.querySelector('.tooltiptext');
        if (tooltip) {
            tooltip.textContent = getTextResource("prevButtonTooltip");
        }
    }

    button = document.getElementById("next-button");
    if (button) {
        const tooltip = button.querySelector('.tooltiptext');
        if (tooltip) {
            tooltip.textContent = getTextResource("nextButtonTooltip");
        }
    }

    button = document.getElementById("new-button");
    if (button) {
        const tooltip = button.querySelector('.tooltiptext');
        if (tooltip) {
            tooltip.textContent = getTextResource("newButtonTooltip");
        }
    }

    button = document.getElementById("cross-search-button");
    if (button) {
        const tooltip = button.querySelector('.tooltiptext');
        if (tooltip) {
            tooltip.textContent = getTextResource("crossSearchButtonTooltip");
        }
    }

    button = document.getElementById("delete-button");
    if (button) {
        const tooltip = button.querySelector('.tooltiptext');
        if (tooltip) {
            tooltip.textContent = getTextResource("deleteButtonTooltip");
        }
    }

    button = document.getElementById("print-button");
    if (button) {
        const tooltip = button.querySelector('.tooltiptext');
        if (tooltip) {
            tooltip.textContent = getTextResource("printButtonTooltip");
        }
    }

    button = document.getElementById("settings-button");
    if (button) {
        const tooltip = button.querySelector('.tooltiptext');
        if (tooltip) {
            tooltip.textContent = getTextResource("settingsButtonTooltip");
        }
    }

    let textarea = document.getElementById("message");
    if (textarea) {
        textarea.placeholder = getTextResource("messagePlaceholder");
    }

    showBody();
}

// 送信ボタン押下時イベントハンドラ
function submit() {
    const button = document.getElementById("submit-button");
    if (button) {
        if (!button.classList.contains("submit-button-disabled")) {
            sendMessage();
        }
        else {
            stopSendMessage();
        }
    }
}

// メッセージを送信する
async function sendMessage() {
    if (!g_aiAgentAvailable) {
        alert(g_aiAgentCreationError);
        return;
    }

    const text = document.getElementById("message").value;
    if (text === "") return;

    setSubmitButtonState(true);

    // HTMLにメッセージを追加
    addChatMessage("user", g_userName, g_userColor, text)
    scrollToBottom();
    hideChatRetryButton();
    document.getElementById("message").value = "";

    // Python側に通知
    try {
        await pywebview.api.send_message_to_chatgpt(text);
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// メッセージを送信を中止する
async function stopSendMessage() {
    // Python側に通知
    try {
        await pywebview.api.stop_send_message_to_chatgpt();
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// 送信ボタンの状態を設定する
function setSubmitButtonState(isSending) {
    const button = document.getElementById("submit-button");
    if (button) {
        if (isSending) {
            button.textContent = getTextResource("stopButton");
            button.classList.add("submit-button-disabled")
        }
        else {
            button.textContent = getTextResource("submitButton");
            button.classList.remove("submit-button-disabled")
        }
    }
}

// チャットメッセージを下端までスクロールする
function scrollToBottom() {
    const messageContainer = document.querySelector(".chat-messages");
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

// 文字列をHTML用にエスケープする
function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#x27;")
        .replace(/\n/g, "<br>")
        .replace(/ /g, "&nbsp;")
        .replace(/\t/g, "&nbsp;&nbsp;&nbsp;&nbsp;");
}

// TeX用の文字列をエスケープする
function escapeTex(text) {
    return text.replace(/\\/g, "@@@@");
}

// TeX用にエスケープした文字列を元に戻す
function unescapeTex(text) {
    return text.replace(/@@@@/g, "\\");
}

// Welcomeメッセージの表示をON/OFFする
function showWelcome(show) {
    const welcome = document.getElementById("welcome");
    if (welcome) {
        if (show) {
            welcome.style.display = "flex";
        }
        else {
            welcome.style.display = "none";
        }
    }
}

// Welcomeメッセージブロックを追加する
function addWelcome() {
    // チャットメッセージコンテナを取得
    const chatMessagesContainer = document.getElementById("chat-messages");

    // Welcomeコンテナを作成
    const welcomeConainer = document.createElement("div");
    welcomeConainer.id = "welcome";
    welcomeConainer.classList.add("welcome");
    chatMessagesContainer.appendChild(welcomeConainer);

    // アシスタントアイコンを作成
    if (g_assistantIcon != "") {
        const imgElement = document.createElement("img");
        imgElement.classList.add("welcome-chat-icon");
        imgElement.src = `data:image/png;base64,${g_assistantIcon}`;
        welcomeConainer.appendChild(imgElement);
    }

    // Welcomeタイトルを作成
    const welcomeTitle = document.createElement("div");
    welcomeTitle.id = "welcome-title";
    welcomeTitle.classList.add("welcome-title");
    welcomeTitle.textContent = g_welcomeTitle;
    welcomeConainer.appendChild(welcomeTitle);

    // Welcomeメッセージを作成
    const welcomeMessage = document.createElement("div");
    welcomeMessage.id = "welcome-message";
    welcomeMessage.classList.add("welcome-message");
    welcomeMessage.textContent = g_welcomeMessage;
    welcomeConainer.appendChild(welcomeMessage);
}

// チャットメッセージブロックを追加する
function addChatMessage(role, speakerName, color, messageText) {
    // Welcomeメッセージの非表示
    showWelcome(false);

    // チャットメッセージコンテナを取得
    const chatMessagesContainer = document.getElementById("chat-messages");

    // 新しいチャットメッセージ要素を作成
    const chatMessageElement = document.createElement("div");
    chatMessageElement.classList.add("chat-message");
    chatMessageElement.id = "message-" + g_nextMessageIndex++;

    // 発言者名を表示する要素を作成
    const speakerElement = document.createElement("div");
    speakerElement.classList.add("speaker-name");
    speakerElement.style.color = color;
    speakerElement.textContent = speakerName;

    if (role === "user") {
        if (g_userIcon != "") {
            // ユーザーアイコンをつける
            const imgElement = document.createElement("img");
            imgElement.classList.add("chat-icon");
            imgElement.src = `data:image/png;base64,${g_userIcon}`;
            speakerElement.prepend(imgElement);
        }
    }
    else if (role === "assistant") {
        if (g_assistantIcon != "") {
            // アシスタントアイコンをつける
            const imgElement = document.createElement("img");
            imgElement.classList.add("chat-icon");
            imgElement.src = `data:image/png;base64,${g_assistantIcon}`;
            speakerElement.prepend(imgElement);
        }
    }

    // コピーボタンをつける
    const copyElement = document.createElement("button");
    copyElement.classList.add("message-copy-btn");
    copyElement.innerHTML = "<i class='fa-regular fa-copy'></i>";
    copyElement.addEventListener("click", copyChatMessage);
    speakerElement.appendChild(copyElement);

    if (role === "user") {
        // 削除ボタンをつける
        const deleteElement = document.createElement("button");
        deleteElement.classList.add("message-delete-btn");
        deleteElement.innerHTML = "<i class='fa-regular fa-trash-can'></i>";
        deleteElement.addEventListener("click", deleteChatMessage);
        speakerElement.appendChild(deleteElement);
    }
    else {
        // 再回答ボタンをつける
        if (g_aiAgentAvailable) {
            const retryElement = document.createElement("button");
            retryElement.classList.add("chat-reanswer-btn");
            retryElement.innerHTML = "<i class='fa-solid fa-rotate'></i>";
            retryElement.style.display = "none";
            retryElement.addEventListener("click", reAnswerChat);
            speakerElement.appendChild(retryElement);
        }
    }

    // メッセージテキストを表示する要素を作成
    const messageElement = document.createElement("div");
    messageElement.classList.add("message-text");
    if (role === "assistant") {
        let html = convertTextToHtmlWithMarkdown(messageText);
        html = escapeTex(html);
        html = adjustURL(html);
        html = marked.parse(html);
        html = unescapeTex(html);
        messageElement.innerHTML = html;
        messageElement.querySelectorAll("pre code").forEach((block) => {
            hljs.highlightElement(block);
        });
        addTargetBlank(messageElement);
    }
    else {
        messageElement.classList.add("mathjax_ignore");
        messageElement.innerHTML = escapeHtml(messageText);
    }

    // コードブロックにコピー用ボタンを追加
    addCopyToClipboardButton(messageElement);

    // チャットメッセージ要素に発言者名とメッセージテキストの要素を追加
    chatMessageElement.appendChild(speakerElement);
    chatMessageElement.appendChild(messageElement);

    // 作成したチャットメッセージをコンテナに追加
    chatMessagesContainer.appendChild(chatMessageElement);
}

// チャットメッセージのコードブロックにコピー用ボタンを追加する
function addCopyToClipboardButton(element) {
    element.querySelectorAll("pre").forEach((block) => {
        const button = document.createElement("button");
        button.innerHTML = "<i class='fa-regular fa-copy'></i>";
        button.className = "copy-button";

        const toast = document.createElement("div");
        toast.className = "code-toast";
        toast.textContent = getTextResource("textCopiedMessage");
        button.appendChild(toast);

        button.addEventListener("click", async () => {
            const code = block.querySelector("code");
            //await navigator.clipboard.writeText(code.textContent);
            await pywebview.api.copytext_to_clipboard(code.textContent);
            showCodeToast(toast);
        });

        block.appendChild(button);
    });    
}

// コードをクリップボードにコピーしたときのトーストを表示する
function showCodeToast(toast) {
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

// マークダウンテキスト内のコードブロックを保護しながらHTML変換する関数
function convertTextToHtmlWithMarkdown(text) {
    // コードブロックを一時保存
    let codeBlocks = [];
    text = text.replace(/```[\s\S]*?```/g, match => {
        codeBlocks.push(match);
        return `__CODE_BLOCK_${codeBlocks.length-1}__`;
    });

    // バッククォート文字を変換
    text = text.replace(/\\`/g, '\\\''); 

    // コードブロックを戻す
    codeBlocks.forEach((block, i) => {
        text = text.replace(`__CODE_BLOCK_${i}__`, block);
    });

    return text;
}

// markedがリンクに連続する文字列全体をリンクに変換してしまう問題に対処
function adjustURL(text) {
    // コードブロックを一時保存
    let codeBlocks = [];
    text = text.replace(/```[\s\S]*?```/g, match => {
        codeBlocks.push(match);
        return `__CODE_BLOCK_${codeBlocks.length-1}__`;
    });

    // https://またはhttp://では始まらない、www.で始まるドメイン名の前後にバッククォートを入れる
    text = text.replace(/(?<!https?:\/\/)(www\.[\w.]+)/g, " `$1` ");
    // https://またはhttp://で始まるURLの前後に半角スペースをいれる
    text = text.replace(/(https?:\/\/[\w.?=&%+#\/\-]+)/g, ' $1 ');

    // コードブロックを戻す
    codeBlocks.forEach((block, i) => {
        text = text.replace(`__CODE_BLOCK_${i}__`, block);
    });

    return text;
}

// 要素中の<a>タグにtarget="_blank"を設定する
function addTargetBlank(targetElement) {
    const links = targetElement.getElementsByTagName("a");
    for (let i = 0; i < links.length; i++) {
        if (!links[i].hasAttribute("target")) {
            links[i].setAttribute("target", "_blank");
            links[i].setAttribute("title", links[i].getAttribute("href"));
        }
    }
}

// 新規チャット開始
async function newChat() {
    // チャット要素を削除
    document.getElementById("chat-messages").innerHTML = "";

    // Python側に通知
    try {
        await pywebview.api.new_chat();
        addWelcome();
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// ひとつ前のチャットに移動する
async function prevChat() {
    try {
        await pywebview.api.prev_chat();
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// ひとつ後のチャットに移動する
async function nextChat() {
    try {
        await pywebview.api.next_chat();
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// 現在表示しているチャットを削除する
async function deleteChat() {
    const messageTextElements = document.querySelectorAll("#chat-messages .message-text");
    if (messageTextElements.length === 0) return;

    if (!confirm(getTextResource("deleteConfirm"))) return;

    try {
        await pywebview.api.delete_current_chat();
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// 設定ボタンが押された
async function settings() {
    try {
        await pywebview.api.move_to_settings();
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// 印刷イベントハンドラ
function printDocument() {
    window.print();
}

// テキストを検索する
function searchText(query = "") {
    const searchText = prompt(getTextResource("searchPrompt"), query);
    if (searchText) {
        g_searchTextIndex = 0;
        var instance = new Mark(document.body);
        instance.unmark();
        instance.mark(searchText, {
            each: function(element) {
                // この中の処理は、見つかった各検索結果に対して実行される
            },
            done: function(totalMarks) {
                // 検索が完了した後に実行される処理
                g_searchTextTotal = totalMarks;
                highlightSearchResult(250);
            }
        });
    }
}

// テキスト検索で見つかったテキストのハイライト処理を行う
function highlightSearchResult(delay=0) {
    document.querySelectorAll("mark").forEach((element, index) => {
        if (index === g_searchTextIndex) {
            element.style.color = "red";
            element.style.backgroundColor = ""
            element.scrollIntoView({ behavior: "smooth" });
            setTimeout(() => {
                element.scrollIntoView({ behavior: "smooth" });
            }, delay);
        }
        else {
            element.style.color = "";
            element.style.backgroundColor = "khaki"
        }
    });    
}

// ファイル横断検索機能のエントリポイント
async function crossFileSearch() {
    try {
        await pywebview.api.move_to_cross_file_search();
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// メッセージの削除ボタンが押された
async function deleteChatMessage(event) {
    if (!confirm(getTextResource("deleteFromHereConfirm"))) return;

    hideChatRetryButton();

    let messageDiv = event.target.closest(".chat-message");
    let messageId = messageDiv.id;
    let messageIndex = parseInt(messageId.split("-")[1], 10);

    try {
        await pywebview.api.truncate_messages(messageIndex);
        g_nextMessageIndex = messageIndex;
        while (messageDiv.nextSibling) {
            messageDiv.nextSibling.remove();
        }
        messageDiv.remove();
    }
    catch (error) {
        console.error("Error: " + error)
    }

    showChatRetryButton();
}

// チャットの再回答ボタンが押された
async function reAnswerChat(event) {
    setSubmitButtonState(true);
    let messageDiv = event.target.closest(".chat-message");
    let messageId = messageDiv.id;
    let messageIndex = parseInt(messageId.split("-")[1], 10);
    messageDiv.remove();

    try {
        g_nextMessageIndex = messageIndex;
        await pywebview.api.ask_another_reply_to_chatgpt(messageIndex);
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// チャットの全メッセージのコピーイベントハンドラ
async function copyChatAllMessages() {
    try {
        const chatText = await pywebview.api.get_all_message_text();
        //navigator.clipboard.writeText(chatText);
        await pywebview.api.copytext_to_clipboard(chatText);
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// メッセージのコピーボタンが押された
async function copyChatMessage(event) {
    const button = event.currentTarget;

    let messageDiv = event.target.closest(".chat-message");
    let messageId = messageDiv.id;
    let messageIndex = parseInt(messageId.split("-")[1], 10);

    try {
        const messageText = await pywebview.api.get_message_text(messageIndex);
        //await navigator.clipboard.writeText(messageText);
        await pywebview.api.copytext_to_clipboard(messageText);
        showToast(event, getTextResource("messageCopiedMessage"));
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// チャットを要約する
async function summarizeChat(event) {
    try {
        showProgressModal(getTextResource("summarizingProgressMessage"));
        const summary = await pywebview.api.summarize_chat();
        hideProgressModal();

        if (summary) {
            //await navigator.clipboard.writeText(summary);
            await pywebview.api.copytext_to_clipboard(summary);
            showToast(event, getTextResource("summaryCopiedMessage"), ToastPosition.CenterScreen);
            showSummaryModal(summary);
        }
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// 要約モーダルを表示する
function showSummaryModal(summary) {
    const modal = document.getElementById("summary-modal");
    const content = document.getElementById("summary-modal-content");
    const closeButton = document.getElementById("summary-modal-close-button");

    if (modal && content && closeButton) {
        content.innerHTML = marked.parse(summary);
        closeButton.addEventListener("click", function() {
            hideSummaryModal();
        });
        modal.style.display = "block";
    }
}

// 要約モーダルを非表示にする
function hideSummaryModal() {
    const modal = document.getElementById("summary-modal");
    if (modal) {
        modal.style.display = "none";
    }
}

// トーストの表示位置
const ToastPosition = {
    ClickPos: "click-pos",
    CenterScreen: "center-screen"
};

// トーストを表示する
function showToast(event, message, position = ToastPosition.ClickPos, duration = 2000) {
    // トースト要素を作成
    const toast = document.createElement("div");
    toast.classList.add("toast");
    toast.textContent = message;

    // トーストをbodyに追加
    document.body.appendChild(toast);
    
    if (position === ToastPosition.ClickPos) {
        // クリック位置の右側に配置
        toast.style.left = `${Math.min(window.innerWidth - toast.offsetWidth, event.pageX + 16)}px`;
        toast.style.top = `${Math.min(window.innerHeight - toast.offsetHeight, event.pageY)}px`;
    }
    else {
        // デフォルトで画面中央に配置
        toast.style.left = `${(window.innerWidth - toast.offsetWidth) / 2}px`;
        toast.style.top = `${(window.innerHeight - toast.offsetHeight) / 2}px`;
    }
    
    // 2秒後に消える
    setTimeout(() => {
        toast.remove();
    }, duration);        
}

// Pythonから呼び出される関数
// 情報をセットする
function setChatInfo(
    displayName, userName, userColor, userIcon,
    assistantName, assistantColor, assistantIcon,
    welcomeTitle, welcomeMessage, aiAgentAvailable, aiAgentCreationError
) {
    g_userName = userName;
    g_userColor = userColor;
    g_userIcon = userIcon;
    g_assistantName = assistantName;
    g_assistantColor = assistantColor;
    g_assistantIcon = assistantIcon;
    g_nextMessageIndex = 0;
    g_welcomeTitle = welcomeTitle;
    g_welcomeMessage = welcomeMessage;
    g_aiAgentAvailable = aiAgentAvailable;
    g_aiAgentCreationError = aiAgentCreationError;

    if (displayName === "") {
        displayName = assistantName;
    }
    document.getElementById("settings-name").textContent = displayName;
}

// Pythonから呼び出される関数
// AIからのチャット応答を開始する
function startResponse() {
    addChatMessage("assistant", g_assistantName, g_assistantColor, "");
    scrollToBottom();

    // アシスタント名のテキストを点滅させる
    const nameTextElements = document.querySelectorAll("#chat-messages .speaker-name");
    const lastNameTextElements = nameTextElements[nameTextElements.length - 1];
    if(lastNameTextElements) {
        lastNameTextElements.classList.add("flowing-text");
    }

    // 出力途中のテキストを表示するエリアを作成する
    const messageTextElements = document.querySelectorAll("#chat-messages .message-text");
    const lastMessageTextElement = messageTextElements[messageTextElements.length - 1];
    if(lastMessageTextElement) {
        const chunkArea = document.createElement("span");
        chunkArea.setAttribute("chunk-area", "true");
        lastMessageTextElement.appendChild(chunkArea);
    }
}

// Pythonから呼び出される関数
// AIからの応答（チャンク）を表示する
function addChunk(text) {
    const elms = document.querySelectorAll('[chunk-area="true"]');
    const chunkArea = elms[elms.length - 1];
    if (chunkArea) {
        chunkArea.innerHTML += escapeHtml(text);
        scrollToBottom();        
    }
}

// Pythonから呼び出される関数
// センテンスの読み上げが終わったときに呼び出される
function parsedSentence(sentence) {
    //MathJax.typesetPromise();
}

// Pythonから呼び出される関数
// 段落を受信したときに呼び出される
function parsedParagraph(paragraph) {
    const messageTextElements = document.querySelectorAll("#chat-messages .message-text");
    const lastMessageTextElement = messageTextElements[messageTextElements.length - 1];

    // チャンク出力領域を削除
    document.querySelectorAll('[chunk-area="true"]').forEach(e => e.remove());

    // 仮レンダリングして表示
    let html = marked.parse(paragraph);
    lastMessageTextElement.innerHTML += html;

    // チャンク出力領域を末尾に再作成
    const chunkArea = document.createElement("span");
    chunkArea.setAttribute("chunk-area", "true");
    lastMessageTextElement.appendChild(chunkArea);
}

// Pythonから呼び出される関数
// AIからのチャット応答が終了した
function endResponse(content) {
    setSubmitButtonState(false);
    showChatRetryButton();

    // アシスタント名の点滅を停止させる
    const nameTextElements = document.querySelectorAll("#chat-messages .speaker-name");
    const lastNameTextElements = nameTextElements[nameTextElements.length - 1];
    if(lastNameTextElements) {
        lastNameTextElements.classList.remove("flowing-text");
    }

    // チャンク出力領域を削除
    document.querySelectorAll('[chunk-area="true"]').forEach(e => e.remove());

    // コンテンツの内容をレンダリングして確定する
    const messageTextElements = document.querySelectorAll("#chat-messages .message-text");
    const lastMessageTextElement = messageTextElements[messageTextElements.length - 1];
    if(lastMessageTextElement) {
        let html = convertTextToHtmlWithMarkdown(content);
        html = escapeTex(html);
        html = adjustURL(html);
        html = marked.parse(html);
        html = unescapeTex(html);
        lastMessageTextElement.innerHTML = html;
        lastMessageTextElement.querySelectorAll("pre code").forEach((block) => {
            hljs.highlightElement(block);
        });
        addTargetBlank(lastMessageTextElement);
        addCopyToClipboardButton(lastMessageTextElement);
    }

    MathJax.typesetPromise();
}

// Pythonから呼び出される関数
// チャット応答で例外が発生した
function handleChatException(message) {
    alert(message);
    endResponse();
}

// Pythonから呼び出される関数
// チャット応答で例外が発生した
async function handleChatTimeoutException(message) {
    if (confirm(`${message}\n` + getTextResource("retryConfirm"))) {
        const messageTextElements = document.querySelectorAll("#chat-messages .message-text");
        const lastMessageTextElement = messageTextElements[messageTextElements.length - 1];
        if (lastMessageTextElement) {
            lastMessageTextElement.textContent = "";
        }

        // Python側に通知
        try {
            await pywebview.api.retry_send_message_to_chatgpt();
        }
        catch (error) {
            console.error("Error: " + error)
        }
    }
    else {
        endResponse()
    }
}

// Pythonから呼び出される関数
// チャットのメッセージを再設定する
function setChatMessages(messages) {
    console.log(messages);
    document.getElementById("chat-messages").innerHTML = "";
    for (let message of messages) {
        let speakerName = "";
        let speakerColor = "";
        if (message.role === "assistant") {
            speakerName = g_assistantName;
            speakerColor = g_assistantColor;
        }
        else {
            speakerName = g_userName;
            speakerColor = g_userColor;
        }
        addChatMessage(message.role, speakerName, speakerColor, message.content);
    }
    MathJax.typesetPromise();
    scrollToBottom();
    showChatRetryButton();
}

// Pythonから呼び出される関数
// 指定されたメッセージに移動する
function moveToMessageAt(messageIndex, highlightText) {
    const element = document.getElementById(`message-${messageIndex}`);
    if (element) {
        element.scrollIntoView({ behavior: "smooth" });
        var instance = new Mark(document.body);
        instance.mark(highlightText);
    }
}

// 再回答ボタンをすべて非表示にする
function hideChatRetryButton() {
    const buttons = document.querySelectorAll(".chat-reanswer-btn");
    buttons.forEach((button, index) => {
        button.style.display = "none";
    });    
}

// 最後の再回答ボタンだけ表示する
function showChatRetryButton() {
    const buttons = document.querySelectorAll(".chat-reanswer-btn");
    buttons.forEach((button, index) => {
        if (index === buttons.length - 1) {
            button.style.display = "inline";
        }
    });
}

// 処理中モーダルを表示する
function showProgressModal(message) {
    const modal = document.getElementById("progress-modal");
    const messageEl = document.getElementById("progress-modal-message");
    messageEl.textContent = message;
    modal.style.display = "block";
}

// 処理中モーダルを非表示にする
function hideProgressModal() {
    const modal = document.getElementById("progress-modal");
    modal.style.display = "none";
}

// Pythonから呼び出される関数（グローバルスコープに登録）
window.setChatInfo = setChatInfo;
window.startResponse = startResponse;
window.addChunk = addChunk;
window.parsedSentence = parsedSentence;
window.parsedParagraph = parsedParagraph;
window.endResponse = endResponse;
window.handleChatException = handleChatException;
window.handleChatTimeoutException = handleChatTimeoutException;
window.setChatMessages = setChatMessages;
window.moveToMessageAt = moveToMessageAt;
window.newChat = newChat;
