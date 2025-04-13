import sys
import threading
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from cefpython3 import cefpython as cef
from dash_app import run_dash_server
from calendar_dialog import CalendarDialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        sys.excepthook = cef.ExceptHook
        cef.Initialize()

        self.title("Yield Curve Viewer")
        self.geometry("1200x800")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ====== 上部バー ======
#         self.frame_top = ctk.CTkFrame(self, height=50)
#         self.frame_top.pack(side="top", fill="x", padx=10, pady=5)

#         self.list_selector = ctk.CTkOptionMenu(self.frame_top, values=["Option 1", "Option 2"], width=300, font=("Arial", 14))
#         self.list_selector.place(relx=0.3, rely=0.5, anchor="center")

#         self.btn_display = ctk.CTkButton(self.frame_top, text="plot")
#         self.btn_display.place(relx=0.7, rely=0.5, anchor="center")

        # ====== メイン領域 ======
        self.frame_main = ctk.CTkFrame(self)
        self.frame_main.pack(fill="both", expand=True, padx=10, pady=5)

        # --- 左側（コントロール） ---
        self.frame_left = ctk.CTkFrame(self.frame_main, width=200)
        self.frame_left.pack(side="left", fill="y", padx=10, pady=10)
        
        self.list_selector = ctk.CTkOptionMenu(self.frame_left, values=["Option 1", "Option 2"], width=300, font=("Arial", 14))
        self.list_selector.pack(padx=8, pady=5)
        
        self.frame_Basedate = ctk.CTkFrame(self.frame_left, corner_radius=10, height=50, width=160)
        self.frame_Basedate.pack(padx=10, pady=10)

        self.label = ctk.CTkLabel(self.frame_Basedate, text="Date")
        self.label.grid(row=0, column=0, padx=5, pady=(10, 2), sticky="w")

        self.__entry = ctk.CTkEntry(self.frame_Basedate, width=160)
        self.__entry.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.button = ctk.CTkButton(self.frame_Basedate, text="get", width=40, command=self.pick_date)
        self.button.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.ccy_menu = ctk.CTkOptionMenu(self.frame_left, values=["USD", "EUR", "JPY"])
        self.ccy_menu.pack(padx=8, pady=5)
        self.ccy_menu.set("CCY")
        
        self.btn_display = ctk.CTkButton(self.frame_left, text="plot", command = self.show_values)
        self.btn_display.pack(padx=8, pady=5)
        
        self.button = ctk.CTkButton(self.frame_left,text="リフレッシュ", command=self.clear_dash_frame)
        self.button.pack(padx=8, pady=5)
        
        self.button = ctk.CTkButton(self.frame_left,text="再読み込み", command=self.recreate_dash_frame)
        self.button.pack(padx=8, pady=5)
        
        # --- 右側：Dash or Google を埋め込む tk.Frame（←ここが違い） ---
        self.frame_plot = tk.Frame(self.frame_main, width=780, height=680, bg="black")
        self.frame_plot.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.frame_plot.pack_propagate(False)
        self.frame_plot.update()

            
        # Dash起動
        threading.Thread(target=run_dash_server, daemon=True).start()

        self.after(1500, self.embed_dash_view)

    def clear_dash_frame(self):
        if hasattr(self, "frame_plot"):
            self.frame_plot.destroy()
            self.frame_plot = None
            
    def recreate_dash_frame(self):
        # 再生成
        self.frame_plot = tk.Frame(self.frame_main, width=780, height=680, bg="black")
        self.frame_plot.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.frame_plot.pack_propagate(False)
        self.frame_plot.update()

        # Dash埋め込み
        self.after(300, self.embed_dash_view)

    def embed_dash_view(self):
        hwnd = self.frame_plot.winfo_id()
        width, height = self.frame_plot.winfo_width(), self.frame_plot.winfo_height()

        window_info = cef.WindowInfo()
        rect = [0, 0, width, height]
        window_info.SetAsChild(hwnd, rect)

        # ✔ Dash用（またはテストに Googleでも可）
        self.browser =  cef.CreateBrowserSync(window_info, url="http://127.0.0.1:8050")
        # cef.CreateBrowserSync(window_info, url="https://google.com")

        def loop_cef():
            cef.MessageLoopWork()
            self.frame_plot.after(10, loop_cef)

        loop_cef()

    def pick_date(self):
        dialog = CalendarDialog(self, title="Select Date")
        if dialog.is_selected():
            self.__entry.delete(0, ctk.END)
            self.__entry.insert(0, dialog.to_str())

    def show_values(self):
        print("現在の日付:", self.list_selector.get())
        print("現在の日付:", self.__entry.get())
        print("現在の通貨:", self.ccy_menu.get())

    def on_closing(self):
        if messagebox.askokcancel("終了", "アプリを終了しますか？"):
            self.destroy()
            cef.Shutdown()
            sys.exit()

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
