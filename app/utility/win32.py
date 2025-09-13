# ZundaGPT2 / ZundaGPT2 Lite
#
# Win32 API ユーティリティ
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
    ]

# prototypes
user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
user32.MonitorFromWindow.restype  = wintypes.HMONITOR
user32.MonitorFromPoint.argtypes  = [wintypes.POINT, wintypes.DWORD]
user32.MonitorFromPoint.restype   = wintypes.HMONITOR
user32.GetMonitorInfoW.argtypes   = [wintypes.HMONITOR, ctypes.POINTER(MONITORINFO)]
user32.GetMonitorInfoW.restype    = wintypes.BOOL
user32.GetWindowRect.argtypes     = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.GetWindowRect.restype      = wintypes.BOOL

def _to_hwnd(handle_obj) -> wintypes.HWND:
    # pywebview.window.native.Handle は System.IntPtr
    try:
        val = handle_obj.ToInt64()
    except AttributeError:
        try:
            val = handle_obj.ToInt32()
        except AttributeError:
            val = int(handle_obj)
    return wintypes.HWND(val)

# ウィンドウが載っているモニタの物理サイズ（または作業領域）を返す
def get_monitor_size_for_window(native_handle, use_work_area: bool = False) -> tuple[int, int]:
    hwnd = _to_hwnd(native_handle) if native_handle else None
    MONITOR_DEFAULTTOPRIMARY = 1
    if hwnd:
        hmon = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTOPRIMARY)
    else:
        # hwndが無い時は原点(0,0)のモニタ（=プライマリ）
        pt = wintypes.POINT(0, 0)
        hmon = user32.MonitorFromPoint(pt, MONITOR_DEFAULTTOPRIMARY)

    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)
    if not user32.GetMonitorInfoW(hmon, ctypes.byref(mi)):
        # フォールバック：システム全体
        sw = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        sh = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        return sw, sh

    rc = mi.rcWork if use_work_area else mi.rcMonitor
    return rc.right - rc.left, rc.bottom - rc.top

# ウィンドウの外枠込みの矩形サイズを返す
def get_window_rect(native_handle) -> tuple[int, int]:
    hwnd = _to_hwnd(native_handle)
    rc = RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rc)):
        raise ctypes.WinError()
    return rc.right - rc.left, rc.bottom - rc.top
