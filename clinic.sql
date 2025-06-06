-- 1. appointment
CREATE TABLE appointment (
    apmt_id INT PRIMARY KEY AUTO_INCREMENT,
    stud_id VARCHAR(30),
    apmt_parent_name VARCHAR(100),
    apmt_contnumber VARCHAR(30),
    apmt_date DATE,
    apmt_purpose VARCHAR(255),
    apmt_status VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME
);

-- 2. current_health_issue
CREATE TABLE current_health_issue (
    chi_id INT PRIMARY KEY AUTO_INCREMENT,
    stud_id VARCHAR(30),
    chi_condition VARCHAR(255),
    chi_detected_date DATE,
    chi_status VARCHAR(50),
    chi_notes TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

-- 3. emergency_hotline
CREATE TABLE emergency_hotline (
    ehotline_id INT PRIMARY KEY AUTO_INCREMENT,
    ehotline_agency_name VARCHAR(100),
    ehotline_contnumber VARCHAR(30),
    ehotline_type VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME
);

-- 4. health_record
CREATE TABLE health_record (
    hr_id INT PRIMARY KEY AUTO_INCREMENT,
    stud_id VARCHAR(30),
    hr_date_recorded DATE,
    hr_height DECIMAL(5,2),
    hr_weight DECIMAL(5,2),
    hr_allergies VARCHAR(255),
    hr_notes TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

-- 5. incident_report
CREATE TABLE incident_report (
    ir_id INT PRIMARY KEY AUTO_INCREMENT,
    stud_id VARCHAR(30),
    ir_date_incident DATE,
    ir_description TEXT,
    ir_action_taken TEXT,
    ir_referral VARCHAR(255),
    ir_follow_up_date DATE,
    created_at DATETIME,
    updated_at DATETIME
);

-- 6. inventory_item
CREATE TABLE inventory_item (
    invitem_id INT PRIMARY KEY AUTO_INCREMENT,
    invitem_name VARCHAR(100),
    invitem_quantity INT,
    invitem_dosage VARCHAR(50),
    invitem_unit VARCHAR(50),
    invitem_expiry_date DATE,
    invitem_status VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME
);

-- 7. medical_history
CREATE TABLE medical_history (
    medhist_id INT PRIMARY KEY AUTO_INCREMENT,
    stud_id VARCHAR(30),
    medhist_condition VARCHAR(255),
    medhist_diagnosis_date DATE,
    medhist_notes TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    medhist_photo VARCHAR(255)
);

-- 8. medication
CREATE TABLE medication (
    med_id INT PRIMARY KEY AUTO_INCREMENT,
    stud_id VARCHAR(30),
    med_name VARCHAR(100),
    med_dosage VARCHAR(50),
    med_frequency VARCHAR(50),
    med_start_date DATE,
    med_end_date DATE,
    notes TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

-- 9. section
CREATE TABLE section (
    section_id INT PRIMARY KEY AUTO_INCREMENT,
    section_name VARCHAR(100),
    year_level_id INT
);

-- 10. storage_history
CREATE TABLE storage_history (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    invitem_id INT,
    action VARCHAR(50),
    quantity_before INT,
    quantity_after INT,
    change INT,
    dispensed_to_student_id VARCHAR(30),
    dispensed_date DATE,
    details TEXT,
    created_at DATETIME
);

-- 11. student
CREATE TABLE student (
    stud_id VARCHAR(30) PRIMARY KEY,
    stud_fname VARCHAR(100),
    stud_lname VARCHAR(100),
    stud_dob DATE,
    stud_gender VARCHAR(10),
    year_level_id INT,
    section_id INT,
    stud_email_add VARCHAR(100),
    stud_address VARCHAR(255),
    stud_parent_fname VARCHAR(100),
    stud_parent_lname VARCHAR(100),
    stud_parent_contnum VARCHAR(30),
    stud_status VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME
);

-- 12. year_level
CREATE TABLE year_level (
    year_level_id INT PRIMARY KEY AUTO_INCREMENT,
    year_level_name VARCHAR(50)
);
