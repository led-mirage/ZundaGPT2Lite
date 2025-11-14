import { setFontFamilyAndSize, setCopyright, showBody, setClickEventHandler } from "./util.js";
import { setCurrentLanguage, getTextResource } from "./text-resources.js";

let g_selectedFilename = "";

// 初期化
document.addEventListener("DOMContentLoaded", function() {
    setClickEventHandler("refresh-button", refresh);
    setClickEventHandler("cancel-button", cancel);
    setClickEventHandler("submit-button", submit);
});

// pywebviewの初期化完了
window.addEventListener("pywebviewready", async function() {
    try {
        const appConfig = await pywebview.api.get_app_config_js();
        initUIComponents(appConfig);

        const settingFiles = await pywebview.api.get_settings_files();
        createSettingFilesUI(settingFiles);

        const elm = document.querySelector(`.selectable[filename="${g_selectedFilename}"]`);
        elm.scrollIntoView({ behavior: 'smooth' });
    }
    catch (error) {
        console.error("Error: " + error)
    }
})

// コンポーネントの初期化
function initUIComponents(appConfig) {
    if (appConfig.theme === "dark") {
        document.body.classList.add("dark-mode");
    }

    setCurrentLanguage(appConfig.language);
    setFontFamilyAndSize(appConfig.fontFamily, appConfig.fontSize);
    setCopyright(appConfig.copyright);

    let elm = document.getElementById("title");
    if (elm) {
        elm.textContent = getTextResource("settingsTitle");
    }

    elm = document.getElementById("cancel-button");
    if (elm) {
        elm.textContent = getTextResource("cancelButton");
    }

    elm = document.getElementById("submit-button");
    if (elm) {
        elm.textContent = getTextResource("okButton");
    }

    showBody();
}

// 設定ファイル選択用のUIを構築する
function createSettingFilesUI(settingFiles) {
    const groupContainer = document.getElementById("group-container");
    groupContainer.innerHTML = "";

    createDetails(groupContainer, settingFiles);
    setupSelectableEventHandler();
}

// 設定ファイル選択用のUIを構築する：details要素
function createDetails(groupContainer, settingFiles) {
    const groups = [...new Set(settingFiles.map(item => item.group))].sort((a, b) => {
        // 大文字小文字を区別せずに昇順ソート
        return a.localeCompare(b, undefined, { sensitivity: "base" });
    });
    //const groups = [... new Set(settingFiles.map(item => item.group))];
    groups.forEach(group => {
        const details = document.createElement("details");
        const summary = document.createElement("summary");
        summary.textContent = group;
        details.appendChild(summary);

        const settings = settingFiles.filter(item => item.group === group);
        createTable(details, settings);

        if (settings.some(item => item.current)) {
            details.setAttribute("open", "");
        }

        groupContainer.appendChild(details);
    });
}

// 設定ファイル選択用のUIを構築する：選択用のイベントハンドラの設定
function setupSelectableEventHandler() {
    document.querySelectorAll(".selectable").forEach(cell => {
        cell.addEventListener("click", function() {
            if (g_selectedFilename != "") {
                const elm = document.querySelector(`.selectable[filename="${g_selectedFilename}"]`)
                elm.textContent = "";
            }
            this.textContent = "✅";
            g_selectedFilename = this.getAttribute("filename");
        });
    });
}

// 設定ファイル選択用のUIを構築する：details毎のテーブル
function createTable(parent, settings) {
    const table = document.createElement("table");
    createTableHead(table);
    createTableBody(table, settings);
    parent.appendChild(table);
}

// 設定ファイル選択用のUIを構築する：テーブルヘッダ
function createTableHead(table) {
    const thead = document.createElement("thead");
    table.appendChild(thead);

    const row = thead.insertRow();
    const cell0 = document.createElement("th");
    const cell1 = document.createElement("th");
    const cell2 = document.createElement("th");
    row.appendChild(cell0);
    row.appendChild(cell1);
    row.appendChild(cell2);

    cell0.textContent = getTextResource("settingsColumnSelect");
    cell1.textContent = getTextResource("settingsColumnDisplayName");
    cell2.textContent = getTextResource("settingsColumnDescription");
}

// 設定ファイル選択用のUIを構築する：テーブルボディ
function createTableBody(table, settings) {
    const tbody = document.createElement("tbody");
    table.appendChild(tbody);

    settings.forEach(item => {
        const row = tbody.insertRow();
        row.appendChild(createSelectCell(item));
        row.appendChild(createNameCell(item));
        row.appendChild(createDetailCell(item));

        if (item.current) {
            g_selectedFilename = item.filename;
        }
    });
}

// 設定ファイル選択用のUIを構築する：テーブルボディのセル１列目
function createSelectCell(item) {
    const cell = document.createElement("td");
    cell.textContent = item.current ? "✅" : "";
    cell.classList.add("selectable");
    cell.setAttribute("filename", item.filename);
    return cell;
}

// 設定ファイル選択用のUIを構築する：テーブルボディのセル２列目
function createNameCell(item) {
    const cell = document.createElement("td");

    cell.appendChild(document.createTextNode(item.displayName));
    cell.appendChild(document.createElement("br"));

    const span = document.createElement("span");
    span.className = "remark";
    span.textContent = `${item.assistantName} x ${item.userName}`;
    cell.appendChild(span);

    return cell;
}

// 設定ファイル選択用のUIを構築する：テーブルボディのセル３列目
function createDetailCell(item) {
    const cell = document.createElement("td");

    // flexレイアウトで左:説明、右:削除ボタン に分ける
    const container = document.createElement("div");
    container.style.display = "flex";
    container.style.justifyContent = "space-between";
    container.style.alignItems = "center";
    container.style.gap = "8px";

    // 左側：説明＋リンク
    const infoDiv = document.createElement("div");
    infoDiv.style.flex = "1";

    const descSpan = document.createElement("span");
    descSpan.textContent = item.description;
    infoDiv.appendChild(descSpan);
    infoDiv.appendChild(document.createElement("br"));

    const span = document.createElement("span");
    span.className = "remark";
    span.textContent = `${item.api}　${item.model}　`;

    const link = document.createElement("a");
    link.href = "javascript:void(0);";
    link.textContent = item.filename;
    link.addEventListener("click", () => edit(item.filename));

    span.appendChild(link);
    infoDiv.appendChild(span);

    // 右側：ゴミ箱ボタン
    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "🗑️";
    deleteBtn.title = getTextResource("settingsDeleteButtonTooltip");
    deleteBtn.style.cursor = "pointer";
    deleteBtn.style.background = "transparent";
    deleteBtn.style.border = "none";
    deleteBtn.style.color = "inherit";
    deleteBtn.style.fontSize = "1rem";

    deleteBtn.addEventListener("click", async (event) => {
        event.stopPropagation();
        const confirmMessage = getTextResource("settingsDeleteConfirm")
            .replace("${filename}", item.filename);
        if (confirm(confirmMessage)) {
            try {
                await pywebview.api.delete_settings(item.filename);
                await refresh();
            } catch (error) {
                console.error("Error deleting settings: " + error);
                alert(getTextResource("settingsDeleteFailureMessage"));
            }
        }
    });

    container.appendChild(infoDiv);
    container.appendChild(deleteBtn);
    cell.appendChild(container);

    return cell;
}

// テーブルの更新
async function refresh() {
    // Python側に通知
    try {
        const settingFiles = await pywebview.api.get_settings_files();
        createSettingFilesUI(settingFiles);
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// 編集リンク押下イベント
async function edit(filename) {
    // Python側に通知
    try {
        await pywebview.api.edit_settings(filename);
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// OKボタン押下イベント
async function submit() {
    // Python側に通知
    try {
        await pywebview.api.submit_settings(g_selectedFilename);
    }
    catch (error) {
        console.error("Error: " + error)
    }
}

// キャンセルボタン押下イベント
async function cancel() {
    // Python側に通知
    try {
        await pywebview.api.cancel_settings();
    }
    catch (error) {
        console.error("Error: " + error)
    }
}
