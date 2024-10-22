import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from langchain_community.llms import Ollama

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot")
        
        style = Style(theme="cosmo")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')
        
        self.chats = {}
        
        self.create_new_chat()
        
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)
        
        self.chat_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Chat", menu=self.chat_menu)
        
        self.chat_menu.add_command(label="Start New Chat", command=self.start_new_chat)
        self.chat_menu.add_command(label="Close Chat", command=self.close_current_chat)
        
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        
        self.view_menu.add_command(label="Toggle Full Screen", command=self.toggle_full_screen)
        
        self.llm = Ollama(model="llama3.2")
        
        self.full_screen = False
        
        self.root.bind("<F11>", self.toggle_full_screen_event)
        
    def create_new_chat(self):
        chat_id = len(self.notebook.tabs()) + 1
        chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(chat_frame, text=f"Chat {chat_id}")
        
        chat_log = tk.Text(chat_frame, state='disabled', width=80, height=20, bg="light grey")
        chat_log.pack(pady=10, expand=True, fill='both')
        
        chat_log.tag_configure('user', foreground='blue')
        chat_log.tag_configure('bot', foreground='green')
        chat_log.tag_configure('code', font=('Courier', 10, 'bold'), foreground='black', background='light yellow')
        
        entry_box = ttk.Entry(chat_frame, width=80, style='TEntry')
        entry_box.pack(pady=10, fill='x')
        entry_box.bind("<Return>", lambda event, log=chat_log, entry=entry_box, cid=chat_id: self.send_message(event, log, entry, cid))
        
        send_button = ttk.Button(chat_frame, text="Send", command=lambda log=chat_log, entry=entry_box, cid=chat_id: self.send_message(None, log, entry, cid), style='TButton')
        send_button.pack(pady=10)
        
        self.chats[chat_id] = {
            'log': chat_log
        }
        
        self.notebook.select(chat_frame)
        
    def send_message(self, event, chat_log, entry_box, chat_id):
        user_input = entry_box.get()
        entry_box.delete(0, tk.END)
        
        chat_log.config(state='normal')
        chat_log.insert(tk.END, "You: " + user_input + "\n", 'user')
        chat_log.config(state='disabled')
        
        print(f"User input: {user_input}")
        
        self.root.after(100, self.get_response, (user_input, chat_log, chat_id))
        
    def get_response(self, data):
        user_input, chat_log, chat_id = data
        
        response_generator = self.llm.stream(user_input)
        
        chat_log.config(state='normal')
        chat_log.insert(tk.END, "BelteiGPT: ", 'bot')
        chat_log.config(state='disabled')
        
        self.update_response(response_generator, chat_log, chat_id)
        
    def update_response(self, response_generator, chat_log, chat_id):
        try:
            response_part = next(response_generator)
            chat_log.config(state='normal')
            
            if '```' in response_part:
                chat_log.insert(tk.END, response_part.replace('```', ''), 'code')
            else:
                chat_log.insert(tk.END, response_part, 'bot')
                
            chat_log.config(state='disabled')
            
            self.root.after(100, self.update_response, response_generator, chat_log, chat_id)
        except StopIteration:
            chat_log.config(state='normal')
            chat_log.insert(tk.END, "\n")
            chat_log.config(state='disabled')
    
    def start_new_chat(self):
        self.create_new_chat()
        
    def close_current_chat(self):
        current_tab = self.notebook.select()
        if current_tab:
            chat_frame = self.notebook.nametowidget(current_tab)
            chat_id = int(self.notebook.tab(current_tab, "text").split()[-1])
            self.close_chat(chat_frame, chat_id)
        
    def close_chat(self, chat_frame, chat_id):
        self.notebook.forget(chat_frame)
        del self.chats[chat_id]
        
    def toggle_full_screen(self):
        self.full_screen = not self.full_screen
        self.root.attributes("-fullscreen", self.full_screen)
        
    def toggle_full_screen_event(self, event):
        self.toggle_full_screen()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
