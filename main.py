import os
import threading
import time
import customtkinter as ctk
import pywinstyles
from dotenv import load_dotenv
from google import genai

load_dotenv()

ctk.set_appearance_mode("Dark")


class FuturisticAIAssistant(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AI Desktop Workspace & Summarizer")
        self.geometry("940x720")

        # Visual Theme Palette (Cyber/Glass Dark)
        self.COLOR_BG = "#0b0d14"
        self.COLOR_CARD = "#131722"
        self.COLOR_CARD_ALT = "#1a1f2c"
        self.COLOR_BORDER = "#2a3147"
        self.COLOR_GLOW = "#00f0ff"  # Neon Cyan
        self.COLOR_PURPLE = "#7000ff"  # Deep Purple
        self.TEXT_MAIN = "#ffffff"
        self.TEXT_MUTED = "#6c7897"

        self.configure(fg_color=self.COLOR_BG)

        # Initialize API Client
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

        self.create_widgets()
        self.apply_theme_effects()

    def apply_theme_effects(self):
        try:
            pywinstyles.apply_style(self, "acrylic")
            pywinstyles.change_header_color(self, color=self.COLOR_BG)
        except Exception:
            pass

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- HEADER HUD ---
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_CARD,
            border_color=self.COLOR_GLOW,
            border_width=1,
            corner_radius=16,
        )
        self.header_frame.grid(
            row=0, column=0, padx=24, pady=(20, 10), sticky="ew"
        )

        self.title_group = ctk.CTkFrame(
            self.header_frame, fg_color="transparent"
        )
        self.title_group.pack(side="left", padx=20, pady=16)

        self.status_dot = ctk.CTkLabel(
            self.title_group,
            text="●",
            text_color="#00ff88",
            font=ctk.CTkFont(size=14),
        )
        self.status_dot.pack(side="left", padx=(0, 8))

        self.title_label = ctk.CTkLabel(
            self.title_group,
            text="GEMINI CORE",
            font=ctk.CTkFont(size=18, weight="bold", family="Consolas"),
            text_color=self.COLOR_GLOW,
        )
        self.title_label.pack(side="left")

        self.sub_title = ctk.CTkLabel(
            self.title_group,
            text=" |  AI Workspace v2.0",
            font=ctk.CTkFont(size=13),
            text_color=self.TEXT_MUTED,
        )
        self.sub_title.pack(side="left")

        self.mode_option = ctk.CTkOptionMenu(
            self.header_frame,
            values=[
                "Summarize Text",
                "Key Takeaways",
                "Code/Writing Assistant",
            ],
            fg_color=self.COLOR_CARD_ALT,
            button_color=self.COLOR_BORDER,
            button_hover_color=self.COLOR_GLOW,
            dropdown_fg_color=self.COLOR_CARD,
            dropdown_hover_color=self.COLOR_BORDER,
            text_color=self.TEXT_MAIN,
            corner_radius=10,
            width=200,
        )
        self.mode_option.pack(side="right", padx=20, pady=16)

        # --- INPUT PANEL ---
        self.input_frame = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_CARD,
            border_color=self.COLOR_BORDER,
            border_width=1,
            corner_radius=16,
        )
        self.input_frame.grid(row=1, column=0, padx=24, pady=8, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_meta = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.input_meta.grid(
            row=0, column=0, sticky="ew", padx=20, pady=(14, 6)
        )

        self.input_label = ctk.CTkLabel(
            self.input_meta,
            text="PROMPT INPUT",
            font=ctk.CTkFont(size=11, weight="bold", family="Consolas"),
            text_color=self.TEXT_MUTED,
        )
        self.input_label.pack(side="left")

        self.input_text = ctk.CTkTextbox(
            self.input_frame,
            height=120,
            corner_radius=12,
            fg_color=self.COLOR_BG,
            border_color=self.COLOR_BORDER,
            border_width=1,
            text_color=self.TEXT_MAIN,
            font=ctk.CTkFont(size=13),
        )
        self.input_text.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.btn_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, padx=20, pady=(6, 14), sticky="e")

        self.clear_btn = ctk.CTkButton(
            self.btn_frame,
            text="Clear",
            width=80,
            fg_color="transparent",
            border_color=self.COLOR_BORDER,
            border_width=1,
            hover_color=self.COLOR_CARD_ALT,
            text_color=self.TEXT_MUTED,
            corner_radius=8,
            command=self.clear_input,
        )
        self.clear_btn.pack(side="left", padx=6)

        self.process_btn = ctk.CTkButton(
            self.btn_frame,
            text="⚡ GENERATE",
            width=140,
            fg_color=self.COLOR_GLOW,
            hover_color="#00b8cc",
            text_color="#05070a",
            font=ctk.CTkFont(size=12, weight="bold", family="Consolas"),
            corner_radius=8,
            command=self.start_ai_task,
        )
        self.process_btn.pack(side="left", padx=6)

        # --- OUTPUT PANEL ---
        self.output_frame = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_CARD,
            border_color=self.COLOR_BORDER,
            border_width=1,
            corner_radius=16,
        )
        self.output_frame.grid(
            row=2, column=0, padx=24, pady=(8, 20), sticky="nsew"
        )
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(1, weight=1)

        self.output_meta = ctk.CTkFrame(
            self.output_frame, fg_color="transparent"
        )
        self.output_meta.grid(
            row=0, column=0, sticky="ew", padx=20, pady=(14, 6)
        )

        self.output_label = ctk.CTkLabel(
            self.output_meta,
            text="LIVE STREAM OUTPUT",
            font=ctk.CTkFont(size=11, weight="bold", family="Consolas"),
            text_color=self.TEXT_MUTED,
        )
        self.output_label.pack(side="left")

        self.stats_label = ctk.CTkLabel(
            self.output_meta,
            text="Idle",
            font=ctk.CTkFont(size=11, family="Consolas"),
            text_color=self.TEXT_MUTED,
        )
        self.stats_label.pack(side="right")

        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            corner_radius=12,
            fg_color=self.COLOR_BG,
            border_color=self.COLOR_BORDER,
            border_width=1,
            text_color=self.TEXT_MAIN,
            font=ctk.CTkFont(size=13),
            state="disabled",
        )
        self.output_text.grid(
            row=1, column=0, padx=20, pady=(0, 10), sticky="nsew"
        )

        self.action_frame = ctk.CTkFrame(
            self.output_frame, fg_color="transparent"
        )
        self.action_frame.grid(
            row=2, column=0, sticky="ew", padx=20, pady=(0, 14)
        )

        self.copy_btn = ctk.CTkButton(
            self.action_frame,
            text="Copy Output",
            width=110,
            fg_color="transparent",
            border_color=self.COLOR_BORDER,
            border_width=1,
            hover_color=self.COLOR_CARD_ALT,
            text_color=self.TEXT_MAIN,
            corner_radius=8,
            command=self.copy_to_clipboard,
        )
        self.copy_btn.pack(side="right")

    def clear_input(self):
        self.input_text.delete("1.0", "end")

    def copy_to_clipboard(self):
        content = self.output_text.get("1.0", "end-1c")
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.stats_label.configure(text="Copied to clipboard! ✓")

    def write_output(self, text):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.configure(state="disabled")

    def append_output_chunk(self, chunk):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", chunk)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def start_ai_task(self):
        user_input = self.input_text.get("1.0", "end-1c").strip()
        selected_mode = self.mode_option.get()

        if not user_input:
            self.write_output(
                "⚠️ Please enter some text or a prompt to analyze."
            )
            return

        if not self.client:
            self.write_output(
                "❌ Error: Missing GEMINI_API_KEY in your .env file."
            )
            return

        if selected_mode == "Summarize Text":
            prompt = f"Provide a clean, well-structured summary of the following text:\n\n{user_input}"
        elif selected_mode == "Key Takeaways":
            prompt = f"Extract the key bullet points and core takeaways from this text:\n\n{user_input}"
        else:
            prompt = user_input

        self.process_btn.configure(state="disabled", text="⚡ STREAMING...")
        self.status_dot.configure(text_color=self.COLOR_GLOW)
        self.stats_label.configure(text="Streaming tokens...")
        self.write_output("")

        self.start_time = time.time()
        threading.Thread(
            target=self.stream_ai_response, args=(prompt,), daemon=True
        ).start()

    def stream_ai_response(self, prompt):
        models_to_try = [
            "gemini-3.8-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.6-flash",
        ]
        stream_successful = False

        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content_stream(
                    model=model_name, contents=prompt
                )
                for chunk in response:
                    if chunk.text:
                        self.after(0, self.append_output_chunk, chunk.text)
                stream_successful = True
                break
            except Exception as e:
                error_msg = str(e)
                if "503" in error_msg or "404" in error_msg:
                    continue
                else:
                    self.after(
                        0,
                        self.write_output,
                        f"❌ API Error: {error_msg}",
                    )
                    stream_successful = True
                    break

        if not stream_successful:
            self.after(
                0,
                self.write_output,
                "❌ API Error: Gemini services are temporarily busy across all regions.",
            )

        self.after(0, self.finish_ai_task)

    def finish_ai_task(self):
        elapsed = round(time.time() - self.start_time, 2)
        self.process_btn.configure(state="normal", text="⚡ GENERATE")
        self.status_dot.configure(text_color="#00ff88")
        self.stats_label.configure(text=f"Completed in {elapsed}s")


if __name__ == "__main__":
    app = FuturisticAIAssistant()
    app.mainloop()