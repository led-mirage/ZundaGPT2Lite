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
