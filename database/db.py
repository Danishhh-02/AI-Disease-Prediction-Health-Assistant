import sqlite3
import uuid
import json
import os
import hashlib
import hmac

DB_FILE = "database/app.db"

def get_password_hash(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ":" + key.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt_hex, key_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False

def get_db_connection():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("database", exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Read and execute schema
    schema_path = "database/schema.sql"
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            cursor.executescript(f.read())

    # Seed Admin and Demo User if not present
    cursor.execute("SELECT * FROM users WHERE email = ?", ("admin@health.ai",))
    if not cursor.fetchone():
        admin_id = str(uuid.uuid4())
        hashed = get_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (id, email, hashed_password, role, is_active) VALUES (?, ?, ?, ?, ?)",
            (admin_id, "admin@health.ai", hashed, "ADMIN", 1)
        )
        cursor.execute(
            "INSERT INTO profiles (id, user_id, full_name, age, gender) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), admin_id, "System Administrator", 35, "Other")
        )

    cursor.execute("SELECT * FROM users WHERE email = ?", ("user@health.ai",))
    if not cursor.fetchone():
        user_id = str(uuid.uuid4())
        hashed = get_password_hash("user123")
        cursor.execute(
            "INSERT INTO users (id, email, hashed_password, role, is_active) VALUES (?, ?, ?, ?, ?)",
            (user_id, "user@health.ai", hashed, "USER", 1)
        )
        cursor.execute(
            "INSERT INTO profiles (id, user_id, full_name, age, gender) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, "Demo Health User", 28, "Female")
        )

    # Seed Symptoms Catalog if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM symptoms")
    if cursor.fetchone()["cnt"] == 0:
        seed_symptoms(cursor)

    # Seed Disease Knowledge Base if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM diseases")
    if cursor.fetchone()["cnt"] == 0:
        seed_diseases(cursor)

    # Seed Demo Predictions if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM predictions")
    if cursor.fetchone()["cnt"] == 0:
        seed_predictions(cursor)

    conn.commit()
    conn.close()
    print("Database initialized and seeded successfully.")

def seed_symptoms(cursor):
    import joblib
    symptom_categories = {
        "itching": ("Itching", "Skin & Allergic"),
        "skin_rash": ("Skin Rash", "Skin & Allergic"),
        "nodal_skin_eruptions": ("Nodal Skin Eruptions", "Skin & Allergic"),
        "dischromic_patches": ("Dischromic Patches", "Skin & Allergic"),
        "red_spots_over_body": ("Red Spots Over Body", "Skin & Allergic"),
        "pus_filled_pimples": ("Pus-filled Pimples", "Skin & Allergic"),
        "blackheads": ("Blackheads", "Skin & Allergic"),
        "scurring": ("Scurring", "Skin & Allergic"),
        "skin_peeling": ("Skin Peeling", "Skin & Allergic"),
        "silver_like_dusting": ("Silver-like Dusting", "Skin & Allergic"),
        "blister": ("Blisters", "Skin & Allergic"),
        "red_sore_around_nose": ("Red Sore Around Nose", "Skin & Allergic"),
        "yellow_crust_ooze": ("Yellow Crust Ooze", "Skin & Allergic"),
        
        "continuous_sneezing": ("Continuous Sneezing", "Respiratory & ENT"),
        "cough": ("Cough", "Respiratory & ENT"),
        "breathlessness": ("Breathlessness / Shortness of Breath", "Respiratory & ENT"),
        "phlegm": ("Phlegm / Mucus", "Respiratory & ENT"),
        "throat_irritation": ("Throat Irritation", "Respiratory & ENT"),
        "sinus_pressure": ("Sinus Pressure", "Respiratory & ENT"),
        "runny_nose": ("Runny Nose", "Respiratory & ENT"),
        "congestion": ("Nasal Congestion", "Respiratory & ENT"),
        "patches_in_throat": ("Patches in Throat", "Respiratory & ENT"),
        "mucoid_sputum": ("Mucoid Sputum", "Respiratory & ENT"),
        "rusty_sputum": ("Rusty Sputum", "Respiratory & ENT"),
        "blood_in_sputum": ("Blood in Sputum", "Respiratory & ENT"),
        "loss_of_smell": ("Loss of Smell", "Respiratory & ENT"),

        "stomach_pain": ("Stomach Pain", "Gastrointestinal"),
        "acidity": ("Acidity / Heartburn", "Gastrointestinal"),
        "ulcers_on_tongue": ("Ulcers on Tongue", "Gastrointestinal"),
        "vomiting": ("Vomiting", "Gastrointestinal"),
        "indigestion": ("Indigestion", "Gastrointestinal"),
        "nausea": ("Nausea", "Gastrointestinal"),
        "constipation": ("Constipation", "Gastrointestinal"),
        "abdominal_pain": ("Abdominal Pain", "Gastrointestinal"),
        "diarrhoea": ("Diarrhea", "Gastrointestinal"),
        "pain_during_bowel_movements": ("Pain During Bowel Movements", "Gastrointestinal"),
        "pain_in_anal_region": ("Pain in Anal Region", "Gastrointestinal"),
        "bloody_stool": ("Bloody Stool", "Gastrointestinal"),
        "irritation_in_anus": ("Irritation in Anus", "Gastrointestinal"),
        "passage_of_gases": ("Passage of Gases / Flatulence", "Gastrointestinal"),
        "belly_pain": ("Belly Pain", "Gastrointestinal"),
        "stomach_bleeding": ("Stomach Bleeding", "Gastrointestinal"),
        "distention_of_abdomen": ("Distention of Abdomen", "Gastrointestinal"),
        "swelling_of_stomach": ("Swelling of Stomach", "Gastrointestinal"),
        "increased_appetite": ("Increased Appetite", "Gastrointestinal"),
        "loss_of_appetite": ("Loss of Appetite", "Gastrointestinal"),

        "shivering": ("Shivering", "General & Systemic"),
        "chills": ("Chills", "General & Systemic"),
        "fatigue": ("Fatigue", "General & Systemic"),
        "weight_gain": ("Weight Gain", "General & Systemic"),
        "weight_loss": ("Weight Loss", "General & Systemic"),
        "lethargy": ("Lethargy", "General & Systemic"),
        "high_fever": ("High Fever", "General & Systemic"),
        "mild_fever": ("Mild Fever", "General & Systemic"),
        "sunken_eyes": ("Sunken Eyes", "General & Systemic"),
        "sweating": ("Excessive Sweating", "General & Systemic"),
        "dehydration": ("Dehydration", "General & Systemic"),
        "yellowish_skin": ("Yellowish Skin", "General & Systemic"),
        "yellowing_of_eyes": ("Yellowing of Eyes", "General & Systemic"),
        "dark_urine": ("Dark Urine", "General & Systemic"),
        "yellow_urine": ("Yellow Urine", "General & Systemic"),
        "swelled_lymph_nodes": ("Swelled Lymph Nodes", "General & Systemic"),
        "malaise": ("General Malaise / Unease", "General & Systemic"),
        "fluid_overload": ("Fluid Overload", "General & Systemic"),
        "toxic_look_(typhos)": ("Toxic Look (Typhos)", "General & Systemic"),

        "headache": ("Headache", "Neurological & Mental"),
        "dizziness": ("Dizziness", "Neurological & Mental"),
        "anxiety": ("Anxiety", "Neurological & Mental"),
        "mood_swings": ("Mood Swings", "Neurological & Mental"),
        "restlessness": ("Restlessness", "Neurological & Mental"),
        "blurred_and_distorted_vision": ("Blurred / Distorted Vision", "Neurological & Mental"),
        "slurred_speech": ("Slurred Speech", "Neurological & Mental"),
        "spinning_movements": ("Spinning Movements / Vertigo", "Neurological & Mental"),
        "loss_of_balance": ("Loss of Balance", "Neurological & Mental"),
        "unsteadiness": ("Unsteadiness", "Neurological & Mental"),
        "weakness_of_one_body_side": ("Weakness of One Body Side", "Neurological & Mental"),
        "depression": ("Depression", "Neurological & Mental"),
        "irritability": ("Irritability", "Neurological & Mental"),
        "altered_sensorium": ("Altered Sensorium / Confusion", "Neurological & Mental"),
        "lack_of_concentration": ("Lack of Concentration", "Neurological & Mental"),
        "visual_disturbances": ("Visual Disturbances", "Neurological & Mental"),
        "coma": ("Coma / Loss of Consciousness", "Neurological & Mental"),

        "joint_pain": ("Joint Pain", "Musculoskeletal"),
        "muscle_wasting": ("Muscle Wasting", "Musculoskeletal"),
        "back_pain": ("Back Pain", "Musculoskeletal"),
        "neck_pain": ("Neck Pain", "Musculoskeletal"),
        "cramps": ("Muscle Cramps", "Musculoskeletal"),
        "knee_pain": ("Knee Pain", "Musculoskeletal"),
        "hip_joint_pain": ("Hip Joint Pain", "Musculoskeletal"),
        "muscle_weakness": ("Muscle Weakness", "Musculoskeletal"),
        "stiff_neck": ("Stiff Neck", "Musculoskeletal"),
        "swelling_joints": ("Swelling Joints", "Musculoskeletal"),
        "movement_stiffness": ("Movement Stiffness", "Musculoskeletal"),
        "muscle_pain": ("Muscle Pain", "Musculoskeletal"),
        "painful_walking": ("Painful Walking", "Musculoskeletal"),

        "chest_pain": ("Chest Pain", "Cardiovascular & Vascular"),
        "fast_heart_rate": ("Fast Heart Rate / Tachycardia", "Cardiovascular & Vascular"),
        "palpitations": ("Heart Palpitations", "Cardiovascular & Vascular"),
        "cold_hands_and_feets": ("Cold Hands and Feet", "Cardiovascular & Vascular"),
        "swollen_legs": ("Swollen Legs", "Cardiovascular & Vascular"),
        "swollen_blood_vessels": ("Swollen Blood Vessels", "Cardiovascular & Vascular"),
        "prominent_veins_on_calf": ("Prominent Veins on Calf", "Cardiovascular & Vascular"),

        "burning_micturition": ("Burning Micturition / Urination", "Urinary & Endocrine"),
        "spotting_urination": ("Spotting During Urination", "Urinary & Endocrine"),
        "bladder_discomfort": ("Bladder Discomfort", "Urinary & Endocrine"),
        "foul_smell_of_urine": ("Foul Smell of Urine", "Urinary & Endocrine"),
        "continuous_feel_of_urine": ("Continuous Urge to Urinate", "Urinary & Endocrine"),
        "polyuria": ("Excessive Urination (Polyuria)", "Urinary & Endocrine"),
        "irregular_sugar_level": ("Irregular Sugar Level", "Urinary & Endocrine"),
        "excessive_hunger": ("Excessive Hunger", "Urinary & Endocrine"),
        "enlarged_thyroid": ("Enlarged Thyroid", "Urinary & Endocrine"),
        "abnormal_menstruation": ("Abnormal Menstruation", "Urinary & Endocrine")
    }

    try:
        data = joblib.load("models/encoder.pkl")
        all_features = data["feature_names"]
    except Exception:
        all_features = list(symptom_categories.keys())

    for feat in all_features:
        disp, cat = symptom_categories.get(feat, (feat.replace("_", " ").title(), "General"))
        cursor.execute(
            "INSERT INTO symptoms (id, name, display_name, category, description) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), feat, disp, cat, f"Clinical feature representation of {disp}.")
        )

def seed_diseases(cursor):
    import joblib
    disease_info_data = {
        "Fungal infection": {
            "overview": "A common skin condition caused by microscopic fungi multiplying on warm, moist skin areas.",
            "common_symptoms": ["Itching", "Skin Rash", "Nodal Skin Eruptions", "Dischromic Patches"],
            "precautions": ["Keep affected skin clean and dry.", "Avoid sharing towels, clothes, or personal items.", "Wear breathable cotton clothing."],
            "when_to_seek_help": "Seek medical evaluation if rash spreads rapidly, becomes painful, or exhibits signs of bacterial secondary infection.",
            "source": "World Health Organization (WHO) Dermatology Guidelines"
        },
        "Allergy": {
            "overview": "An immune system response to environmental substances such as pollen, dust mites, or pet dander.",
            "common_symptoms": ["Continuous Sneezing", "Shivering", "Chills", "Watering from Eyes"],
            "precautions": ["Identify and avoid known allergen triggers.", "Keep indoor environments clean and well-ventilated.", "Use air purifiers if necessary."],
            "when_to_seek_help": "Seek emergency care immediately if experiencing shortness of breath, wheezing, swelling of lips/tongue (anaphylaxis).",
            "source": "Global Allergy & Asthma European Network"
        },
        "GERD": {
            "overview": "Gastroesophageal Reflux Disease occurs when stomach acid frequently flows back into the tube connecting mouth and stomach.",
            "common_symptoms": ["Acidity", "Ulcers on tongue", "Stomach Pain", "Cough", "Chest Pain"],
            "precautions": ["Eat smaller, more frequent meals.", "Avoid lying down for 3 hours after eating.", "Limit fatty, spicy, or acidic foods."],
            "when_to_seek_help": "Consult a gastroenterologist if experiencing difficulty swallowing or chronic persistent chest pain.",
            "source": "American College of Gastroenterology"
        },
        "Diabetes": {
            "overview": "A metabolic disorder characterized by sustained elevated blood glucose levels.",
            "common_symptoms": ["Fatigue", "Weight Loss", "Excessive Hunger", "Frequent Urination", "Irregular Sugar Level"],
            "precautions": ["Monitor blood glucose levels regularly.", "Follow a low-glycemic balanced diet.", "Engage in regular physical activity."],
            "when_to_seek_help": "Seek medical evaluation for persistent hyper/hypoglycemic symptoms, confusion, or slow-healing wounds.",
            "source": "International Diabetes Federation (IDF)"
        },
        "Hypertension": {
            "overview": "A chronic medical condition in which blood pressure in the arteries is persistently elevated.",
            "common_symptoms": ["Headache", "Chest Pain", "Dizziness", "Loss of Balance"],
            "precautions": ["Reduce daily sodium intake.", "Exercise regularly and manage stress.", "Avoid smoking and excessive alcohol."],
            "when_to_seek_help": "Seek emergency medical care if experiencing severe headache, chest pressure, visual disturbances, or shortness of breath.",
            "source": "American Heart Association (AHA)"
        },
        "Malaria": {
            "overview": "A mosquito-borne infectious disease caused by Plasmodium parasites.",
            "common_symptoms": ["Chills", "High Fever", "Sweating", "Headache", "Nausea", "Vomiting"],
            "precautions": ["Use insecticide-treated bed nets.", "Apply insect repellent.", "Eliminate standing water near living quarters."],
            "when_to_seek_help": "Seek immediate medical evaluation for blood testing and prescribed antimalarial treatment upon onset of cyclical high fever.",
            "source": "Centers for Disease Control and Prevention (CDC)"
        },
        "Dengue": {
            "overview": "A mosquito-borne viral infection causing flu-like illness and potentially severe complications.",
            "common_symptoms": ["High Fever", "Severe Headache", "Pain Behind Eyes", "Joint & Muscle Pain", "Skin Rash"],
            "precautions": ["Prevent mosquito bites using repellents.", "Maintain hydration.", "Avoid NSAIDs like ibuprofen which may increase bleeding risk."],
            "when_to_seek_help": "Seek emergency care if experiencing severe abdominal pain, persistent vomiting, mucosal bleeding, or rapid drop in blood pressure.",
            "source": "WHO Dengue Guidelines"
        },
        "Pneumonia": {
            "overview": "An inflammatory condition of the lung affecting primarily the microscopic air sacs.",
            "common_symptoms": ["Chills", "Cough with Sputum", "High Fever", "Breathlessness", "Chest Pain"],
            "precautions": ["Complete prescribed antimicrobial medication.", "Rest adequately and drink plenty of fluids.", "Avoid smoking."],
            "when_to_seek_help": "Seek urgent medical attention if experiencing high fever, bluish lips, severe shortness of breath, or confusion.",
            "source": "American Lung Association"
        },
        "Tuberculosis": {
            "overview": "A serious infectious bacterial disease that mainly affects the lungs.",
            "common_symptoms": ["Persistent Cough", "Coughing Blood", "Fatigue", "Night Sweats", "Weight Loss", "High Fever"],
            "precautions": ["Follow complete course of DOTS treatment.", "Wear a mask to prevent airborne transmission.", "Maintain good room ventilation."],
            "when_to_seek_help": "Consult a pulmonologist immediately if coughing up blood or experiencing unexplainable weight loss with chronic cough.",
            "source": "WHO Global Tuberculosis Programme"
        },
        "Common Cold": {
            "overview": "A viral infection of the upper respiratory tract involving nose and throat.",
            "common_symptoms": ["Sneezing", "Runny Nose", "Sore Throat", "Congestion", "Mild Fever"],
            "precautions": ["Get adequate rest.", "Stay hydrated with warm fluids.", "Wash hands frequently."],
            "when_to_seek_help": "Consult a doctor if symptoms persist past 10 days or if severe high fever develops.",
            "source": "CDC Upper Respiratory Infection Guidance"
        }
    }

    try:
        data = joblib.load("models/encoder.pkl")
        all_diseases = data["target_names"]
    except Exception:
        all_diseases = list(disease_info_data.keys())

    for disease_name in all_diseases:
        info = disease_info_data.get(disease_name, {
            "overview": f"General educational medical overview for {disease_name}.",
            "common_symptoms": ["Consult a healthcare professional for specific clinical symptom verification."],
            "precautions": ["Maintain clean hygiene and proper hydration.", "Seek guidance from a licensed practitioner."],
            "when_to_seek_help": "Consult a qualified medical doctor if experiencing persistent, high-fever, or debilitating symptoms.",
            "source": "Verified Medical Knowledge Base"
        })

        cursor.execute(
            """INSERT INTO diseases 
               (id, name, description, common_symptoms, precautions, when_to_seek_help, source)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()),
                disease_name,
                info["overview"],
                json.dumps(info["common_symptoms"]),
                json.dumps(info["precautions"]),
                info["when_to_seek_help"],
                info["source"]
            )
        )

def seed_predictions(cursor):
    sample_preds = [
        {
            "user_id": "guest_user",
            "model_version": "Logistic Regression v1.0",
            "input_symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"],
            "predicted_condition": "Fungal infection",
            "prediction_score": 0.942,
            "top_results_json": [
                {"condition": "Fungal infection", "score": 0.942, "percentage": "94.2%"},
                {"condition": "Allergy", "score": 0.038, "percentage": "3.8%"},
                {"condition": "Drug Reaction", "score": 0.012, "percentage": "1.2%"}
            ],
            "created_at": "2026-10-18 10:15:30"
        },
        {
            "user_id": "user_demo_id",
            "model_version": "Logistic Regression v1.0",
            "input_symptoms": ["chills", "high_fever", "headache", "nausea", "muscle_pain"],
            "predicted_condition": "Malaria",
            "prediction_score": 0.915,
            "top_results_json": [
                {"condition": "Malaria", "score": 0.915, "percentage": "91.5%"},
                {"condition": "Dengue", "score": 0.062, "percentage": "6.2%"},
                {"condition": "Typhoid", "score": 0.018, "percentage": "1.8%"}
            ],
            "created_at": "2026-10-17 14:32:10"
        },
        {
            "user_id": "guest_user",
            "model_version": "Logistic Regression v1.0",
            "input_symptoms": ["headache", "visual_disturbances", "acidity", "indigestion"],
            "predicted_condition": "Migraine",
            "prediction_score": 0.884,
            "top_results_json": [
                {"condition": "Migraine", "score": 0.884, "percentage": "88.4%"},
                {"condition": "Hypertension", "score": 0.071, "percentage": "7.1%"},
                {"condition": "Cervical spondylosis", "score": 0.032, "percentage": "3.2%"}
            ],
            "created_at": "2026-10-16 09:40:00"
        }
    ]
    for p in sample_preds:
        pid = str(uuid.uuid4())
        cursor.execute(
            """INSERT INTO predictions (id, user_id, model_version, input_symptoms, predicted_condition, prediction_score, top_results_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (pid, p["user_id"], p["model_version"], json.dumps(p["input_symptoms"]), p["predicted_condition"], p["prediction_score"], json.dumps(p["top_results_json"]), p["created_at"])
        )
        for sym in p["input_symptoms"]:
            cursor.execute(
                "INSERT INTO prediction_symptoms (id, prediction_id, symptom_name) VALUES (?, ?, ?)",
                (str(uuid.uuid4()), pid, sym)
            )

if __name__ == "__main__":
    init_db()
