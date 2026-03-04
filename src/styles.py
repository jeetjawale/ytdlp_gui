"""Dark theme stylesheet for the YT-DLP GUI application."""

DARK_THEME = """
/* ============================
   Global
   ============================ */
QMainWindow {
    background-color: #0f172a;
}

QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}

QToolTip {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #475569;
    border-radius: 4px;
    padding: 4px 8px;
}

/* ============================
   URL Input Section
   ============================ */
#urlInput {
    background-color: #1e293b;
    border: 2px solid #334155;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    color: #e2e8f0;
    selection-background-color: #6366f1;
}

#urlInput:focus {
    border-color: #6366f1;
}

#urlInput:hover {
    border-color: #475569;
}

#pasteBtn {
    background-color: #1e293b;
    border: 2px solid #334155;
    border-radius: 8px;
    padding: 8px;
    font-size: 16px;
}

#pasteBtn:hover {
    background-color: #334155;
    border-color: #475569;
}

#fetchBtn {
    background-color: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: bold;
    font-size: 13px;
}

#fetchBtn:hover {
    background-color: #818cf8;
}

#fetchBtn:pressed {
    background-color: #4f46e5;
}

#fetchBtn:disabled {
    background-color: #475569;
    color: #94a3b8;
}

/* ============================
   Video Info Card
   ============================ */
#infoCard {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
}

#videoTitle {
    font-size: 16px;
    font-weight: bold;
    color: #f1f5f9;
}

#videoDetails {
    font-size: 12px;
    color: #94a3b8;
}

#thumbnail {
    background-color: #0f172a;
    border-radius: 6px;
    border: 1px solid #334155;
    color: #64748b;
    font-size: 11px;
}

#typeBadge, #typeBadgePlaylist {
    border-radius: 4px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: bold;
}

/* ============================
   Format Panel
   ============================ */
#formatPanel {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
}

QComboBox {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 30px 6px 10px;
    min-width: 110px;
    color: #e2e8f0;
}

QComboBox:hover {
    border-color: #6366f1;
}

QComboBox:focus {
    border-color: #6366f1;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #94a3b8;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #475569;
    color: #e2e8f0;
    selection-background-color: #6366f1;
    selection-color: white;
    padding: 4px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 6px 10px;
    border-radius: 4px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #334155;
}

QCheckBox {
    spacing: 8px;
    color: #e2e8f0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #475569;
    background-color: #0f172a;
}

QCheckBox::indicator:hover {
    border-color: #6366f1;
}

QCheckBox::indicator:checked {
    background-color: #6366f1;
    border-color: #6366f1;
}

#formatPanel QLineEdit {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    color: #e2e8f0;
}

#formatPanel QLineEdit:focus {
    border-color: #6366f1;
}

#browseBtn {
    background-color: #334155;
    border: none;
    border-radius: 6px;
    padding: 7px 14px;
    color: #e2e8f0;
    font-size: 12px;
}

#browseBtn:hover {
    background-color: #475569;
}

#formatLabel {
    color: #94a3b8;
    font-size: 12px;
}

/* ============================
   Add to Queue Button
   ============================ */
#addQueueBtn {
    background-color: #22c55e;
    color: #052e16;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}

#addQueueBtn:hover {
    background-color: #16a34a;
}

#addQueueBtn:pressed {
    background-color: #15803d;
}

/* ============================
   Tab Widget
   ============================ */
QTabWidget {
    border: none;
}

QTabWidget::pane {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 0 0 8px 8px;
    border-top: none;
}

QTabBar::tab {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 10px 24px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
    font-weight: bold;
    font-size: 12px;
    border: 1px solid #334155;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #0f172a;
    color: #e2e8f0;
}

QTabBar::tab:hover:!selected {
    background-color: #334155;
    color: #e2e8f0;
}

/* ============================
   Download Item Widget
   ============================ */
#downloadItem {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
}

#downloadItem:hover {
    border-color: #475569;
}

#downloadTitle {
    font-size: 13px;
    font-weight: bold;
    color: #f1f5f9;
}

#downloadDetails {
    font-size: 11px;
    color: #94a3b8;
}

/* Progress bar */
QProgressBar {
    background-color: #0f172a;
    border: none;
    border-radius: 3px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #6366f1;
    border-radius: 3px;
}

#cancelBtn {
    background-color: transparent;
    border: 1px solid #475569;
    border-radius: 14px;
    color: #94a3b8;
    font-size: 14px;
    font-weight: bold;
}

#cancelBtn:hover {
    background-color: #ef4444;
    border-color: #ef4444;
    color: white;
}

/* ============================
   History Item Widget
   ============================ */
#historyItem {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
}

#historyItem:hover {
    border-color: #475569;
}

#historyTitle {
    font-size: 13px;
    font-weight: bold;
    color: #f1f5f9;
}

#historyDetails {
    font-size: 11px;
    color: #94a3b8;
}

#openFolderBtn {
    background-color: transparent;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px 10px;
    color: #94a3b8;
    font-size: 11px;
}

#openFolderBtn:hover {
    background-color: #334155;
    color: #e2e8f0;
}

#clearHistoryBtn {
    background-color: transparent;
    border: 1px solid #475569;
    border-radius: 6px;
    color: #94a3b8;
    padding: 6px 14px;
    font-size: 12px;
}

#clearHistoryBtn:hover {
    background-color: #ef4444;
    border-color: #ef4444;
    color: white;
}

/* ============================
   Scroll Areas
   ============================ */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

/* Empty state labels */
#emptyLabel {
    color: #475569;
    font-size: 14px;
    padding: 40px;
}

/* ============================
   Status Bar
   ============================ */
QStatusBar {
    background-color: #1e293b;
    color: #94a3b8;
    border-top: 1px solid #334155;
    padding: 4px 12px;
    font-size: 12px;
}

/* ============================
   Scrollbars
   ============================ */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #334155;
    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background: #475569;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
}

/* ============================
   Message Box overrides
   ============================ */
QMessageBox {
    background-color: #1e293b;
}

QMessageBox QLabel {
    color: #e2e8f0;
}

QMessageBox QPushButton {
    background-color: #334155;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    color: #e2e8f0;
    font-weight: bold;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background-color: #475569;
}

QMessageBox QPushButton:default {
    background-color: #6366f1;
    color: white;
}
"""
