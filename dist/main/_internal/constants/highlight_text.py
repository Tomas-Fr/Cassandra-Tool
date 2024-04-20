from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor
from PyQt6.QtWidgets import QPlainTextEdit


def highlight_text(q_plain_text_edit: QPlainTextEdit, text_to_highlight: str, color: str = "red") -> None:
    highlight_format = QTextCharFormat()
    highlight_format.setForeground(QColor(color))

    cursor = q_plain_text_edit.textCursor()
    cursor.beginEditBlock()

    while not cursor.isNull() and not cursor.atEnd():
        cursor = q_plain_text_edit.document().find(text_to_highlight, cursor)
        if not cursor.isNull():
            cursor.mergeCharFormat(highlight_format)
            cursor.movePosition(QTextCursor.MoveOperation.WordRight)

    cursor.endEditBlock()