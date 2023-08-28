import csv
from dataclasses import asdict, fields
from typing import Protocol
from pathlib import Path
from structures import Article

import win32com.client as win32


class Printer(Protocol):
    def print_to(self, articles: list[Article], path: str, name: str) -> str:
        ...


class ExcelPrinter(Printer):
    def print_to(self, articles: list[Article], path: str, name: str) -> str:
        # create excel object
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = True  # False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Add()

        ws = wb.ActiveSheet
        flds = [fld.name for fld in fields(Article)]
        for col, fld in enumerate(flds, 1):
            ws.Cells(1, col).Value = fld
        for row, article in enumerate(articles, 2):
            for col, val in enumerate(asdict(article).values(), 1):
                if isinstance(val, dict):
                    val = str(val)
                ws.Cells(row, col).Value = val
        try:
            wb.SaveAs(str(Path.cwd() / "output" / f'{name.replace(" ", "_")}_results.xlsx'),
                      ReadOnlyRecommended=False,
                      CreateBackup=False,
                      ConflictResolution=win32.constants.xlLocalSessionChanges)
        except Exception:
            pass
        wb.Close()
        return str(Path.cwd() / "output" / f'{name.replace(" ","_")}_results.xlsx')


class CSVPrinter(Printer):
    def print_to(self, articles: list[Article], path: str, name: str) -> str:
        with open(fr'{path}\{name}_results.csv', 'a', newline='', encoding="utf-8") as f:
            flds = [fld.name for fld in fields(Article)]
            w = csv.DictWriter(f, flds, delimiter="|")
            w.writeheader()
            w.writerows([asdict(article) for article in articles])
        return fr'{path}\{name}_results.csv'

