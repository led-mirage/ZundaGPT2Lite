import { setFontFamilyAndSize, setCopyright, showBody, setClickEventHandler } from "./util.js";
import { setCurrentLanguage, getTextResource } from "./text-resources.js";

let g_searchText = "";
let g_foundCount = 0;
let g_searchResults = [];

// 初期化
document.addEventListener("DOMContentLoaded", function() {
    setClickEventHandler("search-button", startSearch);
    setClickEventHandler("close-button", closeWindow);

    const input = document.getElementById("search-query");
    input.addEventListener("keydown", handleEnterKey);
});

// pywebviewの初期化完了
window.addEventListener("pywebviewready", async function() {
    try {
        const appConfig = await pywebview.api.get_app_config_js();
        initUIComponents(appConfig);

        const response = await pywebview.api.get_cross_search_results();
        const data = JSON.parse(response);
        g_searchText = data.search_text;
        const searchResults = data.results;
        searchResults.forEach(item => {
            const [logfile, messageIndex, matchContext] = item;
            appendSearchResult(g_searchText, logfile, messageIndex, matchContext);
        });
        if (searchResults.length > 0) {
            displaySearchResults(searchResults.length);
        }
    }
    catch (error) {
        console.error("Error: " + error)
    }
})

// UIコンポーネントの初期化
function initUIComponents(appConfig) {
    setCurrentLanguage(appConfig.language);
    setFontFamilyAndSize(appConfig.fontFamily, appConfig.fontSize);
    setCopyright(appConfig.copyright);

    let elm = document.getElementById("title");
    if (elm) {
        elm.textContent = getTextResource("crossFileSearchTitle");
    }

    elm = document.getElementById("search-query");
    if (elm) {
        elm.placeholder = getTextResource("searchPlaceHolder");
    }

    elm = document.getElementById("close-button");
    if (elm) {
        elm.textContent = getTextResource("closeButton");
    }

    elm = document.getElementById("column-result");
    if (elm) {
        elm.textContent = getTextResource("crossFileSearchColumnResult");
    }

    elm = document.getElementById("column-logfile");
    if (elm) {
        elm.textContent = getTextResource("crossFileSearchColumnLogFile");
    }

    showBody();
}

// Enterキーで検索開始
function handleEnterKey(event) {
    if (event.key === "Enter") {
        document.getElementById("search-button").click();
    }
}

// 検索処理開始
function startSearch() {
    let searchText = document.getElementById("search-query").value;
    searchText = searchText.replace(/^\s+|\s+$/g, "");  // 前後の全角半角スペースを除去

    // 検索処理
    if (searchText) {
        try {
            g_searchText = searchText;
            g_foundCount = 0;
            g_searchResults = [];

            const tableBody = document.getElementById("resultTable").getElementsByTagName("tbody")[0];
            tableBody.innerHTML = "";

            pywebview.api.search_across_files(searchText);
        }
        catch (error) {
            console.error("Error: " + error);
        }
    }
}

// 進捗表示
function updateProgress(index, totalCount) {
    let progress = document.getElementById("progress-text");
    if (progress) {
        progress.textContent = `${index} / ${totalCount}`;
        if (index == totalCount) {
            displaySearchResults(g_searchResults.length);
        }
    }
}

// 検索結果の表示
function displaySearchResults(count) {
    let progress = document.getElementById("progress-text");
    const searchResult = getTextResource("searchResultsFound")
        .replace("${count}", count);
    progress.textContent = searchResult;
}

// 検索結果レコードの追加
function appendSearchResult(searchText, logfile, messageIndex, matchContext) {
    const entry = { logfile: logfile, messageIndex: messageIndex, matchContext: matchContext };
    g_searchResults.push(entry);

    appendResultRowToTable(searchText, logfile, messageIndex, matchContext);
}

// テーブルに検索結果を１行追加
function appendResultRowToTable(searchText, logfile, messageIndex, matchContext) {
    const tableBody = document.getElementById("resultTable").getElementsByTagName("tbody")[0];

    let newRow = tableBody.insertRow();
    let cell1 = newRow.insertCell(0);
    let cell2 = newRow.insertCell(1);

    // cell1: コメントアイコン＋テキスト
    const link = document.createElement("a");
    link.href = "javascript:void(0);";
    const index = g_foundCount;
    link.addEventListener("click", () => goToSelectedChat(index));

    const icon = document.createElement("i");
    icon.classList.add("fa-regular", "fa-comment");
    link.appendChild(icon);

    const matchSpan = document.createElement("span");
    matchSpan.className = "match-context";
    matchSpan.textContent = matchContext;

    cell1.appendChild(link);
    cell1.appendChild(document.createTextNode("　"));
    cell1.appendChild(matchSpan);

    // cell2: ファイル名
    const logSpan = document.createElement("span");
    logSpan.className = "log-filename";
    logSpan.textContent = logfile;
    cell2.appendChild(logSpan);

    var instance = new Mark(newRow);
    instance.mark(searchText);

    g_foundCount++;
}

// ユーザーが選んだチャットを表示する
function goToSelectedChat(index) {
    try {
        const logfile = g_searchResults[index].logfile;
        const messageIndex = g_searchResults[index].messageIndex;
        pywebview.api.move_to_chat_at(logfile, messageIndex, g_searchText);
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// クローズボタン押下イベント
async function closeWindow() {
    // Python側に通知
    try {
        await pywebview.api.close_cross_file_search();
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// Pythonから呼び出される関数（グローバルスコープに登録）
window.updateProgress = updateProgress;
window.appendSearchResult = appendSearchResult;
