from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
import pygame, os, json
from gtts import gTTS  # Google Voice
import qrcode   # QR
from PIL import Image, ImageTk # QR display ku

# ---------------- WINDOW ----------------
root = Tk()
root.title("SMART ATM MANAGEMENT SYSTEM PRO")
root.geometry("1000x650")
root.resizable(False, False)
C = {"BG":"#0F172A", "FRAME":"#1E293B", "BUTTON":"#2563EB", "HOVER":"#1D4ED8", "TEXT":"white", "GREEN":"#10B981", "RED":"#EF4444"}
root.configure(bg=C["BG"])

# ---------------- DATA + VOICE + SOUND ----------------
DATA_FILE = "atm_data.json"
balance, pin, history, name = 10000, "1234", [], "SHAMU GUNA"
card_locked, attempts = False, 0

pygame.init()

def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("temp_voice.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load("temp_voice.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        os.remove("temp_voice.mp3")
    except:
        print(f"VOICE: {text}") # Internet illa na print aagum

def play_click(): pass
def clear_screen():
    for widget in root.winfo_children(): widget.destroy()
def hover(btn):
    btn.bind("<Enter>", lambda e: btn.config(bg=C["HOVER"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=C["BUTTON"]))
def save_data():
    with open(DATA_FILE, "w") as f: json.dump({"balance":balance,"pin":pin,"history":history,"name":name}, f)

# ==========================================================
# ALL FUNCTIONS
# ==========================================================
def loading():
    clear_screen()
    Label(root, text="🏦 SMART ATM PRO", font=("Arial",28,"bold"), bg=C["BG"], fg=C["TEXT"]).pack(pady=40)
    progress = ttk.Progressbar(root, length=500); progress.pack(pady=50)
    percent = Label(root, text="0%", font=("Arial",14,"bold"), bg=C["BG"], fg=C["GREEN"]); percent.pack()
    for i in range(101): progress["value"] = i; percent.config(text=f"{i}%"); root.update(); root.after(15)
    root.after(500, login_screen)

def login_screen():
    clear_screen()
    speak("Welcome to Smart ATM Pro. Please enter your PIN")
    frame = Frame(root, bg=C["FRAME"], padx=50, pady=50); frame.place(relx=0.5, rely=0.5, anchor="center")
    Label(frame, text="🔒 ENTER PIN", font=("Arial",20,"bold"), bg=C["FRAME"], fg=C["TEXT"]).pack(pady=10)
    pin_entry = Entry(frame, show="*", font=("Arial",18), width=10, justify="center"); pin_entry.pack(pady=10)
    
    def check_pin():
        global attempts, card_locked
        if card_locked: messagebox.showerror("Locked","Card Blocked. Contact Bank"); return
        if pin_entry.get() == pin: dashboard()
        else:
            attempts += 1
            if attempts >= 3: card_locked = True; messagebox.showerror("Blocked","3 Wrong Attempts. Card Blocked")
            else: messagebox.showerror("Error", f"Wrong PIN. {3-attempts} attempts left")
    
    Button(frame, text="LOGIN", command=check_pin, bg=C["BUTTON"], fg="white", font=("Arial",14,"bold"), width=15).pack(pady=10)
    Button(frame, text="FINGERPRINT LOGIN", command=fingerprint_login, bg=C["GREEN"], fg="white", font=("Arial",12,"bold"), width=20).pack(pady=5)
    hover(Button())

def fingerprint_login():
    speak("Fingerprint scan successful")
    messagebox.showinfo("Success","Fingerprint Matched!")
    dashboard()

def dashboard():
    clear_screen()
    speak("Login successful. Welcome to dashboard")
    Label(root, text=f"Welcome, {name}", font=("Arial",22,"bold"), bg=C["BG"], fg=C["TEXT"]).pack(pady=20)
    frame = Frame(root, bg=C["BG"]); frame.pack(pady=10)
    buttons = [
        ("BALANCE ENQUIRY", balance_screen),
        ("DEPOSIT", deposit_screen),
        ("WITHDRAW", withdraw_screen),
        ("FAST CASH", fast_cash_screen),
        ("MINI STATEMENT", history_screen),
        ("QR PAYMENT", qr_payment_screen),
        ("CHANGE PIN", change_pin_screen),
        ("LOGOUT", logout)
    ]
    for i, (txt, cmd) in enumerate(buttons):
        b = Button(frame, text=txt, command=cmd, bg=C["BUTTON"], fg="white", font=("Arial",12,"bold"), width=25, height=2)
        b.grid(row=i//2, column=i%2, padx=10, pady=10)
        hover(b)

def balance_screen():
    clear_screen()
    speak(f"Your current balance is {balance} rupees")
    Label(root, text=f"Current Balance: ₹{balance}", font=("Arial",24,"bold"), bg=C["BG"], fg=C["GREEN"]).pack(pady=100)
    Button(root, text="BACK", command=dashboard, bg=C["BUTTON"], fg="white").pack()

def deposit_screen():
    def deposit():
        global balance
        amt = int(entry.get())
        balance += amt
        history.append(f"Deposited ₹{amt} on {datetime.now().strftime('%d-%m %H:%M')}")
        save_data()
        speak(f"{amt} rupees deposited successfully")
        messagebox.showinfo("Success", f"₹{amt} Deposited")
        dashboard()
    clear_screen()
    Label(root, text="DEPOSIT AMOUNT", font=("Arial",20,"bold"), bg=C["BG"], fg=C["TEXT"]).pack(pady=50)
    entry = Entry(root, font=("Arial",18)); entry.pack(pady=10)
    Button(root, text="DEPOSIT", command=deposit, bg=C["GREEN"], fg="white").pack(pady=10)
    Button(root, text="BACK", command=dashboard, bg=C["BUTTON"], fg="white").pack()

def withdraw_screen():
    def withdraw():
        global balance
        amt = int(entry.get())
        if amt > balance: messagebox.showerror("Error","Insufficient Balance"); return
        balance -= amt
        history.append(f"Withdrawn ₹{amt} on {datetime.now().strftime('%d-%m %H:%M')}")
        save_data()
        speak(f"{amt} rupees withdrawn successfully")
        messagebox.showinfo("Success", f"₹{amt} Withdrawn")
        dashboard()
    clear_screen()
    Label(root, text="WITHDRAW AMOUNT", font=("Arial",20,"bold"), bg=C["BG"], fg=C["TEXT"]).pack(pady=50)
    entry = Entry(root, font=("Arial",18)); entry.pack(pady=10)
    Button(root, text="WITHDRAW", command=withdraw, bg=C["RED"], fg="white").pack(pady=10)
    Button(root, text="BACK", command=dashboard, bg=C["BUTTON"], fg="white").pack()

def fast_cash_screen():
    clear_screen()
    Label(root, text="FAST CASH", font=("Arial",20,"bold"), bg=C["BG"], fg=C["TEXT"]).pack(pady=20)
    for amt in [500, 1000, 2000, 5000]:
        Button(root, text=f"₹{amt}", command=lambda a=amt: quick_withdraw(a), bg=C["BUTTON"], fg="white", width=20).pack(pady=5)
    Button(root, text="BACK", command=dashboard, bg=C["BUTTON"], fg="white").pack(pady=10)

def quick_withdraw(amt):
    global balance
    if amt > balance: messagebox.showerror("Error","Insufficient Balance"); return
    balance -= amt
    history.append(f"Fast Cash ₹{amt} on {datetime.now().strftime('%d-%m %H:%M')}")
    save_data()
    speak(f"{amt} rupees withdrawn")
    messagebox.showinfo("Success", f"₹{amt} Withdrawn")
    dashboard()

def history_screen():
    clear_screen()
    speak("Showing last 5 transactions")
    Label(root, text="MINI STATEMENT", font=("Arial",20,"bold"), bg=C["BG"], fg=C["TEXT"]).pack(pady=20)
    for h in history[-5:]:
        Label(root, text=h, font=("Arial",12), bg=C["BG"], fg=C["TEXT"]).pack()
    Button(root, text="BACK", command=dashboard, bg=C["BUTTON"], fg="white").pack(pady=20)

def change_pin_screen():
    def change():
        global pin
        pin = new_pin.get()
        save_data()
        speak("PIN changed successfully")
        messagebox.showinfo("Success","PIN Changed")
        dashboard()
    clear_screen()
    Label(root, text="CHANGE PIN", font=("Arial",20,"bold"), bg=C["BG"], fg=C["TEXT"]).pack(pady=50)
    new_pin = Entry(root, show="*", font=("Arial",18)); new_pin.pack(pady=10)
    Button(root, text="CHANGE", command=change, bg=C["GREEN"], fg="white").pack()
    Button(root, text="BACK", command=dashboard, bg=C["BUTTON"], fg="white").pack()

def qr_payment_screen():
    def generate():
        amt = amount.get()
        qr = qrcode.make(f"UPI PAYMENT TO {name} AMOUNT: {amt}")
        qr.save("qr.png")
        img = Image.open("qr.png").resize((200,200))
        imgtk = ImageTk.PhotoImage(img)
        label.config(image=imgtk); label.image = imgtk
        speak(f"QR code generated for {amt} rupees")
    
    clear_screen()
    Label(root, text="QR PAYMENT", font=("Arial",20,"bold"), bg=C["BG"], fg=C["TEXT"]).pack(pady=20)
    amount = Entry(root, font=("Arial",18)); amount.pack(pady=10)
    Button(root, text="GENERATE QR", command=generate, bg=C["GREEN"], fg="white").pack()
    label = Label(root, bg=C["BG"]); label.pack(pady=20)
    Button(root, text="BACK", command=dashboard, bg=C["BUTTON"], fg="white").pack()

def logout():
    speak("Thank you. Please collect your card")
    messagebox.showinfo("Logout","Logged Out Successfully")
    root.quit()

# ==========================================================
# START
# ==========================================================
loading()
root.mainloop()
