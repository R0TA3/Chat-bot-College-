-- ============================================================
-- AI-Powered College Enquiry Chatbot - Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS college_chatbot;
USE college_chatbot;

-- ----------------------------
-- Table: admin
-- ----------------------------
CREATE TABLE IF NOT EXISTS admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------
-- Table: user
-- ----------------------------
CREATE TABLE IF NOT EXISTS user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    session_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------
-- Table: faq
-- ----------------------------
CREATE TABLE IF NOT EXISTS faq (
    faq_id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    keywords TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ----------------------------
-- Table: chat_history
-- ----------------------------
CREATE TABLE IF NOT EXISTS chat_history (
    chat_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    session_id VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    matched_faq_id INT NULL,
    confidence_score FLOAT DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE SET NULL,
    FOREIGN KEY (matched_faq_id) REFERENCES faq(faq_id) ON DELETE SET NULL
);

-- ----------------------------
-- Table: feedback (for unanswered / low-confidence queries)
-- ----------------------------
CREATE TABLE IF NOT EXISTS unanswered_queries (
    query_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100),
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE
);

-- ----------------------------
-- Default Admin (password: admin123 -- hashed in app on first run via seed script)
-- ----------------------------
-- Inserted by seed_data.py instead of plain text here for security.

-- ----------------------------
-- Sample FAQ Data
-- ----------------------------
INSERT INTO faq (question, answer, category, keywords) VALUES
('What courses are available?', 'We offer B.Tech (CSE, ECE, ME, CE, EEE), B.Sc, BCA, MCA, MBA, and Ph.D programs across multiple departments. Visit the admissions office or website for the full list.', 'Courses', 'courses programs degree branches available offered'),
('What is the fee structure?', 'The fee structure varies by course. For example, B.Tech is approximately ₹85,000/year, MCA is ₹60,000/year, and MBA is ₹95,000/year. Please contact the admission office for the latest detailed fee structure.', 'Fees', 'fee fees cost tuition price structure payment'),
('How can I apply for admission?', 'You can apply online through our college website admissions portal, or visit the admission office in person with your academic documents. Applications typically open in May and June each year.', 'Admissions', 'apply admission process how register enroll'),
('What are the eligibility criteria?', 'Eligibility varies by program. For B.Tech, candidates need 12th grade with Physics, Chemistry, and Mathematics with a minimum of 50% marks. For MCA, a Bachelor degree with Mathematics is required. Check specific course pages for detailed criteria.', 'Admissions', 'eligibility criteria requirements qualify minimum marks'),
('Is hostel facility available?', 'Yes, separate hostel facilities are available for boys and girls with mess, Wi-Fi, 24/7 security, and recreational areas. Hostel fees are charged separately from tuition.', 'Hostel', 'hostel accommodation room stay residence facility boys girls'),
('What are the placement opportunities?', 'Our college has a dedicated placement cell with 85%+ placement rate. Top recruiters include TCS, Infosys, Wipro, Cognizant, and several startups. Average package is ₹4.5 LPA with highest packages reaching ₹18 LPA.', 'Placements', 'placement job career recruit company package salary'),
('What scholarship programs are available?', 'We offer merit-based scholarships (up to 50% fee waiver for top performers), government scholarships for SC/ST/OBC students, and need-based financial aid. Contact the scholarship cell for application details.', 'Scholarships', 'scholarship financial aid fee waiver merit grant'),
('What documents are required for admission?', '10th & 12th mark sheets, transfer certificate, migration certificate, passport size photos, Aadhar card, category certificate (if applicable), and entrance exam scorecard (if applicable).', 'Admissions', 'documents required papers certificates needed admission'),
('What is the college contact information?', 'You can reach us at info@college.edu or call +91-9876543210. Our office is open Monday to Saturday, 9 AM to 5 PM. The campus is located in the city center, easily accessible by public transport.', 'Contact', 'contact phone email address location reach office'),
('When do examinations take place?', 'Semester examinations are typically held in November-December (odd semester) and April-May (even semester). The exact schedule is published on the college website and notice board one month in advance.', 'Examinations', 'exam examination schedule test date semester'),
('What is the campus infrastructure like?', 'Our campus features modern smart classrooms, well-equipped labs, a central library with 50,000+ books, sports facilities, an auditorium, cafeteria, and free Wi-Fi across campus.', 'Infrastructure', 'campus infrastructure facilities library labs classroom'),
('Are there transportation facilities?', 'Yes, the college provides bus transportation covering major routes across the city. Bus fees are charged separately per semester based on the route distance.', 'Transportation', 'transport bus transportation commute travel route'),
('What extracurricular activities are offered?', 'We have technical clubs, cultural clubs, sports teams, NCC/NSS units, and host annual fests like TechFest and Cultural Fest. Students are encouraged to join clubs aligned with their interests.', 'Activities', 'extracurricular clubs activities sports fest cultural technical'),
('How do I contact the admission office directly?', 'The admission office can be reached at admissions@college.edu or +91-9876543211, located in the Administrative Block, Room 101, open during working hours.', 'Contact', 'admission office contact direct reach phone email'),
('What is the refund policy for fees?', 'Fee refunds are processed as per UGC/AICTE guidelines. If you withdraw before classes commence, 100% refund minus processing fee applies. Refund percentage decreases as the academic year progresses.', 'Fees', 'refund policy fee withdraw cancellation');
