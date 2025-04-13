import tkinter
from tkinter.simpledialog import Dialog
from datetime import datetime
from tkcalendar import Calendar


class CalendarDialog(Dialog):
    __date: str
    __calendar : Calendar
    def __init__(self, master : tkinter.Tk, title=None) -> None:
        """カレンダーを選択し日付を得るダイアログを生成する

        Args:
            master (tkinter.Tk): 配置するコンポーネント
            title (_type_, optional): _description_. Defaults to None.
        """
        self.__date = ""
        self.__calendar = None
        super().__init__(parent=master, title=title)
        
    def body(self, master : tkinter.Tk) -> None:
        """ダイアログ内に配置するコンポーネント.今回はカレンダーを表示する。

        Args:
            master (tkinter.Tk): 配置するコンポーネント
        """
        self.__calendar = Calendar(master, showweeknumbers=False,date_pattern="yyyy/mm/dd")
        self.__calendar.grid(sticky="w", row=0, column=0)
        
    def apply(self) -> None:
        """OKが押された時の処理
        """
        self.__date = self.__calendar.get_date()
        
    def __str__(self) -> str:
        return self.to_str()
    
    def __repr__(self) -> str:
        return str(self)

    def to_str(self) -> str:
        """日付をで得る

        Returns:
            str: 日付
        """
        return self.__date

    def to_datetime(self) -> datetime:
        """日付を得る

        Returns:
            datetime: 日付
        """
        return datetime.strptime(r"%Y/%m/%d")

    def is_selected(self) -> bool:
        """カレンダーが選択されたか"""
        return self.__date != ''
