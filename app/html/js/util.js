var util = util || {};  // namespace

// フォントファミリとサイズを設定する
util.setFontFamilyAndSize = function (fontFamily, fontSize) {
    if (fontFamily) {
        document.body.style.fontFamily = fontFamily;
    }

    document.documentElement.style.fontSize = fontSize + "px";
    document.body.style.fontSize = fontSize + "px";
};

// コピーライトを設定する
util.setCopyright = function (copyright) {
    const footer = document.getElementById("copyright");
    if (footer) {
        footer.textContent = copyright;
    }
};

// ボディを表示する
util.showBody = function () {
    document.body.style.display = "block";
}
