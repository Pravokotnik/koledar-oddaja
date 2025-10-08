import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import math

# STRUKTURA MESECEV
mesecnaStruktura = {
    0: {"ime": "januar", "dnevi": 31},
    1: {"ime": "februar", "dnevi": 28},
    2: {"ime": "marec", "dnevi": 31},
    3: {"ime": "april", "dnevi": 30},
    4: {"ime": "maj", "dnevi": 31},
    5: {"ime": "junij", "dnevi": 30},
    6: {"ime": "julij", "dnevi": 31},
    7: {"ime": "avgust", "dnevi": 31},
    8: {"ime": "september", "dnevi": 30},
    9: {"ime": "oktober", "dnevi": 31},
    10: {"ime": "november", "dnevi": 30},
    11: {"ime": "december", "dnevi": 31}
}


# POMOŽNE FUNCKIJE

## ali je leto prestopno
def prestopno(leto):
    if leto % 4 == 0 and (leto % 100 != 0 or leto % 400 == 0):
        return True
    return False

## da vemo kateri dan je uporabimo zellerjev algoritem
def zeller(q, m, year):
    days = ["ponedeljek", "torek", "sreda", "četrtek", "petek", "sobota", "nedelja"]
    if (m < 3):
        m += 12
        year -= 1
    
    k = year % 100
    j = year // 100
    #print(q, m, k, j)
    h = (q + math.floor((13 * (m + 1)) / 5) + k + math.floor(k / 4) + math.floor(j / 4) - 2 * j) % 7

    d = (h + 5) % 7 + 1

    # mormo zmanjsat d za 1 zrd indexov
    d -= 1
    return days[d]
    #print(d)

# funkcija ki prebere praznike iz datoteke
## format datoteke: (dan, mesec, ponavlja) --> ce se praznik ponavlja bo ponavlja==True
def prazniki(file):
    prazniki = set()
    try:
        with open(file, "r", encoding="utf-8") as f:
            for vrstica in f:
                deli = vrstica.strip().split(",")
                if len(deli) >= 1:
                    datum = deli[0]
                    ponavlja = deli[1].strip().lower() if len(deli) >= 2 else "p"
                    try:
                        dan = int(datum.split(".")[0])
                        mesec = int(datum.split(".")[1])
                        prazniki.add((dan, mesec, ponavlja == "p"))
                    except ValueError:
                        print(f"Neveljaven datum: {datum}")
                        continue
    except FileNotFoundError:
        pass
    return prazniki


# GLAVNI RAZRED

class Koledar:
    def __init__(self, root):
        self.root = root
        self.root.title("Koledar")

        self.root.geometry("600x450")
        self.root.minsize(600, 400)

        # današnji datum - da lahko dobimo trenuten dan, mesec in leto
        danes = datetime.now()
        self.mesec = danes.month - 1
        self.leto = danes.year

        # okvir
        self.frame = tk.Frame(root, padx=20, pady=20)
        self.frame.pack()

        # naslov --> mesec in leto (combo box + vnos)
        self.title_frame = tk.Frame(self.frame)
        self.title_frame.pack(pady=(0, 20))

        # combobox za izbiro meseca
        vsi_meseci = [mesecnaStruktura[i]['ime'].capitalize() for i in range(12)]
        
        ## dobimo ime trenutnega meseca
        self.trenutni_mesec_ime = tk.StringVar(value=mesecnaStruktura[self.mesec]['ime'].capitalize())
        ## combobox k ima kot text variable trenutno ime meseca, za dropdown pa seznam vseh mesecev
        self.combo_box = ttk.Combobox(self.title_frame, textvariable=self.trenutni_mesec_ime, values=vsi_meseci, state="readonly", font=("Arial", 16), width=12)
        self.combo_box.pack(side=tk.LEFT, padx=(0, 10))
        ## ko user izbere drug mesec se klice funkcija on_month_change
        self.combo_box.bind('<<ComboboxSelected>>', self.on_month_change)

        # vpis leta
        ## spremenimo leto v string
        self.leto_str = tk.StringVar(value=str(self.leto))
        ## naredimo text field za vnos leta, noter je self.leto_str
        self.leto_vnos = tk.Entry(self.title_frame, textvariable=self.leto_str, font=("Arial", 16), width=6, justify='center')
        self.leto_vnos.pack(side=tk.LEFT)
        ## se triggera in klice funckijo on_year_change ob pristisku enter tipke na tipkovnici
        self.leto_vnos.bind('<Return>', self.on_year_change)

        # okvir za dneve
        self.dnevi_frame = tk.Frame(self.frame)
        self.dnevi_frame.pack()

        # input field za datum
        ## naredimo frame za vnos datuma
        self.datum_frame = tk.Frame(self.frame)
        self.datum_frame.pack(pady=(20, 0))
        ## label da pove kaj vpisat
        date_label = tk.Label(self.datum_frame, text="Pojdi na datum:", font=("Arial", 12))
        date_label.pack(side=tk.LEFT, padx=(0, 5))
        ## vnosno polje za datum
        ### datum shranimo kot stirng
        self.vnesen_datum = tk.StringVar()
        ### widget za vnos datuma
        self.datum_vnos = tk.Entry(self.datum_frame, textvariable=self.vnesen_datum, font=("Arial", 12), width=15, justify='center')
        self.datum_vnos.pack(side=tk.LEFT, padx=(0, 5))
        ### se triggera in klice funkcijo on_date_change ob pristisku enter tipke na tipkovnici
        self.datum_vnos.bind('<Return>', self.on_date_change)
        
        ## placeholder funkcionalnost
        ### ko user klikne notri vnosnega polja se placeholder izbrise
        self.datum_vnos.bind('<FocusIn>', self.clear_placeholder)
        ### ko user klikne ven iz vnosnega polja in je prazno se placeholder vrne
        self.datum_vnos.bind('<FocusOut>', self.restore_placeholder)
        ### nastavimo placeholder
        self.datum_vnos.insert(0, "d.m.yyyy")
        self.datum_vnos.config(fg='gray')

        # gumb za potrditev vnosa datuma --> kliče on_date_change
        potrditev = tk.Button(self.datum_frame, text="Pojdi", command=self.on_date_change, font=("Arial", 10))
        potrditev.pack(side=tk.LEFT, padx=(5, 0))

        # preberemo praznike in se shranijo v self.prazniki_set
        self.read_prazniki()

        # kličemo funkcijo za izris koledarja
        self.izris_koledarja()

    def read_prazniki(self):
        self.prazniki_set = prazniki("datumi.txt")
    
    def clear_placeholder(self, event):
        # zbrisemo placeholder, nastavimo barvo na crno
        if self.datum_vnos.get() == "d.m.yyyy":
            self.datum_vnos.delete(0, tk.END)
            self.datum_vnos.config(fg='black')

    def restore_placeholder(self, event):
        # ce je vnosno polje prazno, vrnemo placeholder in nastavimo barvo na sivo
        if self.datum_vnos.get() == "":
            self.datum_vnos.insert(0, "d.m.yyyy")
            self.datum_vnos.config(fg='gray')
    
    def on_month_change(self, event):
        # dobimo ime izbranega meseca
        selected_month = self.trenutni_mesec_ime.get().lower()
        # dobimo index izbranega meseca in to nastavimo za trenutni mesec
        for i in range(12):
            if mesecnaStruktura[i]['ime'] == selected_month:
                self.mesec = i
                break
        
        # se enkrat izrisemo koledar
        for widget in self.dnevi_frame.winfo_children():
            widget.destroy()
        
        self.izris_koledarja()

    def on_year_change(self, event):
        try:
            # dobimo novo leto iz vnosnega polja in spremenimo v int
            novo_leto = int(self.leto_str.get())
            if 1 <= novo_leto <= 9999:  # nek reasonable year range (lahko tudi ne bi bilo tega)
                self.leto = novo_leto
                
                # se enkrat izrisemo koledar
                for widget in self.dnevi_frame.winfo_children():
                    widget.destroy()
                
                self.izris_koledarja()
            else:
                # ce ni v range, resetiramo na trenutno leto
                self.leto_str.set(str(self.leto))
        except ValueError:
            # ce ni stevilka se resetira na trenutno leto
            self.leto_str.set(str(self.leto))

    def on_date_change(self, event=None):
        try:
            # dobimo vnesen datum iz widgeta
            date_input = self.datum_vnos.get().strip()
            
            # skipamo ce je placeholder ali prazen
            if not date_input or date_input == "d.m.yyyy":
                return
                
            # zahtevamo format d.m.yyyy
            parts = date_input.split('.')
            if len(parts) == 3:
                dan, mesec, leto = int(parts[0]), int(parts[1]), int(parts[2])
                self.mesec = mesec - 1
                self.leto = leto
            else:
                raise ValueError("Neveljaven format")
            
            # preverimo ce je mesec veljaven
            if self.mesec < 0 or self.mesec > 11:
                raise ValueError("Neveljaven mesec")
            
            # preverimo ce je dan veljaven
            max_dnevi = mesecnaStruktura[self.mesec]['dnevi']
            if self.mesec == 1 and prestopno(self.leto):
                max_dnevi = 29
            if dan < 1 or dan > max_dnevi:
                raise ValueError("Neveljaven dan")

            # posodobimo UI
            self.trenutni_mesec_ime.set(mesecnaStruktura[self.mesec]['ime'].capitalize())
            self.leto_str.set(str(self.leto))

            # clearamo vnos datuma in restoramo placeholder
            self.datum_vnos.delete(0, tk.END)
            self.restore_placeholder(None)
            
            # odstranimo fokus iz vnosnega polja, da se ne pojavi kursor na nepravem mestu
            self.root.focus()
            
            # ponovno izrisemo koledar
            for widget in self.dnevi_frame.winfo_children():
                widget.destroy()
            self.izris_koledarja()
            
        except (ValueError, IndexError):
            # error message za neveljaven datum
            messagebox.showerror("Napaka", "Neveljaven datum! Uporabi format: d.m.yyyy (npr. 15.12.2024)")
            # clearamo in restoramo placeholder
            self.datum_vnos.delete(0, tk.END)
            self.restore_placeholder(None)
            # odstranimo fokus iz vnosnega polja
            self.root.focus()

    def izris_koledarja(self):

        # dnevi
        dnevi = ["Pon", "Tor", "Sre", "Čet", "Pet", "Sob", "Ned"]
        for i, h in enumerate(dnevi):
            tk.Label(self.dnevi_frame, text=h, font=("Arial", 10, "bold"), width=4, anchor="center").grid(row=0, column=i)

        # preverimo ce je leto prestopno --> ce je prilagodimo februar
        if prestopno(self.leto):
            mesecnaStruktura[1]["dnevi"] = 29
        else:
            mesecnaStruktura[1]["dnevi"] = 28

        # dobimo kateri dan v tednu je prvi dan v mesecu --> zellerjev algoritem
        ## self.mesec je 0-11, zeller pa rabi 1-12
        prvi_dan = zeller(1, self.mesec + 1, self.leto)
        dan_index = ["ponedeljek", "torek", "sreda", "četrtek", "petek", "sobota", "nedelja"].index(prvi_dan)

        # Izris dni
        ## vedno zacnemo s 1. v mesecu
        dan = 1
        ## zacnemo v 1. vrstici
        row = 1
        ## zacnemo v dan_index stolpcu
        col = dan_index
        ## koliko dni v trenutnem mesecu
        total_days = mesecnaStruktura[self.mesec]["dnevi"]

        for i in range(total_days):

            # oznacimo nedelje z rdeco barvo, ostale s crno
            barva = "red" if col == 6 else "black"
            
            # preverimo ce je trenutni dan  praznik
            je_praznik = False
            if (dan, self.mesec + 1, True) in self.prazniki_set:
                je_praznik = True
            if (dan, self.mesec + 1, False) in self.prazniki_set:
                if self.leto == datetime.now().year:
                    je_praznik = True
            
            ## naredimo canvas widget za vsak dan v koledarju
            canvas = tk.Canvas(self.dnevi_frame, width=60, height=40, highlightthickness=0)
            ## postavimo ga v ustrezno vrstico in stolpec
            canvas.grid(row=row, column=col, padx=2, pady=2)
            ## nastavimo barvo ozadja widgeta enako kot okvir
            canvas.configure(bg=self.dnevi_frame.cget('bg'))

            # ce je dan praznik ga obkrožimo z modrim krogom
            if je_praznik:
                canvas.create_oval(16, 1, 43, 28, outline="blue", width=2)

            # napisemo stevilko dneva z ustrezno barvo
            canvas.create_text(30, 15, text=str(dan), fill=barva, font=("Arial", 12))

            # povecamo dan in stolpec ter po moznosti vrstico
            dan += 1
            col += 1
            if col > 6:
                col = 0
                row += 1


# ZAGON
if __name__ == "__main__":
    root = tk.Tk()
    app = Koledar(root)
    root.mainloop()