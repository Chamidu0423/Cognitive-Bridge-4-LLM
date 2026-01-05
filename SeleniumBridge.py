import customtkinter as ctk
import threading
import time
import sys
import io
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Fix encoding for Sinhala text
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- SYSTEM CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- MODEL DEFINITIONS ---
MODEL_CONFIGS = {
    "ChatGPT (OpenAI)": {
        "url_key": "chatgpt.com",
        "input_selector": [(By.ID, "prompt-textarea")],
        "output_selector": [(By.CSS_SELECTOR, ".markdown")],
    },
    "Gemini (Google)": {
        "url_key": "google.com",
        "input_selector": [(By.CSS_SELECTOR, ".ql-editor"), (By.CSS_SELECTOR, "rich-textarea")],
        "output_selector": [(By.CSS_SELECTOR, ".model-response-text"), (By.TAG_NAME, "message-content")],
    },
    "Grok (xAI)": {
        "url_key": "grok.com",
        "input_selector": [(By.CSS_SELECTOR, "textarea[placeholder='Ask Grok anything']"), (By.CSS_SELECTOR, "textarea")],
        "output_selector": [(By.CSS_SELECTOR, ".prose"), (By.CSS_SELECTOR, "div[data-testid='message-bubble']")],
    },
    "DeepSeek (R1/V3)": {
        "url_key": "deepseek.com",
        "input_selector": [(By.CSS_SELECTOR, "textarea[placeholder='Message DeepSeek']")],
        "output_selector": [(By.CSS_SELECTOR, ".ds-markdown"), (By.CLASS_NAME, "ds-markdown")],
    }
}

class AIResearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Cognitive Bridge: AI Interoperability Suite v3.1")
        self.geometry("1280x850")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # State Variables
        self.running = False
        self.driver = None

        # ================= SIDEBAR (CONFIGURATION) =================
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Header
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="COGNITIVE BRIDGE", font=ctk.CTkFont(size=22, weight="bold", family="Roboto"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="w")
        
        self.lbl_subtitle = ctk.CTkLabel(self.sidebar, text="Automated Dialectic Framework", text_color="#aaaaaa", font=ctk.CTkFont(size=12))
        self.lbl_subtitle.grid(row=1, column=0, padx=20, pady=(0, 30), sticky="w")

        # Model Configuration
        self.lbl_section1 = ctk.CTkLabel(self.sidebar, text="MODEL CONFIGURATION", text_color="#888888", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_section1.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")

        # Primary Model
        ctk.CTkLabel(self.sidebar, text="Initiator Model:", anchor="w").grid(row=3, column=0, padx=20, sticky="ew")
        self.opt_p1 = ctk.CTkOptionMenu(self.sidebar, values=list(MODEL_CONFIGS.keys()), fg_color="#333", button_color="#444", text_color="white")
        self.opt_p1.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.opt_p1.set("ChatGPT (OpenAI)")

        # Secondary Model
        ctk.CTkLabel(self.sidebar, text="Respondent Model:", anchor="w").grid(row=5, column=0, padx=20, sticky="ew")
        self.opt_p2 = ctk.CTkOptionMenu(self.sidebar, values=list(MODEL_CONFIGS.keys()), fg_color="#333", button_color="#444", text_color="white")
        self.opt_p2.grid(row=6, column=0, padx=20, pady=(0, 30), sticky="ew")
        self.opt_p2.set("Gemini (Google)")

        # Protocol Settings
        self.lbl_section2 = ctk.CTkLabel(self.sidebar, text="EXECUTION PROTOCOL", text_color="#888888", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_section2.grid(row=7, column=0, padx=20, pady=(10, 5), sticky="w")

        self.protocol_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.protocol_frame.grid(row=8, column=0, padx=10, sticky="ew")

        self.term_mode = ctk.StringVar(value="conclusion")
        
        # Radio Buttons
        self.rb_conclusion = ctk.CTkRadioButton(self.protocol_frame, text="Semantic Termination (Wait for 'ALL DONE')", variable=self.term_mode, value="conclusion", command=self.toggle_slider)
        self.rb_conclusion.pack(anchor="w", padx=10, pady=8)
        
        self.rb_count = ctk.CTkRadioButton(self.protocol_frame, text="Iterative Termination (Max Cycles)", variable=self.term_mode, value="count", command=self.toggle_slider)
        self.rb_count.pack(anchor="w", padx=10, pady=8)

        # Slider
        self.lbl_slider = ctk.CTkLabel(self.protocol_frame, text="Iterations: 10", text_color="gray")
        self.lbl_slider.pack(anchor="w", padx=10, pady=(10,0))
        
        self.slider = ctk.CTkSlider(self.protocol_frame, from_=1, to=50, number_of_steps=49, command=self.update_slider, progress_color="#1f6aa5")
        self.slider.pack(fill="x", padx=10, pady=(0, 10))
        self.slider.set(10)
        self.slider.configure(state="disabled")

        # Control Buttons
        self.btn_start = ctk.CTkButton(self.sidebar, text="INITIALIZE SESSION", fg_color="#1f6aa5", hover_color="#144870", command=self.start_thread, height=45, font=ctk.CTkFont(weight="bold"))
        self.btn_start.grid(row=11, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.btn_stop = ctk.CTkButton(self.sidebar, text="TERMINATE", fg_color="#c42b1c", hover_color="#8a1f14", command=self.stop_bot, state="disabled", height=45)
        self.btn_stop.grid(row=12, column=0, padx=20, pady=(0, 20), sticky="ew")

        # ================= MAIN WORKSPACE =================
        self.tabview = ctk.CTkTabview(self, fg_color="transparent")
        self.tabview.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)
        
        self.tab_console = self.tabview.add("Command Console")
        self.tab_docs = self.tabview.add("Documentation")

        self.setup_console()
        self.setup_documentation()

    def setup_console(self):
        self.tab_console.grid_columnconfigure(0, weight=1)
        # FIX: Changed expansion from Row 2 (Label) to Row 3 (Log Box)
        self.tab_console.grid_rowconfigure(3, weight=1) 

        # Prompt Input
        ctk.CTkLabel(self.tab_console, text="System Instruction / Initial Prompt:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=(10, 5))
        
        self.entry_prompt = ctk.CTkTextbox(self.tab_console, height=100, font=("Consolas", 12), border_width=1, border_color="#333")
        self.entry_prompt.grid(row=1, column=0, sticky="ew", pady=(0, 15)) # Reduced bottom padding slightly
        self.entry_prompt.insert("0.0", "Engage in a critical analysis of the following topic: [Topic Here]. Critically evaluate arguments. When a synthesis is reached, output 'ALL DONE'.")

        # Logs Label (No extra expansion now)
        ctk.CTkLabel(self.tab_console, text="Real-time Execution Logs:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        # Logs Box (Now expands to fill space)
        self.log_box = ctk.CTkTextbox(self.tab_console, font=("Consolas", 11), fg_color="#0d0d0d", text_color="#00ff00", border_width=1, border_color="#333")
        self.log_box.grid(row=3, column=0, sticky="nsew")
        self.log_box.configure(state="disabled")

        # Status Bar
        self.status = ctk.CTkLabel(self.tab_console, text="System Status: IDLE", anchor="w", text_color="#888")
        self.status.grid(row=4, column=0, sticky="ew", pady=(5, 0))

    def setup_documentation(self):
        self.doc_scroll = ctk.CTkScrollableFrame(self.tab_docs, fg_color="transparent")
        self.doc_scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(self.doc_scroll, text="System Documentation & Safety Protocols", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=20)
        
        # --- CRITICAL WARNING SECTION ---
        self.add_doc_section("⚠️ SECURITY WARNING: ACCOUNT SAFETY", 
                             "DO NOT USE YOUR PERSONAL OR PRIMARY ACCOUNTS. Automated interactions can trigger anti-bot mechanisms. ALWAYS use secondary/throwaway accounts.",
                             "", text_color="#ff5555")

        self.add_doc_section("1. Environment Initialization", 
                             "Install required dependencies via terminal:",
                             "pip install selenium customtkinter packaging pillow pyperclip webdriver-manager")
        
        # --- CHROME SECTION ---
        self.add_doc_section("2. Debug Protocol Launch (CRITICAL)", 
                             "Launch Chrome in Debug Mode using COMMAND PROMPT (CMD).\nIMPORTANT: Do NOT use PowerShell for this command.",
                             r'start chrome --remote-debugging-port=9222 --user-data-dir="C:\selenium\ChromeProfile"')
        
        self.add_doc_section("3. Operation Guide", 
                             "Select models and termination logic. Ensure the debug window remains open during execution.",
                             "")

    def add_doc_section(self, title, desc, command, text_color="#1f6aa5"):
        frame = ctk.CTkFrame(self.doc_scroll, fg_color="#1c1c1c")
        frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(weight="bold", size=14), text_color=text_color).pack(anchor="w", padx=15, pady=(15,5))
        ctk.CTkLabel(frame, text=desc, wraplength=800, justify="left", text_color="#ccc").pack(anchor="w", padx=15, pady=5)

        if command:
            cmd_frame = ctk.CTkFrame(frame, fg_color="#111", corner_radius=5)
            cmd_frame.pack(fill="x", padx=15, pady=(5, 15))
            
            entry = ctk.CTkEntry(cmd_frame, border_width=0, fg_color="transparent", font=("Consolas", 11), text_color="#ddd")
            entry.insert(0, command)
            entry.configure(state="readonly")
            entry.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            
            btn = ctk.CTkButton(cmd_frame, text="Copy", width=60, height=25, fg_color="#333", hover_color="#444", 
                                command=lambda c=command: self.copy_to_clipboard(c))
            btn.pack(side="right", padx=10, pady=8)

    def copy_to_clipboard(self, text):
        pyperclip.copy(text)
        self.status.configure(text="System Notification: Command copied to clipboard.")

    # --- LOGIC HANDLERS ---
    def update_slider(self, value):
        self.lbl_slider.configure(text=f"Iterations: {int(value)}")

    def toggle_slider(self):
        if self.term_mode.get() == "count":
            self.slider.configure(state="normal", progress_color="#1f6aa5")
            self.lbl_slider.configure(text_color="white")
        else:
            self.slider.configure(state="disabled", progress_color="#555")
            self.lbl_slider.configure(text_color="gray")

    def log(self, message):
        self.log_box.configure(state="normal")
        ts = time.strftime("[%H:%M:%S]")
        self.log_box.insert("end", f"{ts} {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.status.configure(text=f"System Status: {message}")

    def start_thread(self):
        if not self.running:
            self.running = True
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.entry_prompt.configure(state="disabled")
            self.log("Initializing Automation Sequence...")
            threading.Thread(target=self.run_logic, daemon=True).start()

    def stop_bot(self):
        self.running = False
        self.log("Termination Signal Sent. Halting processes...")
        self.btn_stop.configure(state="disabled")

    # --- SELENIUM CORE ---
    def paste_content(self, element, text):
        try:
            pyperclip.copy(text)
            time.sleep(0.5)
            element.click()
            time.sleep(0.2)
            element.send_keys(Keys.CONTROL, 'v')
            time.sleep(0.5)
        except:
            element.send_keys(text)

    def switch_to_tab(self, keyword):
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            if keyword in self.driver.current_url:
                self.driver.execute_script("window.focus();")
                return True
        self.log(f"Error: Target endpoint '{keyword}' unreachable.")
        return False

    def find_safe(self, selectors):
        for by, val in selectors:
            try: return WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((by, val)))
            except: continue
        return None

    def get_reply_safe(self, selectors):
        for by, val in selectors:
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((by, val)))
                elements = self.driver.find_elements(by, val)
                if elements:
                    text = elements[-1].get_attribute("innerText")
                    if text.strip(): return text
            except: continue
        return None

    def run_logic(self):
        self.log("Connecting to Chrome Debugging Interface...")
        try:
            opts = Options()
            opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.driver = webdriver.Chrome(options=opts)
            
            p1_key, p2_key = self.opt_p1.get(), self.opt_p2.get()
            mode, limit = self.term_mode.get(), int(self.slider.get())
            msg = self.entry_prompt.get("0.0", "end").strip()

            self.log(f"Session Started: {p1_key} <-> {p2_key}")
            round_n = 1
            
            while self.running:
                if mode == "count" and round_n > limit:
                    self.log("Iteration limit reached. Concluding session."); break
                
                self.log(f"--- Iteration Cycle {round_n} ---")

                for player in [p1_key, p2_key]:
                    if not self.switch_to_tab(MODEL_CONFIGS[player]["url_key"]): return
                    if not self.running: return

                    try:
                        inp = self.find_safe(MODEL_CONFIGS[player]["input_selector"])
                        if inp:
                            self.paste_content(inp, msg)
                            time.sleep(1)
                            inp.send_keys(Keys.ENTER)
                            self.log(f"Awaiting response from {player}...")
                            time.sleep(20)
                            
                            reply = self.get_reply_safe(MODEL_CONFIGS[player]["output_selector"])
                            if reply:
                                msg = reply
                                self.log(f"Data received from {player}.")
                                if "ALL DONE" in msg and mode == "conclusion": 
                                    self.log(f"Semantic Termination Triggered by {player}.")
                                    self.running = False; return
                            else: self.log(f"Warning: No response data detected from {player}")
                    except Exception as e: self.log(f"Exception in {player} module: {e}")
                    
                    time.sleep(3)
                    if not self.running: return

                round_n += 1

        except Exception as e:
            self.log(f"Critical System Error: {e}")
            self.log("Verify Chrome Debug Port (9222) is active.")
        finally:
            self.running = False
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.entry_prompt.configure(state="normal")
            self.log("Session Terminated.")

if __name__ == "__main__":
    app = AIResearchApp()
    app.mainloop()