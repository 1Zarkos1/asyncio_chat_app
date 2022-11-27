import tkinter as tk
import tkinter.ttk as ttk
import threading


def gui(inbox, out_queue):
    root = tk.Tk()
    root.title("asyncio chat")

    def on_close():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    main_frame = tk.Frame(master=root)
    canvas = tk.Canvas(master=main_frame)
    v_scroll = tk.Scrollbar(master=main_frame, command=canvas.yview)
    canvas.config(yscrollcommand=v_scroll.set, scrollregion=canvas.bbox("all"))
    chat_frame = tk.Frame(master=canvas)
    canvas.create_window((0,0), window=chat_frame, anchor="nw")
    input_frame = tk.Frame(master=root)

    main_frame.pack(side="top", fill="both", expand=True)
    canvas.pack(side="left", fill="both", expand=True)
    v_scroll.pack(fill="y", side="right")
    input_frame.pack(side="top", fill="x")


    def add_received_message(inbox, frame):
        while True:
            message = inbox.get()
            message_label = tk.Label(
                text=message, master=frame, anchor="w", justify="left"
            )
            message_label.pack(fill="x")
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.yview_moveto(1)

    t = threading.Thread(target=add_received_message, args=(inbox, chat_frame), daemon=True)
    t.start()

    input_field = tk.Entry(master=input_frame)
    input_field.pack(side="left", fill="x", expand=True)
    
    def send_message(e, field=input_field):
        out_queue.put(field.get())
        field.delete(0, "end")
    
    input_field.bind("<Return>", send_message)

    send_btn = tk.Button(text='send', master=input_frame)
    send_btn.bind("<ButtonPress>", send_message)
    send_btn.pack()

    root.mainloop()