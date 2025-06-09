-- 1. year_level
CREATE TABLE year_level (
    year_level_id SERIAL PRIMARY KEY,
    year_level_name VARCHAR(50)
);

-- 2. section
CREATE TABLE section (
    section_id SERIAL PRIMARY KEY,
    section_name VARCHAR(100),
    year_level_id INTEGER,
    FOREIGN KEY (year_level_id) REFERENCES year_level(year_level_id)
);

-- 3. student
CREATE TABLE student (
    stud_id VARCHAR(30) PRIMARY KEY,
    stud_fname VARCHAR(100),
    stud_mname VARCHAR(100), 
    stud_lname VARCHAR(100),
    stud_dob DATE,
    stud_gender VARCHAR(10),
    year_level_id INTEGER,
    section_id INTEGER,
    stud_email_add VARCHAR(100),
    stud_address VARCHAR(255),
    stud_parent_fname VARCHAR(100),
    stud_parent_lname VARCHAR(100),
    stud_parent_contnum VARCHAR(30),
    stud_status VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (year_level_id) REFERENCES year_level(year_level_id),
    FOREIGN KEY (section_id) REFERENCES section(section_id)
);

-- 4. appointment
CREATE TABLE appointment (
    apmt_id SERIAL PRIMARY KEY,
    stud_id VARCHAR(30),
    apmt_parent_name VARCHAR(100),
    apmt_contnumber VARCHAR(30),
    apmt_date DATE,
    apmt_purpose VARCHAR(255),
    apmt_status VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (stud_id) REFERENCES student(stud_id)
);

-- 5. current_health_issue
CREATE TABLE current_health_issue (
    chi_id SERIAL PRIMARY KEY,
    stud_id VARCHAR(30),
    chi_condition VARCHAR(255),
    chi_detected_date DATE,
    chi_status VARCHAR(50),
    chi_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (stud_id) REFERENCES student(stud_id)
);

-- 6. emergency_hotline
CREATE TABLE emergency_hotline (
    ehotline_id SERIAL PRIMARY KEY,
    ehotline_agency_name VARCHAR(100),
    ehotline_contnumber VARCHAR(30),
    ehotline_type VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 7. health_record
CREATE TABLE health_record (
    hr_id SERIAL PRIMARY KEY,
    stud_id VARCHAR(30),
    hr_date_recorded DATE,
    hr_height NUMERIC(5,2),
    hr_weight NUMERIC(5,2),
    hr_allergies VARCHAR(255),
    hr_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (stud_id) REFERENCES student(stud_id)
);

-- 8. incident_report
CREATE TABLE incident_report (
    ir_id SERIAL PRIMARY KEY,
    stud_id VARCHAR(30),
    ir_date_incident DATE,
    ir_description TEXT,
    ir_action_taken TEXT,
    ir_referral VARCHAR(255),
    ir_follow_up_date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (stud_id) REFERENCES student(stud_id)
);

-- 9. inventory_item
CREATE TABLE inventory_item (
    invitem_id SERIAL PRIMARY KEY,
    invitem_name VARCHAR(100),
    invitem_quantity INTEGER,
    invitem_dosage VARCHAR(50),
    invitem_unit VARCHAR(50),
    invitem_expiry_date DATE,
    invitem_status VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 10. medical_history
CREATE TABLE medical_history (
    medhist_id SERIAL PRIMARY KEY,
    stud_id VARCHAR(30),
    medhist_condition VARCHAR(255),
    medhist_diagnosis_date DATE,
    medhist_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    medhist_photo VARCHAR(255),
    FOREIGN KEY (stud_id) REFERENCES student(stud_id)
);

-- 11. medication
CREATE TABLE medication (
    med_id SERIAL PRIMARY KEY,
    stud_id VARCHAR(30),
    med_name VARCHAR(100),
    med_dosage VARCHAR(50),
    med_frequency VARCHAR(50),
    med_start_date DATE,
    med_end_date DATE,
    notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (stud_id) REFERENCES student(stud_id)
);

-- 12. storage_history
CREATE TABLE storage_history (
    history_id SERIAL PRIMARY KEY,
    invitem_id INTEGER,
    action VARCHAR(50),
    quantity_before INTEGER,
    quantity_after INTEGER,
    change INTEGER,
    dispensed_to_student_id VARCHAR(30),
    dispensed_date DATE,
    details TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (invitem_id) REFERENCES inventory_item(invitem_id),
    FOREIGN KEY (dispensed_to_student_id) REFERENCES student(stud_id)
);

CREATE TABLE referral (
    referral_id SERIAL PRIMARY KEY,
    stud_id VARCHAR(30),
    referral_date DATE,
    referral_reason VARCHAR(255),
    referral_to VARCHAR(255),
    referral_status VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (stud_id) REFERENCES student(stud_id)
);

CREATE TABLE clinic_visit_log (
    visit_id SERIAL PRIMARY KEY,
    stud_id VARCHAR(30),
    visit_date DATE,
    reason VARCHAR(255),
    time_in TIME,
    time_out TIME,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (stud_id) REFERENCES student(stud_id)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
