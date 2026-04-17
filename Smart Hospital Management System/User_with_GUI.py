import tkinter as tk 
from tkinter import ttk, messagebox #  Import tkiner to create a window.
from Doctor import Doctor 
from Patient import Patient
from Case_history import Manage # Import class from other three module.

class MainInterface:
    def __init__(self, master):
        self.master = master
        self.master.title("Smart Hospital Management System")
        self.master.geometry("400x300")
        self.current_frame = None
        self.frames = {} # <- Store all frames.
        
        # Instantiate the case manager.
        self.case_manager = Manage(total_beds=10, data_file="patient_data.json")
        
        # Create GUI.
        self._create_widgets()

    def switch_frame(self, frame_name):
        if self.current_frame:
            self.current_frame.pack_forget() # Hide current page.
        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(fill="both", expand=True)
    
    
    def _create_widgets(self):
        # Create the main component for main interface.
        title_label = ttk.Label(self.master, text="Smart Hospital Management System", font=("Arial", 16))
        title_label.pack(pady=20)
        
        doctor_btn = ttk.Button(self.master, text="For doctor", 
                               command=self.open_doctor_interface, width=20)
        doctor_btn.pack(pady=10)
        
        patient_btn = ttk.Button(self.master, text="For patient", 
                                command=self.open_patient_interface, width=20)
        patient_btn.pack(pady=10)
        
        exit_btn = ttk.Button(self.master, text="Quit the system", 
                             command=self.master.quit, width=20)
        exit_btn.pack(pady=10)
        
    def open_doctor_interface(self):
        try:
            doctor_name = "Doctor"
            if not hasattr(self, "doctor"):
                self.doctor = Doctor(doctor_name, self.case_manager, self.master)

            # Create a new child window.
            doctor_win = tk.Toplevel(self.master)
            doctor_win.title("Doctor interface.")
            doctor_win.geometry("300x200")

            ttk.Button(doctor_win, text="Add patient", command=self.doctor.add_patient).pack(pady=10)
            ttk.Button(doctor_win, text="Search case", command=self.doctor.search_case).pack(pady=10)
            ttk.Button(doctor_win, text="Discharge patient", command=self.doctor.discharge_patient).pack(pady=10)
            ttk.Button(doctor_win, text="View all patients", command=self.doctor.view_all_patients).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open doctor interface: {str(e)}")

    def open_patient_interface(self):
        try:
            # Create a new child window.
            patient_win = tk.Toplevel(self.master)
            patient_win.title("Patient interface")
            patient_win.geometry("600x500")

            # Instance Patient in this child window.
            patient = Patient(self.case_manager, patient_win)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open patient interface: {str(e)}")
        


# Entrance for the main program.      
if __name__ == "__main__":
    root= tk.Tk()
    app = MainInterface(root)
    root.mainloop()

