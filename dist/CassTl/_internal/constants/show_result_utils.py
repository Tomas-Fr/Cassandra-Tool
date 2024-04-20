from constants.common import ErrorTitles, RESULT_STATISTICS, SUCCESS
from constants.highlight_text import highlight_text
from PyQt6.QtWidgets import QPlainTextEdit


class ShowResultUtils:

    def __init__(self: 'ShowResultUtils',
                 results_plain_text_edit: QPlainTextEdit,
                 result_statistics_plain_text_edit: QPlainTextEdit) -> None:
        self.results_plain_text_edit = results_plain_text_edit
        self.result_statistics_plain_text_edit = result_statistics_plain_text_edit


    def show_result(self: 'ShowResultUtils', message: str) -> None:
        current_text = self.results_plain_text_edit.toPlainText()
        if message:
            self.results_plain_text_edit.setPlainText(f"{current_text}\n{message}\n")
        highlight_text(self.results_plain_text_edit, ErrorTitles.Failed.value)

    def show_result_statistics(self: 'ShowResultUtils', added_rows_count: int, error_count: int) -> None:
        result_statistics = f"{RESULT_STATISTICS} Added rows: {added_rows_count}"
        self.result_statistics_plain_text_edit.setPlainText(result_statistics)
        if error_count > 0:
            result_statistics = f"{result_statistics} {ErrorTitles.Failed.value} {error_count}"
            self.result_statistics_plain_text_edit.setPlainText(result_statistics)
            highlight_text(self.result_statistics_plain_text_edit, ErrorTitles.Failed.value)

    def show_success(self: 'ShowResultUtils') -> None:
        result_statistics = f"{RESULT_STATISTICS} {SUCCESS}"
        self.result_statistics_plain_text_edit.setPlainText(result_statistics)
        highlight_text(self.result_statistics_plain_text_edit, SUCCESS, color="green")

    def clear_results(self: 'ShowResultUtils') -> None:
        self.results_plain_text_edit.setPlainText("")
        self.result_statistics_plain_text_edit.setPlainText(RESULT_STATISTICS)
