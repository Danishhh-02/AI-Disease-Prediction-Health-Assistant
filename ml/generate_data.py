import os
import random
import pandas as pd
import numpy as numpy

def generate_medical_dataset():
    os.makedirs("data", exist_ok=True)
    
    # List of 132 standard symptom features
    symptoms = [
        "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing", "shivering",
        "chills", "joint_pain", "stomach_pain", "acidity", "ulcers_on_tongue",
        "muscle_wasting", "vomiting", "burning_micturition", "spotting_urination", "fatigue",
        "weight_gain", "anxiety", "cold_hands_and_feets", "mood_swings", "weight_loss",
        "restlessness", "lethargy", "patches_in_throat", "irregular_sugar_level", "cough",
        "high_fever", "sunken_eyes", "breathlessness", "sweating", "dehydration",
        "indigestion", "headache", "yellowish_skin", "dark_urine", "nausea",
        "loss_of_appetite", "pain_behind_the_eyes", "back_pain", "constipation", "abdominal_pain",
        "diarrhoea", "mild_fever", "yellow_urine", "yellowing_of_eyes", "acute_liver_failure",
        "fluid_overload", "swelling_of_stomach", "swelled_lymph_nodes", "malaise", "blurred_and_distorted_vision",
        "phlegm", "throat_irritation", "redness_of_eyes", "sinus_pressure", "runny_nose",
        "congestion", "chest_pain", "weakness_in_limbs", "fast_heart_rate", "pain_during_bowel_movements",
        "pain_in_anal_region", "bloody_stool", "irritation_in_anus", "neck_pain", "dizziness",
        "cramps", "bruising", "obesity", "swollen_legs", "swollen_blood_vessels",
        "puffy_face_and_eyes", "enlarged_thyroid", "brittle_nails", "swollen_extremeties", "excessive_hunger",
        "extra_marital_contacts", "drying_and_tingling_lips", "slurred_speech", "knee_pain", "hip_joint_pain",
        "muscle_weakness", "stiff_neck", "swelling_joints", "movement_stiffness", "spinning_movements",
        "loss_of_balance", "unsteadiness", "weakness_of_one_body_side", "loss_of_smell", "bladder_discomfort",
        "foul_smell_of_urine", "continuous_feel_of_urine", "passage_of_gases", "internal_itching", "toxic_look_(typhos)",
        "depression", "irritability", "muscle_pain", "altered_sensorium", "red_spots_over_body",
        "belly_pain", "abnormal_menstruation", "dischromic_patches", "watering_from_eyes", "increased_appetite",
        "polyuria", "family_history", "mucoid_sputum", "rusty_sputum", "lack_of_concentration",
        "visual_disturbances", "receiving_blood_transfusion", "receiving_unsterile_injections", "coma", "stomach_bleeding",
        "distention_of_abdomen", "history_of_alcohol_consumption", "blood_in_sputum", "prominent_veins_on_calf", "palpitations",
        "painful_walking", "pus_filled_pimples", "blackheads", "scurring", "skin_peeling",
        "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails", "blister", "red_sore_around_nose",
        "yellow_crust_ooze"
    ]

    # Map of 41 Diseases and their core characteristic primary and secondary symptoms
    disease_symptom_map = {
        "Fungal infection": ["itching", "skin_rash", "nodal_skin_eruptions", "dischromic_patches"],
        "Allergy": ["continuous_sneezing", "shivering", "chills", "watering_from_eyes"],
        "GERD": ["acidity", "ulcers_on_tongue", "stomach_pain", "cough", "chest_pain"],
        "Chronic cholestasis": ["itching", "yellowish_skin", "nausea", "loss_of_appetite", "yellowing_of_eyes"],
        "Drug Reaction": ["itching", "skin_rash", "stomach_pain", "burning_micturition", "spotting_urination"],
        "Peptic ulcer disease": ["stomach_pain", "acidity", "indigestion", "loss_of_appetite", "abdominal_pain"],
        "AIDS": ["muscle_wasting", "patches_in_throat", "high_fever", "extra_marital_contacts"],
        "Diabetes": ["fatigue", "weight_loss", "restlessness", "lethargy", "irregular_sugar_level", "excessive_hunger", "polyuria"],
        "Gastroenteritis": ["vomiting", "sunken_eyes", "dehydration", "diarrhoea"],
        "Bronchial Asthma": ["fatigue", "cough", "high_fever", "breathlessness", "mucoid_sputum"],
        "Hypertension": ["headache", "chest_pain", "dizziness", "loss_of_balance", "lack_of_concentration"],
        "Migraine": ["acidity", "indigestion", "headache", "blurred_and_distorted_vision", "excessive_hunger", "stiff_neck", "depression", "irritability"],
        "Cervical spondylosis": ["back_pain", "neck_pain", "dizziness", "loss_of_balance"],
        "Paralysis (brain hemorrhage)": ["vomiting", "headache", "weakness_of_one_body_side", "altered_sensorium"],
        "Jaundice": ["itching", "vomiting", "fatigue", "weight_loss", "high_fever", "yellowish_skin", "dark_urine", "abdominal_pain"],
        "Malaria": ["chills", "vomiting", "high_fever", "sweating", "headache", "nausea", "muscle_pain"],
        "Chicken pox": ["itching", "skin_rash", "fatigue", "lethargy", "high_fever", "headache", "loss_of_appetite", "mild_fever", "swelled_lymph_nodes", "malaise", "red_spots_over_body"],
        "Dengue": ["skin_rash", "chills", "joint_pain", "vomiting", "fatigue", "high_fever", "headache", "nausea", "loss_of_appetite", "pain_behind_the_eyes", "back_pain", "muscle_pain", "red_spots_over_body"],
        "Typhoid": ["chills", "vomiting", "fatigue", "high_fever", "headache", "nausea", "loss_of_appetite", "toxic_look_(typhos)", "belly_pain"],
        "Hepatitis A": ["joint_pain", "vomiting", "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "abdominal_pain", "diarrhoea", "mild_fever", "yellowing_of_eyes", "muscle_pain"],
        "Hepatitis B": ["itching", "fatigue", "lethargy", "yellowish_skin", "dark_urine", "loss_of_appetite", "yellowing_of_eyes", "receiving_blood_transfusion", "receiving_unsterile_injections"],
        "Hepatitis C": ["fatigue", "yellowish_skin", "nausea", "loss_of_appetite", "yellowing_of_eyes", "family_history"],
        "Hepatitis D": ["joint_pain", "vomiting", "fatigue", "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes"],
        "Hepatitis E": ["joint_pain", "vomiting", "fatigue", "high_fever", "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "abdominal_pain", "yellowing_of_eyes", "acute_liver_failure"],
        "Alcoholic hepatitis": ["vomiting", "yellowish_skin", "abdominal_pain", "swelling_of_stomach", "history_of_alcohol_consumption", "fluid_overload"],
        "Tuberculosis": ["chills", "vomiting", "fatigue", "weight_loss", "cough", "high_fever", "breathlessness", "sweating", "loss_of_appetite", "mild_fever", "phlegm", "swelled_lymph_nodes", "malaise", "phlegm", "blood_in_sputum"],
        "Common Cold": ["continuous_sneezing", "chills", "fatigue", "cough", "high_fever", "headache", "swelled_lymph_nodes", "malaise", "phlegm", "throat_irritation", "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion", "chest_pain", "loss_of_smell", "muscle_pain"],
        "Pneumonia": ["chills", "fatigue", "cough", "high_fever", "breathlessness", "sweating", "malaise", "phlegm", "chest_pain", "fast_heart_rate", "rusty_sputum"],
        "Dimorphic hemorrhoids (piles)": ["constipation", "pain_during_bowel_movements", "pain_in_anal_region", "bloody_stool", "irritation_in_anus"],
        "Heart attack": ["vomiting", "breathlessness", "sweating", "chest_pain"],
        "Varicose veins": ["fatigue", "cramps", "bruising", "obesity", "swollen_legs", "swollen_blood_vessels", "prominent_veins_on_calf"],
        "Hypothyroidism": ["fatigue", "weight_gain", "cold_hands_and_feets", "mood_swings", "lethargy", "dizziness", "puffy_face_and_eyes", "enlarged_thyroid", "brittle_nails", "swollen_extremeties", "depression", "irritability"],
        "Hyperthyroidism": ["fatigue", "mood_swings", "weight_loss", "restlessness", "sweating", "diarrhoea", "fast_heart_rate", "excessive_hunger", "muscle_weakness", "irritability", "abnormal_menstruation"],
        "Hypoglycemia": ["vomiting", "fatigue", "anxiety", "sweating", "headache", "nausea", "blurred_and_distorted_vision", "excessive_hunger", "drying_and_tingling_lips", "slurred_speech", "irritability", "palpitations"],
        "Osteoarthritis": ["joint_pain", "neck_pain", "knee_pain", "hip_joint_pain", "swelling_joints", "painful_walking"],
        "Arthritis": ["muscle_wasting", "stiff_neck", "swelling_joints", "movement_stiffness", "painful_walking"],
        "(vertigo) Paroxysmal Positional Vertigo": ["vomiting", "headache", "nausea", "spinning_movements", "loss_of_balance", "unsteadiness"],
        "Acne": ["skin_rash", "pus_filled_pimples", "blackheads", "scurring"],
        "Urinary tract infection": ["burning_micturition", "spotting_urination", "bladder_discomfort", "foul_smell_of_urine", "continuous_feel_of_urine"],
        "Psoriasis": ["skin_rash", "joint_pain", "skin_peeling", "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails"],
        "Impetigo": ["skin_rash", "high_fever", "blister", "red_sore_around_nose", "yellow_crust_ooze"]
    }

    random.seed(42)
    rows = []
    
    # Generate 120 samples per disease = 4920 total rows
    samples_per_disease = 120

    for disease, core_symptoms in disease_symptom_map.items():
        for _ in range(samples_per_disease):
            row = {sym: 0 for sym in symptoms}
            row["prognosis"] = disease
            
            # Select 70-100% of core symptoms
            num_core = max(1, int(len(core_symptoms) * random.uniform(0.7, 1.0)))
            selected_core = random.sample(core_symptoms, num_core)
            for sym in selected_core:
                if sym in row:
                    row[sym] = 1
            
            # Add 0-2 noisy non-core symptoms with low probability
            other_symptoms = [s for s in symptoms if s not in core_symptoms]
            num_noise = random.choices([0, 1, 2], weights=[0.75, 0.20, 0.05])[0]
            for sym in random.sample(other_symptoms, num_noise):
                row[sym] = 1
                
            rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv("data/dataset.csv", index=False)
    print(f"Generated dataset with {len(df)} rows, {len(symptoms)} symptom features, and {df['prognosis'].nunique()} classes.")

if __name__ == "__main__":
    generate_medical_dataset()
