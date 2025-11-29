// フォントファミリとサイズを設定する
export function setFontFamilyAndSize(fontFamily, fontSize) {
    if (fontFamily) {
        document.body.style.fontFamily = fontFamily;
    }

    document.documentElement.style.fontSize = fontSize + "px";
    document.body.style.fontSize = fontSize + "px";
};

// コピーライトを設定する
export function setCopyright(copyright) {
    const footer = document.getElementById("copyright");
    if (footer) {
        footer.textContent = copyright;
    }
};

// ボディを表示する
export function showBody() {
    document.body.style.display = "block";
}

// クリックイベントハンドラを登録する
export function setClickEventHandler(elementId, handler) {
    const element = document.getElementById(elementId);
    if (element) {
        element.addEventListener("click", handler);
    }
}

// フルスクリーンになったときにポップアップメッセージを表示する
export function showFullscreenMessage(elementId, message) {
    const div = document.getElementById(elementId);
    div.textContent = message;
    div.style.display = "block";
    div.style.opacity = 1;
    setTimeout(() => {
        div.style.opacity = 1;
    }, 10);

    setTimeout(() => {
        div.style.opacity = 0;
        setTimeout(() => {
            div.style.display = "none";
        }, 1000);
    }, 2000);
}
