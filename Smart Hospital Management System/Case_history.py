import json
import os # Import json and os to make file persistence.
from datetime import datetime
from typing import List, Dict, Optional # Import these to complete GUI.
import Search_and_Sort

# Places for case manager.
class Manage():
    def __init__(self,total_beds: int=10, data_file: str="patient_data.json"):
        self.total_beds= total_beds
        self.beds = [None]*total_beds # The state of the beds, None express the empty beds.
        self.name_index=Search_and_Sort.Trie()
        self.data_file=data_file
        self._next_case_id = 1 # Case ID counter.
        self._load_data()

    # Get the information of the patient based on case ID.
    def get_patient_by_id(self, case_id: int) -> Optional[Dict]:
        # Check the patient on beds.
        for bed in self.beds:
            if bed and bed.get("case_id") == case_id:
                return bed.copy()
        # If not found, check the file.
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for record in data:
                if record.get("case_id") == case_id:
                    return record
                
        return None

    
    def _load_data(self): # Load the date from file.
        # Make sure the file if exist.
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = [data]
                    except json.JSONDecodeError:
                        f.seek(0)
                        data = []
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    obj =json.loads(line)
                                    data.append(obj)
                                except json.JSONDecodeError:
                                    print(f"Pass the line which can't explain: {line}")

                for record in data:
                    # Update next case ID.
                    if isinstance(record,dict):
                        case_id = record.get("case_id", 0)
                        if case_id >= self._next_case_id:
                            self._next_case_id= case_id +1

                        patient_name = record.get("name")
                        if patient_name:
                            self.name_index.insert(patient_name, case_id)

                        bed_index = record.get("bed_index")
                        if bed_index is not None and 0 <= bed_index < self.total_beds:
                            self.beds[bed_index] = record
                    else:
                        print(f"record is not dictionary type: {record}")
                print(f"Data loaded successfully, there are {len(data)} loaded.")
            except (IOError, json.JSONDecodeError) as e:
                        print(f"Data loading failed: {e}")
                        self.initialize_db()
        else:
            self.initialize_db()
                            
    #Detect whether there's enough beds for patients to use in this hospital.
    def detect(self) -> int: 
        available_count = 0
        for bed in self.beds:
            if bed is None:
                available_count += 1
        return available_count
                   
    # Write in patient's information.
    def write(self,patient_name: str,patient_disease: str) -> int:  
        if not patient_name.strip():
            raise ValueError("Name cannot be empty!")
        if not patient_disease.strip():
            raise ValueError("The discription of the disease cannot be empty.")
        
        # Check whether there's avaliable beds.
        available_bed = -1
        for i in range(len(self.beds)):
            if self.beds[i] is None:
                available_bed = i
                break
        if available_bed == -1:
            print("There's no beds in the hospital, please send the patient to the nearby hospital which has enough beds.")
            return -1
        
        # Generate the case.
        case_id = self._generate_case_id()
        patient_record = {
            "case_id": case_id,
            "name": patient_name,
            "disease": patient_disease,
            "admission_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bed_index": available_bed,
            "discharged": False,
            "discharged_date": None
        }

        # Update the state of bed.
        self.beds[available_bed] = patient_record
        # Update the name index.
        self.name_index.insert(patient_name, case_id)
        # Save into the file.
        self._save_data()

        print(f"Patint {patient_name} has admitted to hospital, case ID: {case_id}, bed: {available_bed}")
        return case_id

        
    def _save_data(self): #Save the data to file.
        try:
            # Collect all records of the patient.
            all_records = []
            # Collect current patients from the number of beds.
            for bed in self.beds:
                if bed:
                    all_records.append(bed)
            # Write into the file.
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(all_records, f, ensure_ascii=False, indent=2)
            print(f"Data has been saved successfully, {len(all_records)} of records has been saved.")
        except IOError as e:
            print(f"Data saving failed: {e}.")

    # Initialize the database(when the file got damanged or doesn't exist).
    def initialize_db(self):
        print("Initialized the database...")
        self.beds = [None]*self.total_beds
        self.name_index = Search_and_Sort.Trie()
        self._next_case_id = 1
        
        # Create empty data file.
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

        print("Initialization has been succeed.")
        
    def search_patients_by_name_prefix(self, prefix: str) -> List[Dict]:
        # Use Trie index to get corresponding case.
        matching_names = self.name_index.search_prefix(prefix)
        # Find information based on names.
        results = []
        for _, ids in matching_names:
            # Find in beds.
            for case_id in ids:
                patient = self.get_patient_by_id(case_id)
                if patient:
                    results.append(patient)
                    break

        return results
    
    # Update the information of the diseases.
    def update_patient_diseases(self, case_id: int, new_diseases: str) -> bool:
        # Find patients in beds.
        for i in range(len(self.beds)):
            if self.beds[i] and self.beds[i].get("case_id") == case_id:
                # Update the information of the disease.
                self.beds[i]["disease"] = new_diseases
                self.beds[i]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Save to file.
                self._save_data()
                print(f"The information of disease for case ID {case_id} has been updated.")
                return True
        
        print(f"The patient with case ID of {case_id} has not found")
        return True
    
    def get_available_bed_count(self) -> int:
        return self.detect()
    
    # Generate a unique, incrementing case ID.
    def _generate_case_id(self) -> int:
        case_id = self._next_case_id
        self._next_case_id += 1
        return case_id
    
    # Get patient list based on sorted case ID.
    def get_patients_sorted_by_case_id(self) -> List[Dict]:
        # Collect all records of the patient.
        all_patients = []

        for bed in self.beds:
            if bed:
                all_patients.append(bed)

        # Use radix sort over here.
        sorted_patients = Search_and_Sort.RadixSort.sort_objects(
            all_patients,
            key_func= lambda patient: patient.get("case_id", 0)
        )

        #Return patient's information after sorted.
        return sorted_patients
    
    def search_patients_by_disease(self, disease: str) -> List[Dict]:
        results = []
        if not disease or not isinstance(disease, str):
            return results # If the input is empty or not string, return empty list.
        
        disease = disease.strip().lower()
        for bed in self.beds:
            if bed:
                patient_disease = bed.get("disease", "").lower()
                if disease in patient_disease:
                    results.append(bed.copy())
        return results

    def search_patient(self, prefix: str) -> List[Dict]:
        return self.search_patients_by_name_prefix(prefix)
    
    # For patient who has been recovered.
    def discharge_patient(self, case_id: int) -> bool:
        for i in range(len(self.beds)):
            if self.beds[i] and self.beds[i].get("case_id") == case_id:
                # Signed as discharged.
                self.beds[i]["discharged"] = True
                self.beds[i]["discharge_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Delete from name index.
                patient_name = self.beds[i].get("name")
                if patient_name:
                    self.name_index.delete(patient_name, case_id)

                # Empty the beds.
                self.beds[i] = None

                # Save into the file.
                self._save_data()

                print(f"The patient with case ID {case_id} has been discharged.")
                return True
            
    def get_all_patients(self) -> List[Dict]:
        all_patients = []
        for bed in self.beds:
            if bed:
                all_patients.append(bed.copy())
        return all_patients
        
    def get_patient_by_name(self, name: str) -> Optional[Dict]:
        for bed in self.beds:
            if bed and bed.get("name") == name:
                return bed.copy()
        return None
    
    def get_bed_status(self) -> List[Dict]:
        bed_status= []
        for i in range(len(self.beds)):
            status = {
                "bed_index": i,
                "occupied": self.beds[i] is not None,
                "patient": self.beds[i].copy() if self.beds[i] else None
            }
            bed_status.append(status)
        return bed_status
