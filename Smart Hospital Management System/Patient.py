import tkinter as tk 
from tkinter import ttk, messagebox, scrolledtext #  Import tkiner to create a window.
from Case_history import Manage
from typing import Optional, Dict, Any

class Patient:
    def __init__(self, case_manager: Manage, master: Optional[tk.Tk]=None):
        self.case_manager= case_manager
        self.master = master
        self.identity_verified = False
        self.current_case_id = None
        self.current_patient_name = None

        # Create main window.
        if not self.master:
            self.master = tk.Tk()
            self.master.title("Inquire information system for patient")
            self.master.geometry("600x500")

        # Create GUI component.
        self._create_gui()

    def _create_gui(self) -> None:
        # Main frame.
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title.
        title_label = ttk.Label(
            main_frame, 
            text="Inquire information system for patient", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame for identity verify.
        auth_frame = ttk.Labelframe(main_frame, text="Verify identity", padding="15")
        auth_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Case ID input.
        ttk.Label(auth_frame, text="Case ID: ").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.case_id_entry = ttk.Entry(auth_frame, width=25)
        self.case_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Input patient's name.
        ttk.Label(auth_frame, text="Patient's name: ").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(auth_frame, width=25)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Button for verify.
        self.verify_btn = ttk.Button(
            auth_frame, 
            text="Verify identity", 
            command=self.verify_identity,
            width=15
        )
        self.verify_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Frame for showing information.
        info_frame = ttk.Labelframe(main_frame, text="Case information", padding="15")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a text frame with scrollbar.
        self.record_text = scrolledtext.ScrolledText(
            info_frame, 
            width=70, 
            height=15, 
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 10)
        )
        self.record_text.pack(fill=tk.BOTH, expand=True)
        
        # Inquire button (not able to use at start).
        self.query_btn = ttk.Button(
            main_frame,
            text="Find my case",
            command=self.show_record,
            state=tk.DISABLED,
            width=20
        )
        self.query_btn.pack(pady=10)
        
        # Label the status.
        self.status_label = ttk.Label(main_frame, text="Please verify the identity first.", foreground="gray")
        self.status_label.pack()
        
        # Link with "Enter" button to submit.
        self.case_id_entry.bind('<Return>', lambda e: self.verify_identity())
        self.name_entry.bind('<Return>', lambda e: self.verify_identity())

    # Verify the identity.
    def verify_identity(self) -> None:        
        try:
            case_id_str = self.case_id_entry.get().strip()
            name = self.name_entry.get().strip()
            
            # Input verify.
            if not case_id_str:
                messagebox.showwarning("Input error", "Please input case ID.")
                self.case_id_entry.focus_set()
                return
            
            if not name:
                messagebox.showwarning("Input error", "Please input name.")
                self.name_entry.focus_set()
                return
            
            # Verify the format of case ID.
            try:
                case_id = int(case_id_str)
                if case_id <= 0:
                    raise ValueError("Case ID should be a positive integer.")
            except ValueError:
                messagebox.showerror("Input error", "Case ID should be a positive integer.")
                self.case_id_entry.focus_set()
                return
            
            # Get the information from case manager.
            patient_record = self.case_manager.get_patient_by_id(case_id)
            
            if not patient_record:
                messagebox.showerror("Verify failed", f"Patient with case ID {case_id} has not found.")
                self._reset_verification()
                return
            
            # Verify whether it is matched or not.
            record_name = patient_record.get("name", "").strip()
            if record_name.lower() != name.lower():
                messagebox.showerror("Verify failed", "Case ID is not matched with name.")
                self._reset_verification()
                return
            
            # Verify whether the patient has been discharged or not.
            if patient_record.get("discharged", False):
                discharge_date = patient_record.get("discharge_date", "Time unknown")
                messagebox.showwarning(
                    "State of the patient", 
                    f"The patient has been discharged in {discharge_date}\n"
                    "If you want to check history record, please contact to the hospital administrator."
                )
            
            # Verify succeed.
            self.identity_verified = True
            self.current_case_id = case_id
            self.current_patient_name = name
            
            # Upload the state of UI.
            self.query_btn.config(state=tk.NORMAL)
            self.status_label.config(
                text=f"Identity verify succeed - patient: {name} (ID: {case_id})",
                foreground="green"
            )
            
            messagebox.showinfo("Verify succeed", "Identity verify succeed, you can check the information of the case now.")

            # Chow the case.
            self.show_record()
            
        except Exception as e:
            messagebox.showerror("System error", f"There's an error during the verify: {str(e)}")
            self._reset_verification()
    
    # Reset the state of identification.
    def _reset_verification(self) -> None:
        self.identity_verified = False
        self.current_case_id = None
        self.current_patient_name = None
        self.query_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Please verify the identity first.", foreground="gray")
        self.record_text.config(state=tk.NORMAL)
        self.record_text.delete(1.0, tk.END)
        self.record_text.config(state=tk.DISABLED)
    
    def show_record(self) -> None: # Show patient's information.
        if not self.identity_verified or not self.current_case_id:
            messagebox.showerror("Permission error", "Please complete the identity verification.")
            return
        try:
            record = self.case_manager.get_patient_by_id(self.current_case_id)
            if not record:
                messagebox.showerror("Data error", "Inquire case information failed, please verify ifentity again.")
                self._reset_verification()
                return
            
            # Verify the integrity of record verifying.
            required_fields = ["case_id", "name", "disease", "admission_date"]
            for field in required_fields:
                if field not in record:
                    raise ValueError(f"The case is not whole completed, it lacks of: {field}")
            
            # Clear and raady to display.
            self.record_text.config(state=tk.NORMAL)
            self.record_text.delete(1.0, tk.END)
            
            # Format the display information.
            info_lines = []
            info_lines.append("=" * 60)
            info_lines.append("                   Case information")
            info_lines.append("=" * 60)
            info_lines.append("")
            
            # Basic information.
            info_lines.append("[Basic information]")
            info_lines.append(f"  Case ID: {record.get('case_id', 'N/A')}")
            info_lines.append(f"  Name: {record.get('name', 'N/A')}")
            info_lines.append(f"  Date of admission: {record.get('admission_date', 'N/A')}")
            
            # Beds information.
            bed_index = record.get('bed_index')
            if bed_index is not None:
                info_lines.append(f"  Number of the bed: {bed_index + 1}")  # Show as 1-based.
            
            # Disease information.
            info_lines.append("")
            info_lines.append("[Diagnostic information]")
            disease = record.get('disease', 'Not recorded')
            info_lines.append(f"  Diagnosis of diseases: {disease}")
            
            # The state of discharging.
            info_lines.append("")
            info_lines.append("[Status information]")
            discharged = record.get('discharged', False)
            status = "Discharged" if discharged else "In hospital"
            info_lines.append(f"  Current state: {status}")
            
            if discharged:
                discharge_date = record.get('discharge_date')
                if discharge_date:
                    info_lines.append(f"  Date of discharged: {discharge_date}")
            
            # Insert the text.
            for line in info_lines:
                self.record_text.insert(tk.END, line + "\n")
            
            # Set text to read-only.
            self.record_text.config(state=tk.DISABLED)
            
            # Rolling to the top.
            self.record_text.see(1.0)
            
        except ValueError as e:
            messagebox.showerror("Data error", str(e))
            self.record_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("System error", f"There's a error when inquiring the case information: {str(e)}")
            self.record_text.config(state=tk.NORMAL)
            self.record_text.delete(1.0, tk.END)
            self.record_text.insert(tk.END, "The case information cannot be loaded now, please try again later.")
            self.record_text.config(state=tk.DISABLED)
    
    # Get the current time.
    def _get_current_time(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Clear the form.
    def clear_form(self) -> None:
        self.case_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self._reset_verification()
        self.case_id_entry.focus_set()
    
    # Run the interface for patient.
    def run(self) -> None:
        pass