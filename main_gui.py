import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from breast_cancer_model import predict_breast_cancer
import sklearn.datasets

# Load feature names from dataset
feature_names = sklearn.datasets.load_breast_cancer().feature_names

# Global user info
current_user = {"name": ""}

class LoginSignupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("User Access")
        self.geometry("400x300")
        self.configure(bg='#e6f2ff')
        self.show_signup()

    def show_signup(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Sign Up", font=("Helvetica", 18, "bold"), bg='#e6f2ff').pack(pady=10)
        self.name = tk.Entry(self, width=30)
        self.userid = tk.Entry(self, width=30)
        self.password = tk.Entry(self, width=30, show='*')

        tk.Label(self, text="Full Name", bg='#e6f2ff').pack()
        self.name.pack()
        tk.Label(self, text="User ID", bg='#e6f2ff').pack()
        self.userid.pack()
        tk.Label(self, text="Password", bg='#e6f2ff').pack()
        self.password.pack()

        tk.Button(self, text="Sign Up", bg="#4CAF50", fg="white", command=self.save_user).pack(pady=10)

    def save_user(self):
        name = self.name.get()
        uid = self.userid.get()
        pwd = self.password.get()

        if name and uid and pwd:
            conn = sqlite3.connect("cancer_data.db")
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, userid TEXT PRIMARY KEY, password TEXT)")
            try:
                cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (name, uid, pwd))
                conn.commit()
                messagebox.showinfo("Success", "Signup successful")
                self.show_login()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "User ID already exists")
            conn.close()
        else:
            messagebox.showerror("Error", "Please fill all fields")

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Login", font=("Helvetica", 18, "bold"), bg='#e6f2ff').pack(pady=10)
        self.login_userid = tk.Entry(self, width=30)
        self.login_password = tk.Entry(self, width=30, show='*')

        tk.Label(self, text="User ID", bg='#e6f2ff').pack()
        self.login_userid.pack()
        tk.Label(self, text="Password", bg='#e6f2ff').pack()
        self.login_password.pack()

        tk.Button(self, text="Login", bg="#007BFF", fg="white", command=self.verify_login).pack(pady=10)

    def verify_login(self):
        uid = self.login_userid.get()
        pwd = self.login_password.get()

        conn = sqlite3.connect("cancer_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE userid = ? AND password = ?", (uid, pwd))
        result = cursor.fetchone()
        conn.close()

        if result:
            current_user["name"] = result[0]
            self.destroy()
            app = CancerApp()
            app.mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials")

class CancerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Breast Tumor Classification")
        self.geometry("1000x600")

        welcome_msg = f"Welcome {current_user['name']}"
        if current_user['name'].lower() == 'sujit kumar tripathy':
            welcome_msg = "Welcome Sujit Sir 🙏"

        tk.Label(self, text=welcome_msg, font=("Helvetica", 16), bg='#e0f7fa').pack(fill='x')

        self.tabs = ttk.Notebook(self)
        self.predict_frame = ttk.Frame(self.tabs)
        self.history_frame = ttk.Frame(self.tabs)

        self.tabs.add(self.predict_frame, text='Diagnose')
        self.tabs.add(self.history_frame, text='Diagnosis History')
        self.tabs.pack(expand=1, fill='both')

        self.create_predict_tab()
        self.create_history_tab()

    def create_predict_tab(self):
        tk.Label(self.predict_frame, text="Enter Sample ID:").grid(row=0, column=0, padx=5, pady=5)
        self.sample_id_entry = tk.Entry(self.predict_frame)
        self.sample_id_entry.grid(row=0, column=1)
        tk.Button(self.predict_frame, text="Fetch Data", command=self.load_sample).grid(row=0, column=2)

        self.inputs = []
        for i in range(30):
            row, col = divmod(i, 3)
            tk.Label(self.predict_frame, text=feature_names[i]).grid(row=row+1, column=col*2, padx=5, pady=5, sticky='w')
            entry = tk.Entry(self.predict_frame, width=20)
            entry.grid(row=row+1, column=col*2+1, padx=5, pady=5)
            self.inputs.append(entry)

        tk.Button(self.predict_frame, text="Diagnose", command=self.make_prediction).grid(row=12, column=1, pady=10)

    def create_history_tab(self):
        self.history_table = ttk.Treeview(self.history_frame, columns=("id", "diagnosis", "timestamp"), show='headings')
        self.history_table.heading("id", text="Sample ID")
        self.history_table.heading("diagnosis", text="Diagnosis")
        self.history_table.heading("timestamp", text="Timestamp")
        self.history_table.pack(expand=True, fill='both')
        tk.Button(self.history_frame, text="Refresh", command=self.load_history).pack(pady=10)

    def load_sample(self):
        try:
            sample_id = int(self.sample_id_entry.get())
            conn = sqlite3.connect("cancer_data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cancer_data WHERE id = ?", (sample_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                raise ValueError("Sample ID not found")

            feature_values = row[1:]
            for i, value in enumerate(feature_values):
                self.inputs[i].delete(0, tk.END)
                self.inputs[i].insert(0, str(value))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def make_prediction(self):
        try:
            input_data = [float(entry.get()) for entry in self.inputs]
            diagnosis = predict_breast_cancer(input_data)
            messagebox.showinfo("Diagnosis", f"The Breast Cancer is {diagnosis}")

            sample_id = int(self.sample_id_entry.get())
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect("cancer_data.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO diagnoses (id, diagnosis, timestamp) VALUES (?, ?, ?)",
                           (sample_id, diagnosis, timestamp))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Prediction Error", str(e))

    def load_history(self):
        for row in self.history_table.get_children():
            self.history_table.delete(row)

        conn = sqlite3.connect("cancer_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM diagnoses")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.history_table.insert("", tk.END, values=row)

if __name__ == '__main__':
    login_app = LoginSignupApp()
    login_app.mainloop()
