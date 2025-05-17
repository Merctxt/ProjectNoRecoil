import ctypes
import keyboard
import time
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import json
import sys
import os
from pynput.mouse import Listener
from licensing.models import *
from licensing.methods import Key, Helpers
from datetime import datetime

def resource_path(relative_path):
    """Obtem o caminho absoluto para o arquivo de recurso."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MouseInput)]

# Configurações de verificação de licença
RSAPubKey = "<RSAKeyValue><Modulus>pA7QHdfxkrRgJs6QLiA4eApCrl1ftAXouKbMDVfU60NkE0qm34kpC3+nnlHMKDtVA472LeCHS/4Lj3r1SIInrpui3bTIXjhD9if8PQfLNd9Vq1uDEaGauIOSZj+xAJFUqRK7h2KmDYZcxNYPISpF9rdMQSqs3P++igYI6nawp7Vtp7JPKyMROHoXuHUrvBqYufjZXBO6xcDsxoJ+YnU90BoZoLamuX/uVBz2VAr/NXhk3rgbjH6XD4DS3GTO8QdzQrR00eBSqZGFbQjQ2CAPFhWyS70OFSNAj73YOeHfEbVgu8Ky19YZc55XErXkH3h0C7kojaES+6TrvfUiB0C5dQ==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"
auth = "WyIxMDMwMjI4MjkiLCJyNXV5eGtnV3M3TitnRE04c0lJb05waW5nQXR1RkliWWxUK3IyNGpZIl0="
LICENSE_FILE = "license_cache.json"

class LicenseManager:
    @staticmethod
    def save_license(key, machine_code, expires):
        expires_str = expires.strftime('%Y-%m-%d %H:%M:%S')
        with open(LICENSE_FILE, 'w') as f:
            json.dump({'key': key, 'machine_code': machine_code, 'expires': expires_str}, f)

    @staticmethod
    def load_license():
        if not os.path.exists(LICENSE_FILE):
            return None
        with open(LICENSE_FILE, 'r') as f:
            data = json.load(f)
            if 'expires' in data:
                data['expires'] = datetime.strptime(data['expires'], '%Y-%m-%d %H:%M:%S')
                return data
            return json.load(f)

    @staticmethod
    def validate_cached_license():
        cached = LicenseManager.load_license()
        if not cached:
            return False
            
        try:
            result = Key.activate(
                token=auth,
                rsa_pub_key=RSAPubKey,
                product_id='28880',
                key=cached['key'],
                machine_code=cached['machine_code']
            )
            return result[0] and Helpers.IsOnRightMachine(result[0])
        except:
            return False

class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Verificação de Licença")
        self.window.geometry("700x394")
        try:
            self.window.iconbitmap(resource_path("back.ico"))
        except:
            pass
        self.window.configure(bg="black")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        versao = "Versão: 1.0.0"

# Adicionar um label para mostrar a versão no canto inferior direito
        versao_label = tk.Label(self.window, text=versao, font=("Arial", 10), anchor="e", padx=10, bg="black", fg="white")
        versao_label.pack(side="bottom", fill="x")
        self.title_label = tk.Label(self.window, text="""

 ███▄    █  ▒█████      ██▀███  ▓█████  ▄████▄   ▒█████   ██▓ ██▓    
 ██ ▀█   █ ▒██▒  ██▒   ▓██ ▒ ██▒▓█   ▀ ▒██▀ ▀█  ▒██▒  ██▒▓██▒▓██▒    
▓██  ▀█ ██▒▒██░  ██▒   ▓██ ░▄█ ▒▒███   ▒▓█    ▄ ▒██░  ██▒▒██▒▒██░    
▓██▒  ▐▌██▒▒██   ██░   ▒██▀▀█▄  ▒▓█  ▄ ▒▓▓▄ ▄██▒▒██   ██░░██░▒██░    
▒██░   ▓██░░ ████▓▒░   ░██▓ ▒██▒░▒████▒▒ ▓███▀ ░░ ████▓▒░░██░░██████▒
░ ▒░   ▒ ▒ ░ ▒░▒░▒░    ░ ▒▓ ░▒▓░░░ ▒░ ░░ ░▒ ▒  ░░ ▒░▒░▒░ ░▓  ░ ▒░▓  ░
░ ░░   ░ ▒░  ░ ▒ ▒░      ░▒ ░ ▒░ ░ ░  ░  ░  ▒     ░ ▒ ▒░  ▒ ░░ ░ ▒  ░
   ░   ░ ░ ░ ░ ░ ▒       ░░   ░    ░   ░        ░ ░ ░ ▒   ▒ ░  ░ ░   
         ░     ░ ░        ░        ░  ░░ ░          ░ ░   ░      ░  ░
                                       ░                             

""", fg="red", bg="black", font=("Courier", 10, "bold"))
        self.title_label.pack(pady=5)
        

        tk.Label(self.window, text="Insira sua chave de licença:", bg="black", fg="white").pack(pady=10)
        
        self.key_entry = tk.Entry(self.window, width=40)
        self.key_entry.pack(pady=5)
        
        self.status_label = tk.Label(self.window, text="", bg="black", fg="red")
        self.status_label.pack(pady=5)
        
        tk.Button(self.window, text="Ativar", command=self.verify_key).pack(pady=5)
        
        self.window.mainloop()

    def verify_key(self):
        key = self.key_entry.get().strip()
        if not key:
            self.status_label.config(text="Por favor insira uma chave!")
            return

        try:
            machine_code = Helpers.GetMachineCode()
            result = Key.activate(
                token=auth,
                rsa_pub_key=RSAPubKey,
                product_id='28880',
                key=key,
                machine_code=machine_code
            )

            if result[0] and Helpers.IsOnRightMachine(result[0]):
                expires = result[0].expires
                LicenseManager.save_license(key, machine_code, expires)
                self.window.destroy()
                MainApp()
            else:
                messagebox.showerror("Erro", f"Licença inválida: {result[1]}")
                # self.on_close()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na verificação: {str(e)}")
            # self.on_close()

    def on_close(self):
        try:
            self.window.destroy()
        except tk.TclError:
            pass
        sys.exit()



class CustomMenu:
    def __init__(self, master, reset_license_command):
        self.master = master
        self.reset_license_command = reset_license_command

        # Cria um frame que funciona como a barra de menu no topo
        self.menu_frame = tk.Frame(master, bg="black")
        self.menu_frame.pack(fill="x", side="top")

        # Botão principal do menu: "Sistema"
        self.sistema_button = tk.Button(
            self.menu_frame,
            text="Licença",
            bg="black",
            fg="white",
            bd=0,
            activebackground="gray",
            command=self.toggle_dropdown
        )
        self.sistema_button.pack(side="left", padx=10, pady=5)

        # Cria o frame do dropdown (inicialmente não exibido)
        self.dropdown_frame = tk.Frame(master, bg="black", bd=1, relief="solid")
        self.dropdown_visible = False

        # Botão do dropdown: "Alterar Licença"
        self.reset_button = tk.Button(
            self.dropdown_frame,
            text="Alterar Licença",
            bg="gray",
            fg="white",
            bd=0,
            activebackground="gray",
            command=self.reset_license
        )
        self.reset_button.pack(padx=10, pady=5)

    def toggle_dropdown(self):
        if self.dropdown_visible:
            self.dropdown_frame.place_forget()
            self.dropdown_visible = False
        else:
            # Posiciona o dropdown logo abaixo do botão "Sistema"
            # Obtem a posição do botão em relação ao master
            x = self.sistema_button.winfo_x()
            y = self.sistema_button.winfo_y() + self.sistema_button.winfo_height()
            self.dropdown_frame.place(x=x, y=y)
            self.dropdown_visible = True

    def reset_license(self):
        self.reset_license_command(self)
        self.toggle_dropdown()

class MainApp:
    def __init__(self):
        self.DEFAULT_CONFIG = {
            "initial_recoil": 20,
            "max_recoil": 40,
            "single_shoot_recoil": 10,
            "delay_auto": 0.01,
            "delay_single": 0.05,
            "acceleration_factor": 1.8,
            "toggle_key": "p",
            "exit_key": "esc"
        }

        self.config_file = "config.json"
        self.config = self.load_config()

        self.script_ativo = False
        self.mouse_left_pressed = False
        self.time_pressed = 0
        self.initial_recoil = self.config["initial_recoil"]
        self.max_recoil = self.config["max_recoil"]
        self.single_shoot_recoil = self.config["single_shoot_recoil"]
        self.delay_auto = self.config["delay_auto"]
        self.delay_single = self.config["delay_single"]
        self.acceleration_factor = self.config["acceleration_factor"]

        self.mouse_thread = threading.Thread(target=self.listen_for_mouse, daemon=True)
        self.mouse_thread.start()

        self.root = tk.Tk()
        self.root.title("No Recoil")
        self.root.geometry("700x420")
        try:
            self.root.iconbitmap(resource_path("back.ico"))
        except:
            pass
        self.root.configure(bg="black")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.close_script)
        

        self.custom_menu = CustomMenu(self.root, lambda *args: self.reset_license())

        self.create_ui()
        self.rebind_hotkeys()

        self.update_expiry_label()

        self.script_thread = threading.Thread(target=self.run_script, daemon=True)
        self.script_thread.start()


        self.root.mainloop()


    def reset_license(self):
        try:
            os.remove(LICENSE_FILE)
            messagebox.showinfo("Licença", "Licença removida. Reinicie o aplicativo.")
            self.close_script()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover licença: {str(e)}")

    def update_expiry_label(self):
        license_data = LicenseManager.load_license()
        if license_data and 'expires' in license_data:
            formatted_expires = license_data['expires'].strftime('%d/%m/%Y %H:%M:%S')
            self.expiry_label.config(text=f"Data de Expiração: {formatted_expires}")
        else:
            self.expiry_label.config(text="Licença não encontrada.")

    

    def create_ui(self):
        self.expiry_label = tk.Label(self.root, text="Data de Expiração: ", fg="white", bg="black", font=("Arial", 10))
        self.expiry_label.pack(side="top", pady=1)

        self.title_label = tk.Label(self.root, text="""

 ███▄    █  ▒█████      ██▀███  ▓█████  ▄████▄   ▒█████   ██▓ ██▓    
 ██ ▀█   █ ▒██▒  ██▒   ▓██ ▒ ██▒▓█   ▀ ▒██▀ ▀█  ▒██▒  ██▒▓██▒▓██▒    
▓██  ▀█ ██▒▒██░  ██▒   ▓██ ░▄█ ▒▒███   ▒▓█    ▄ ▒██░  ██▒▒██▒▒██░    
▓██▒  ▐▌██▒▒██   ██░   ▒██▀▀█▄  ▒▓█  ▄ ▒▓▓▄ ▄██▒▒██   ██░░██░▒██░    
▒██░   ▓██░░ ████▓▒░   ░██▓ ▒██▒░▒████▒▒ ▓███▀ ░░ ████▓▒░░██░░██████▒
░ ▒░   ▒ ▒ ░ ▒░▒░▒░    ░ ▒▓ ░▒▓░░░ ▒░ ░░ ░▒ ▒  ░░ ▒░▒░▒░ ░▓  ░ ▒░▓  ░
░ ░░   ░ ▒░  ░ ▒ ▒░      ░▒ ░ ▒░ ░ ░  ░  ░  ▒     ░ ▒ ▒░  ▒ ░░ ░ ▒  ░
   ░   ░ ░ ░ ░ ░ ▒       ░░   ░    ░   ░        ░ ░ ░ ▒   ▒ ░  ░ ░   
         ░     ░ ░        ░        ░  ░░ ░          ░ ░   ░      ░  ░
                                       ░                             

""", fg="red", bg="black", font=("Courier", 10, "bold"))
        self.title_label.pack(pady=5)
        versao = "Versão: 1.0.0"
        versao_label = tk.Label(self.root, text=versao, font=("Arial", 10), anchor="e", padx=10, bg="black", fg="white")
        versao_label.pack(side="bottom", fill="x")

        self.instructions_label = tk.Label(self.root, text=f"[{self.config['toggle_key'].upper()}] - Ativar/Desativar\n[{self.config['exit_key'].upper()}] - Fechar", 
                              fg="white", bg="black", font=("Arial", 10))
        self.instructions_label.pack()

        self.status_label = tk.Label(self.root, text="Status: Desativado", fg="red", bg="black", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=5)

        tk.Button(self.root, text="Configurações", command=self.open_settings).pack(pady=1)

    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def move_mouse_relative(self, x, y):
        input_struct = Input(type=0, mi=MouseInput(dx=x, dy=y, mouseData=0, dwFlags=0x0001, time=0, dwExtraInfo=None))
        ctypes.windll.user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(input_struct))

    def toggle_script(self):
        global script_ativo
        self.script_ativo = not self.script_ativo
        self.status_label.config(text=f"Status: {'Ativado' if self.script_ativo else 'Desativado'}", 
                        fg='green' if self.script_ativo else 'red')

    def on_click(self, x, y, button, pressed):
        global mouse_left_pressed
        if button.name == 'left':
            self.mouse_left_pressed = pressed

    def listen_for_mouse(self):
        with Listener(on_click=self.on_click) as listener:
            listener.join()

    def run_script(self):
        """Método para controlar a execução do script."""
        try:
            while True:
                if self.script_ativo:
                    if self.mouse_left_pressed:
                        self.move_mouse_relative(0, self.single_shoot_recoil)
                        time.sleep(self.delay_single)
                    else:
                        self.time_pressed += 1
                        adjusted_recoil = min(self.initial_recoil + (self.acceleration_factor * self.time_pressed), self.max_recoil)
                        while self.mouse_left_pressed:
                            self.move_mouse_relative(0, adjusted_recoil)
                            time.sleep(self.delay_auto)
                time.sleep(0.01)  # Sleep para evitar uso excessivo de CPU
        except KeyboardInterrupt:
            print("Script encerrado.")

    def rebind_hotkeys(self):
        try:
            keyboard.unhook_all()
        except Exception as e:
            print(f"Erro ao remover hotkeys: {str(e)}")
        
        keyboard.add_hotkey(self.config["toggle_key"], self.toggle_script)
        keyboard.add_hotkey(self.config["exit_key"], self.close_script)
        
        if hasattr(self, 'instructions_label'):
            self.instructions_label.config(text=f"[{self.config['toggle_key'].upper()}] - Ativar/Desativar\n[{self.config['exit_key'].upper()}] - Fechar")

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configurações")
        settings_window.geometry("400x500")
        try:
            settings_window.iconbitmap(resource_path("back.ico"))
        except:
            pass
        settings_window.configure(bg="black")
        settings_window.resizable(False, False)

        def open_advanced_settings():
            advanced_window = tk.Toplevel(settings_window)
            advanced_window.title("Opções Avançadas")
            advanced_window.geometry("350x250")
            try:
                advanced_window.iconbitmap(resource_path("back.ico"))
            except:
                pass
            advanced_window.configure(bg="black")
            advanced_window.resizable(False, False)

            tk.Label(advanced_window, text="Delay Automático:", bg="black", fg="white").pack(pady=5)
            delay_auto_var = tk.Entry(advanced_window)
            delay_auto_var.insert(0, self.config["delay_auto"])
            delay_auto_var.pack(pady=5)

            tk.Label(advanced_window, text="Delay Single Shot:", bg="black", fg="white").pack(pady=5)
            delay_single_var = tk.Entry(advanced_window)
            delay_single_var.insert(0, self.config["delay_single"])
            delay_single_var.pack(pady=5)

            tk.Label(advanced_window, text="Fator de Aceleração:", bg="black", fg="white").pack(pady=5)
            acceleration_var = tk.Entry(advanced_window)
            acceleration_var.insert(0, self.config["acceleration_factor"])
            acceleration_var.pack(pady=5)

            def save_advanced():
                try:
                    self.config["delay_auto"] = float(delay_auto_var.get())
                    self.config["delay_single"] = float(delay_single_var.get())
                    self.config["acceleration_factor"] = float(acceleration_var.get())
                    self.save_config()
                except ValueError:
                    pass
                advanced_window.destroy()

            tk.Button(advanced_window, text="Salvar", command=save_advanced).pack(pady=10)

        def save_and_close():
            try:
                self.config["initial_recoil"] = int(recoil_var.get())
                self.config["max_recoil"] = int(max_recoil_var.get())
                self.config["single_shoot_recoil"] = int(single_shoot_var.get())
                self.config["toggle_key"] = toggle_key_var.get().strip() or self.config["toggle_key"]
                self.config["exit_key"] = exit_key_var.get().strip() or self.config["exit_key"]
                self.save_config()
            except ValueError:
                pass
            self.rebind_hotkeys()
            settings_window.destroy()

        def reset_defaults():
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
            self.rebind_hotkeys()
            settings_window.destroy()
            self.open_settings()

        tk.Label(settings_window, text="Recuo Inicial:", bg="black", fg="white").pack(pady=5)
        recoil_var = tk.Entry(settings_window)
        recoil_var.insert(0, self.config["initial_recoil"])
        recoil_var.pack(pady=5)

        tk.Label(settings_window, text="Recuo Máximo:", bg="black", fg="white").pack(pady=5)
        max_recoil_var = tk.Entry(settings_window)
        max_recoil_var.insert(0, self.config["max_recoil"])
        max_recoil_var.pack(pady=5)

        tk.Label(settings_window, text="Recuo Single Shot:", bg="black", fg="white").pack(pady=5)
        single_shoot_var = tk.Entry(settings_window)
        single_shoot_var.insert(0, self.config["single_shoot_recoil"])
        single_shoot_var.pack(pady=5)

        tk.Label(settings_window, text="Tecla Toggle:", bg="black", fg="white").pack(pady=5)
        toggle_key_var = tk.Entry(settings_window)
        toggle_key_var.insert(0, self.config["toggle_key"])
        toggle_key_var.pack(pady=5)

        tk.Label(settings_window, text="Tecla de Saída:", bg="black", fg="white").pack(pady=5)
        exit_key_var = tk.Entry(settings_window)
        exit_key_var.insert(0, self.config["exit_key"])
        exit_key_var.pack(pady=5)

        tk.Button(settings_window, text="Opções Avançadas", command=open_advanced_settings).pack(pady=10)
        tk.Button(settings_window, text="Salvar", command=save_and_close).pack(pady=5)
        tk.Button(settings_window, text="Restaurar Padrão", command=reset_defaults).pack(pady=5)

    def close_script(self):
        try:
            keyboard.unhook_all()
            self.root.destroy()
        except Exception as e:
            print(f"Erro ao fechar: {str(e)}")
        finally:
            sys.exit()

# Estrutura do INPUT para mouse


# Inicia a aplicação com a verificação de licença
if __name__ == "__main__":
    if LicenseManager.validate_cached_license():
        MainApp().root.mainloop()
    else:
        LoginWindow()