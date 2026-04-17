import tkinter as tk 
from tkinter import ttk, messagebox, scrolledtext
from Case_history import Manage
from typing import List, Dict, Optional, Any
import datetime

class Doctor:
    # Initialization.
    def __init__(self,name: str, case_manager: Manage, master: Optional[tk.Tk] = None) -> None:
        self.name = name 
        self.case_manager = case_manager
        self.master = master # Quote the main interface.

    def add_patient(self) -> None: # Add new patient's information.
        if not self.master:
            messagebox.showerror("System error", "No quotation of the main interface.")
            return
        # Create input window.
        input_win = tk.Toplevel(self.master)
        input_win.title("Please input patient's information")
        input_win.grab_set() # Create a modal.
        input_win.transient(self.master) # Set as child window of the main window.
        # Input the name.
        ttk.Label(input_win, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_entry = ttk.Entry(input_win, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        name_entry.focus_set() # Set the focus point.
        # Input the discription of the disease.
        ttk.Label(input_win, text="Disease:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        disease_entry =ttk.Entry(input_win, width=30)
        disease_entry.grid(row=1, column=1, padx=10, pady=10)

        # Submit the information of the patient.
        def submit() -> None:
            try:
                name = name_entry.get().strip()
                disease = disease_entry.get().strip()

                # Input confirmation.
                if not name or not disease:
                    messagebox.showerror("Input error", "Name and disease cannnot be empty.")
                    return
                
                if len(name) > 50:
                    messagebox.showerror("Input error", "The name is too long, please remain in 50 characters.")
                    name_entry.focus_set()
                    return
                
                if len(disease) >200:
                    messagebox.showerror("Input error", "The name of the disease is too long, please remain in 200 characters.")
                    return
                
                # Call case manager to add patient.
                case_id = self.case_manager.write(name, disease)
                
                if case_id !=-1:
                    messagebox.showinfo("Operation succeed", f"Patient \"{name}\" has been hospitalized\ncase ID: {case_id}")
                    input_win.destroy()
                else:
                    messagebox.showerror("Operation failed", "There's no beds in the hospital, please send the patient to the nearby hospital which has enough beds.")
            except ValueError as e:
                messagebox.showerror("Input error", str(e))
            except Exception as e:
                messagebox.showerror("System error", f"There's an error when adding the patient: {str(e)}")
    
        # Cancel the operation.
        def cancel() -> None:
            input_win.destroy()
        
        # Frame of the button.
        button_frame = ttk.Frame(input_win)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Submit", command=submit, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=cancel, width=10).pack(side=tk.LEFT, padx=10)

        # Link with "Enter" button to submit.
        input_win.bind('<Return>', lambda event: submit())
    
    # Search the inoformation of a patient.
    def search_case(self) -> None: 
        if not self.master:
            messagebox.showerror("System error", "No quotation of the main interface.")
            return
        
        # Create a search window.
        search_win = tk.Toplevel(self.master)
        search_win.title("Search case")
        search_win.geometry("500x400")
        search_win.grab_set()
        search_win.transient(self.master)

        # Input the search criteria.
        ttk.Label(search_win, text="Search criteria:").grid(row=0,column=0, padx=10, pady=10, sticky="e")

        # Choose the way to search.
        search_type_var = tk.StringVar(value="name")
        search_frame = ttk.Frame(search_win)
        search_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ttk.Radiobutton(search_frame, text="By name", variable=search_type_var, value="name").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(search_frame, text="By case ID", variable=search_type_var, value="id").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(search_frame, text="By disease", variable=search_type_var, value="disease").pack(side=tk.LEFT, padx=5)  
        
        # Input frame for search.
        ttk.Label(search_win, text="Content for search (name/ID/disease: )").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        search_entry = ttk.Entry(search_win, width=40)
        search_entry.grid(row=1, column=1, padx=10, pady=10)

        # Show result.
        result_frame = ttk.Labelframe(search_win, text="Result", padding=10)
        result_frame.grid(row=2,column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configure grid weights.
        search_win.grid_rowconfigure(2, weight=1)
        search_win.grid_columnconfigure(1, weight=1)

        # Create a text frame with scrollbar.
        result_text = scrolledtext.ScrolledText(result_frame, width=60, height=15, wrap=tk.WORD)
        result_text.pack(fill=tk.BOTH, expand=True)

        # Execute search operation.
        def perform_search() -> None:
            try:
                search_content = search_entry.get().strip()
                search_type = search_type_var.get()
                if not search_content:
                    messagebox.showwarning("Input hint", "Please input the content.")
                    return
                result_text.delete(1.0, tk.END) # Clean previous results.

                # Execute based on the way to search.
                if search_type == "name": # Based on name.
                    try:
                        if any(char.isdigit() for char in search_content):
                            raise ValueError("Name should not contain numbers.")
                        patients = self.case_manager.search_patients_by_name_prefix(search_content)
                        if not patients:
                            result_text.insert(tk.END, f"The patient who named in \"{search_content}\" as start has not found.")
                        else:
                            result_text.insert(tk.END, f"{len(patients)} patient(s) found:\n\n")
                            for patient in patients:
                                result_text.insert(tk.END, self.format_patient_info(patient))
                                result_text.insert(tk.END, "-" * 50 + "\n\n")
                    except ValueError as e:
                        messagebox.showerror("Input error", str(e))
                elif search_type == "id": # Based on case id.
                    try:
                        case_id = int(search_content)
                        patient = self.case_manager.get_patient_by_id(case_id)
                        if patient:
                            result_text.insert(tk.END, "The information of the patient has found:\n\n")
                            result_text.insert(tk.END, self.format_patient_info(patient))
                        else:
                            result_text.insert(tk.END, f"The patient with case ID of {case_id} has not found \n")
                    except ValueError:
                        messagebox.showerror("Input error", "Case ID should be a number.")

                elif search_type == "disease": # Search based on disease.
                    try:
                        patients = self.case_manager.search_patients_by_disease(search_content)
                        if not patients:
                            result_text.insert(tk.END, f"No patient found with disease \"{search_content}\".\n")
                        else:
                            result_text.insert(tk.END, f"{len(patients)} patient(s) found:\n\n")
                            for patient in patients:
                                result_text.insert(tk.END, self.format_patient_info(patient))
                    except Exception as e:
                        messagebox.showerror("System error", f"Error during disease search: {str(e)}")
                
            except Exception as e:
                messagebox.showerror("Search error", f"There's error during the search: {str(e)}.")

        # Clear search results.
        def clear_results() -> None:
            result_text.delete(1.0, tk.END)
            search_entry.delete(0, tk.END)
            search_entry.focus_set()

        # Button frame.
        button_frame = ttk.Frame(search_win)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Search", command=perform_search, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Clear", command=clear_results, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Close", command=search_win.destroy, width=10).pack(side=tk.LEFT, padx=10)

        # Link with "Enter" button to submit.
        search_win.bind('<Return>', lambda event: perform_search())
            
    # Discharge the patient if thepatient has been cured.
    def discharge_patient(self) -> None:
        if not self.master:
            messagebox.showerror("System error", "No quotation of the main interface.")
            return
        
        # Create window for discharging.
        discharge_win = tk.Toplevel(self.master)
        discharge_win.title("Discharging")
        discharge_win.geometry("400x150")
        discharge_win.grab_set()
        discharge_win.transient(self.master)
        
        # Input case ID.
        ttk.Label(discharge_win, text="Case ID:").grid(row=0, column=0, padx=10, pady=20, sticky="e")
        case_id_entry = ttk.Entry(discharge_win, width=20)
        case_id_entry.grid(row=0, column=1, padx=10, pady=20)
        case_id_entry.focus_set()
        
        def confirm_discharge() -> None:
            try:
                case_id_str = case_id_entry.get().strip()
                if not case_id_str:
                    messagebox.showerror("Input error", "Please input case ID.")
                    return
                case_id = int(case_id_str)

                # Get the confirm of the patient information.
                patient = self.case_manager.get_patient_by_id(case_id)
                if not patient:
                    messagebox.showerror("Failed", f"The patient with case ID {case_id} has not found.")
                    return
                
                # Confirm the frame.
                patient_name = patient.get("name", "unknown patient")
                confirm = messagebox.askyesno(
                    "Confirm discharge",
                    f"Are you sure to let patient \"{patient_name}\" (case ID: {case_id}) to discharge?"
                )

                if confirm:
                    success = self.case_manager.discharge_patient(case_id)
                    if success:
                        messagebox.showinfo("Discharging succeed", f"Patient \"{patient_name}\" has been discharged successfully.")
                        discharge_win.destroy()
                    else:
                        messagebox.showerror("Discharging failed", "Discharging failed, please check the state of the system.")
                
            except ValueError:
                messagebox.showerror("Input error", "Case ID should be an number.")
            except Exception as e:
                messagebox.showerror("System error", f"There's error when operating discharge, please check the system state.")
        
        # Frame of the button.
        button_frame = ttk.Frame(discharge_win)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Discharge", command=confirm_discharge, width=12).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=discharge_win.destroy, width=12).pack(side=tk.LEFT, padx=10)

        # Link with "Enter" button to submit.
        discharge_win.bind('<Return>', lambda event: confirm_discharge())
         
    # View all patient's information.
    def view_all_patients(self) -> None:
        if not self.master:
            messagebox.showerror("System error", "No quotation of the main interface.")
            return
        
        # Create the window for viewing.
        view_win = tk.Toplevel(self.master)
        view_win.title("All patient's information")
        view_win.geometry("800x600")
        view_win.grab_set()
        view_win.transient(self.master)

        # Create a text frame with scrollbar.
        text_area = scrolledtext.ScrolledText(view_win, width=90, height=30, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True,padx=10, pady=10)

        try:
            # Get all information and sorteb based on case ID.
            patients = self.case_manager.get_patients_sorted_by_case_id()
            if not patients:
                text_area.insert(tk.END, "There's no patient record now\n")
            else:
                text_area.insert(tk.END, f"The number of the patient now is {len(patients)}:\n\n")
                for patient in patients:
                    text_area.insert(tk.END, self.format_patient_info(patient))
                    text_area.insert(tk.END, "=" * 60 + "\n\n")
        
        except Exception as e:
            text_area.insert(tk.END, f"There's an error when getting patient's information: {str(e)}\n")
        
        # Add close button.
        ttk.Button(view_win, text="Close", command=view_win.destroy).pack(pady=10)
    
    # Transform the patient's information as string.
    def format_patient_info(self, patient: Dict[str, Any]) -> str:
        info = []
        info.append(f"Case ID: {patient.get('case_id', 'N/A')}")
        info.append(f"Name: {patient.get('name', 'N/A')}")
        info.append(f"Disease: {patient.get('disease', 'N/A')}")
        info.append(f"Date of admission: {patient.get('admission_date', 'N/A')}")
        bed_index = patient.get("bed_index", None)
        if bed_index is not None and isinstance(bed_index, int):
            info.append(f"Bed number: {bed_index + 1}") # Plus 1 when show it(avoid bed number is 0).
        else:
            info.append("Bed number: N/A")
        info.append(f"State: {'Discharged' if patient.get('discharged', False) else 'In hospital'}")
        
        discharge_date = patient.get('discharge_date')
        if discharge_date:
            info.append(f"Discharge date: {discharge_date}")
        
        return "\n".join(info) + "\n\n"
    
    # Set the quote of the main interface.
    def set_master(self, master: tk.Tk) -> None:
        self.master = master