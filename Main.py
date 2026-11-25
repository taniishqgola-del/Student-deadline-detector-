#!/usr/bin/env python3
"""
MRIIRS Campus Assistant  -  GUI Edition
=======================================
A retrieval chatbot for Manav Rachna International Institute of Research and
Studies (MRIIRS), Faridabad.  Pure Python, standard library only
(tkinter, difflib, math, re, webbrowser) - no pip install needed.

Engine : text cleaning -> synonyms -> spelling fix -> TF-IDF -> cosine similarity
Extras : campus-block lookup, "did you mean" suggestions, related questions,
         live search suggestions while typing, source links on every answer.
GUI    : gradient header, topic sidebar, rounded chat bubbles, typing animation,
         welcome cards, light/dark theme, chat export.

Run :  python college_faq_gui.py
Keys:  Enter = send | Up/Down = previous questions | Tab = accept suggestion
       Ctrl+T = theme | Ctrl+L = clear chat | Esc = close suggestions

Knowledge base snapshot: 26 November 2026 (official Manav Rachna pages).
Fees, dates and policies change - the bot always points to the official page.
"""

import difflib
import math
import re
import sys
import webbrowser
import tkinter as tk
from collections import Counter
from datetime import datetime
from tkinter import filedialog, messagebox
from tkinter import font as tkfont

# ======================================================================
# 1. KNOWLEDGE BASE
# ======================================================================
SITE = "https://manavrachna.edu.in"

CATEGORIES = [
    ("About", "🏛"), ("Programmes", "🎓"), ("Admissions", "📝"),
    ("Fees", "💰"), ("Scholarships", "🏅"), ("Hostel", "🏠"),
    ("Campus", "🏫"), ("Library", "📚"), ("Sports", "⚽"),
    ("Transport", "🚌"), ("Placements", "💼"), ("Student Life", "🎭"),
    ("Contact", "📞"),
]
CAT_ICON = dict(CATEGORIES)

CAT_SOURCE = {
    "About": SITE + "/mriirs/about/about-mriirs",
    "Programmes": SITE + "/mriirs",
    "Admissions": SITE + "/mriirs/admissions/admission-process",
    "Fees": SITE + "/mriirs/admissions/fee-structure",
    "Scholarships": SITE + "/mriirs/admissions/financial-aid-and-scholarships",
    "Hostel": SITE + "/mriirs/admissions/hostel-facility",
    "Campus": SITE + "/mriirs/life/campus-facilities",
    "Library": "https://ftp.manavrachna.edu.in/mriirs/life/library",
    "Sports": SITE + "/mriirs/life/sports",
    "Transport": SITE + "/mriirs/life/transport-facility",
    "Placements": SITE + "/mriirs/placements/overview",
    "Student Life": SITE + "/mriirs/life/dsw",
    "Contact": SITE + "/contact-us",
}
BROCHURE = SITE + "/assets/campus/mriirs/pdf/MRIIRS_brochure.pdf"


class Entry:
    __slots__ = ("category", "question", "answer", "keywords")

    def __init__(self, category, question, answer, keywords=""):
        self.category = category
        self.question = question
        self.answer = answer
        self.keywords = keywords


ENTRIES = []


def _add(cat, question, answer, keywords=""):
    ENTRIES.append(Entry(cat, question, answer, keywords))


# ---------------------------------------------------------------- About
_add("About", "What is the college name?",
     "The college is Manav Rachna International Institute of Research and "
     "Studies (MRIIRS), a Deemed-to-be University in Faridabad, Haryana.",
     "mriirs name deemed university manav rachna")
_add("About", "What is the full form of MRIIRS?",
     "MRIIRS stands for Manav Rachna International Institute of Research and Studies.",
     "abbreviation stands meaning mriirs")
_add("About", "Tell me about the history of MRIIRS",
     "MRIIRS began as the Career Institute of Technology & Management (CITM), "
     "established in 1997. It received Deemed-to-be-University status under "
     "Section 3 of the UGC Act (2008), and in 2018 its name changed from Manav "
     "Rachna International University to MRIIRS.",
     "history established founded origin citm started 1997 2018 name change")
_add("About", "Is MRIIRS NAAC accredited?",
     "According to the official MRIIRS About page, MRIIRS holds NAAC A++ "
     "(second cycle, February 2023, valid for five years from 20 February 2023) "
     "and UGC 12B status. NBA Tier-I accreditation is listed for B.Tech CSE, "
     "B.Tech Biotechnology and MBA.\n\nPlease verify the current regulatory "
     "status on the official website before relying on it for an important decision.",
     "naac accreditation grade a++ nba ugc 12b approved recognised")
_add("About", "What is the difference between MRIIRS, MRU and MREI?",
     "These are separate institutions - please don't mix their fees, admissions, "
     "placements or programmes:\n"
     "• MREI - Manav Rachna Educational Institutions (the wider education group)\n"
     "• MRIIRS - Manav Rachna International Institute of Research and Studies "
     "(Deemed-to-be University)\n"
     "• MRU - Manav Rachna University (a separate State Private University)\n"
     "• MRDC - Manav Rachna Dental College (constituent institution under MRIIRS)\n"
     "• MRIS - Manav Rachna International School network\n"
     "• MRCDOE - Manav Rachna Centre for Distance and Online Education\n\n"
     "I answer questions about MRIIRS, Faridabad.",
     "manav rachna university mru mrei mrdc mris mrcdoe difference same separate")
_add("About", "Where is the college located?",
     "MRIIRS is at Sector 43, Delhi-Surajkund Road, Faridabad 121004, Haryana, India.",
     "address location map faridabad sector 43 haryana pin")
_add("About", "What can you help me with?",
     "I can answer questions about MRIIRS: admissions, programmes, fees, "
     "scholarships, hostels, campus blocks and labs, library, sports, transport, "
     "placements and student life.\n\nTap a topic on the left, pick a question "
     "below, or just type your own - spelling mistakes are fine!",
     "help assistant features topics menu who are you")

# -------------------------------------------------------------- Contact
_add("Contact", "How can I contact the college?",
     "📞 General enquiry: +91-129-4198000 / +91-129-4198100\n"
     "📞 Admission helpdesk: +91-129-4259000\n"
     "✉ Admissions email: admissions@manavrachna.edu.in\n"
     "🌐 Website: manavrachna.edu.in",
     "phone number email helpline call reach website")
_add("Contact", "What is the admission helpline number?",
     "Admission helpdesk: +91-129-4259000\nEmail: admissions@manavrachna.edu.in\n"
     "General enquiry: +91-129-4198000 / +91-129-4198100",
     "admission helpdesk phone email number")
_add("Contact", "What is the official website?",
     "The official website is https://manavrachna.edu.in - the MRIIRS section is "
     "at https://manavrachna.edu.in/mriirs",
     "website link url portal online")
_add("Contact", "Can you tell me room numbers, timetable or staff contacts?",
     "I don't have room numbers, class timetables, live hostel vacancy, current "
     "bus stops or individual staff contacts, and I won't guess them. Please ask "
     "your department or call the helpdesk: +91-129-4198000.",
     "room number timetable staff faculty professor teacher vacancy seats availability bus stop")

# ----------------------------------------------------------- Programmes
SCHOOLS = [
    ("School of Engineering & Technology", "SET",
     "Computer Science and Engineering, Biotechnology, Civil Engineering, "
     "Electronics and Communication Engineering, Mechanical Engineering, Applied Sciences"),
    ("School of Computer Applications", "SCA", "Computer Applications"),
    ("School of Leadership & Management", "SLM", "Management Studies"),
    ("School of Allied Health Sciences", "SAHS",
     "Nutrition and Dietetics, Physiotherapy, Physiology, Biochemistry"),
    ("School of Behavioral and Social Sciences", "SBSS",
     "Applied Psychology, Economics, International Relations, Sociology/Social Work, "
     "Public Policy, Political Science"),
    ("School of Media Studies & Humanities", "SMSH",
     "Journalism and Mass Communication, English"),
    ("School of Design", "SoD", "Design"),
    ("School of Commerce & Economics", "SoCE", "Commerce, Economics"),
    ("School of Culinary and Hotel Management", "SCHM", "Hotel Management, Culinary Arts"),
    ("School of Dental Sciences", "SDS",
     "Conservative Dentistry and Endodontics, Oral and Maxillofacial Surgery, "
     "Pediatric and Preventive Dentistry, Prosthodontics and Crown and Bridge, "
     "Oral Medicine and Radiology, Biochemistry, Microbiology, Periodontology, "
     "Orthodontics and Dentofacial Orthopaedics, Public Health Dentistry"),
]

_add("Programmes", "Which courses are available?",
     "Programme examples (see the current brochure for the complete list, "
     "eligibility, duration and intake):\n"
     "• B.Tech - CSE; CSE (Hons.) AI & ML, Data Science, Digital Forensics & "
     "Cyber Security, Quantum Computing; Civil; ECE; Biotechnology\n"
     "• M.Tech, BCA, MCA, BBA, MBA, B.Com (Hons.)\n"
     "• BPT, MPT, Nutrition & Dietetics, Food Science & Technology\n"
     "• Journalism & Mass Communication, English, Applied Psychology, "
     "Political Science, Liberal Arts\n"
     "• B.Des specialisations, Culinary Arts, Hospitality & Hotel Administration\n"
     "• BDS, MDS and Ph.D. programmes",
     "course program programme degree stream list offered available btech mba bba bca")
_add("Programmes", "Which schools and departments does MRIIRS have?",
     "MRIIRS has 10 schools:\n" +
     "\n".join(f"{i}. {n} ({a})" for i, (n, a, _) in enumerate(SCHOOLS, 1)) +
     "\n\nAsk about any school, e.g. “What does the School of Design offer?”",
     "school department faculty branch list schools")
for _n, _a, _d in SCHOOLS:
    _add("Programmes", f"What does the {_n} ({_a}) offer?",
         f"{_n} ({_a}) - departments: {_d}.\n\nSee the current brochure for "
         f"programmes, eligibility and intake.", f"{_a} {_d}")
_add("Programmes", "Which B.Tech specialisations are available?",
     "B.Tech options mentioned by MRIIRS include:\n"
     "• Computer Science and Engineering (CSE)\n"
     "• CSE (Hons.) - Artificial Intelligence & Machine Learning\n"
     "• CSE (Hons.) - Data Science\n"
     "• CSE (Hons.) - Digital Forensics & Cyber Security\n"
     "• CSE (Hons.) - Quantum Computing\n"
     "• Civil Engineering\n"
     "• Electronics & Communication Engineering (ECE), including ECE (Hons.) "
     "AI & IoT and Semiconductor Design & Manufacturing\n"
     "• Biotechnology\n\nCheck the current brochure for the complete list and intake.",
     "btech engineering specialisation specialization branch cse aiml ai ml data "
     "science cyber security quantum ece civil biotechnology")
_add("Programmes", "Are BBA, MBA, BCA and MCA available?",
     "Yes. Management programmes (BBA, MBA) are offered through the School of "
     "Leadership & Management and computer applications (BCA, MCA) through the "
     "School of Computer Applications. B.Com (Hons.) is also listed.\n\n"
     "Check the current brochure for eligibility, duration and intake.",
     "bba mba bca mca management commerce bcom computer applications")
_add("Programmes", "Is dental course BDS or MDS available?",
     "Yes. The School of Dental Sciences offers BDS and MDS programmes, and "
     "Manav Rachna Dental College is a constituent institution under MRIIRS. "
     "Specialities include Conservative Dentistry & Endodontics, Oral & "
     "Maxillofacial Surgery, Pediatric & Preventive Dentistry, Prosthodontics, "
     "Oral Medicine & Radiology, Periodontology, Orthodontics and Public Health Dentistry.",
     "bds mds dental dentistry dentist mrdc")
_add("Programmes", "Are physiotherapy and nutrition courses available?",
     "Yes. The School of Allied Health Sciences covers Nutrition and Dietetics, "
     "Physiotherapy, Physiology and Biochemistry. Programmes listed include BPT, "
     "MPT, Nutrition & Dietetics and Food Science & Technology.",
     "bpt mpt physio physiotherapy nutrition dietetics allied health food science")
_add("Programmes", "Is PhD available?",
     "Yes, Ph.D. programmes are listed by MRIIRS. Please check the current "
     "brochure or the admission helpdesk (+91-129-4259000) for departments, "
     "eligibility and intake.",
     "phd doctorate research doctoral")
_add("Programmes", "What are the eligibility and duration of courses?",
     "Eligibility, duration and intake are different for every programme and "
     "can change each year. Please check the current brochure:\n" + BROCHURE +
     "\nor call the admission helpdesk: +91-129-4259000.",
     "eligibility criteria duration years intake seats brochure")

# ----------------------------------------------------------- Admissions
_add("Admissions", "What is the admission process?",
     "1. Apply online on the Manav Rachna admission portal.\n"
     "2. Prioritise up to three programme choices.\n"
     "3. Upload your Class 10 & Class 12 marksheets, address proof and "
     "programme-specific merit documents.\n"
     "4. Selection follows the current admission brochure - MRNAT is one route "
     "where applicable; JEE Main, SAT/UNIGAUGE or GATE may apply to relevant programmes.\n"
     "5. Selected applicants receive an offer letter by email.\n"
     "6. Accept the offer and pay the first instalment by the deadline.\n"
     "7. Complete physical document verification and enrolment.",
     "apply how steps procedure enroll join process")
_add("Admissions", "What documents are required for admission?",
     "Upload on the portal: Class 10 marksheet, address proof, Class 12 "
     "marksheet and programme-specific merit documents. You will also complete "
     "physical document verification at enrolment.",
     "document marksheet certificate proof upload required verification")
_add("Admissions", "What is the application fee?",
     "The admission page lists an application fee of ₹1,200. Please verify the "
     "amount for the current intake on the admission portal.",
     "application fee form registration")
_add("Admissions", "Which entrance exams are accepted?",
     "Selection follows the current admission brochure. MRNAT is one route where "
     "applicable, and JEE Main, SAT/UNIGAUGE or GATE may apply to relevant "
     "programmes. Scholarship schemes also mention CUET and NEET. Please confirm "
     "the exact route for your programme with the helpdesk (+91-129-4259000).",
     "entrance exam jee main sat unigauge gate mrnat cuet neet accepted test")
_add("Admissions", "What is MRNAT?",
     "MRNAT is one of the selection routes MRIIRS uses where applicable. "
     "Selection follows the current admission brochure, and JEE Main, "
     "SAT/UNIGAUGE or GATE may apply to relevant programmes. MRNAT also has an "
     "‘Utkarsh’ scholarship - ask me about scholarships.",
     "mrnat test entrance exam utkarsh")
_add("Admissions", "What are the admission dates and deadlines?",
     "Dates differ by programme and intake. For reference, the published Utkarsh "
     "admission window for MRNAT 2026 was 25 Jan - 15 May 2026. Please check the "
     "admission portal or call the helpdesk (+91-129-4259000) for the current deadlines.",
     "date deadline last start close intake schedule apply")
_add("Admissions", "What happens after I receive an offer letter?",
     "Accept the offer and pay the first instalment by the deadline, then "
     "complete physical document verification and enrolment.",
     "offer letter accept pay installment instalment enrolment enrollment")

# ----------------------------------------------------------------- Fees
FEES = [
    ("B.Tech Biotechnology", "₹2,20,000"),
    ("B.Tech Computer Science and Engineering (CSE)", "₹3,05,800"),
    ("B.Tech CSE (Hons.) Quantum Computing", "₹3,33,800"),
    ("B.Tech CSE (Hons.) Digital Forensics and Cyber Security", "₹3,33,800"),
    ("B.Tech CSE (Hons.) Data Science", "₹3,33,800"),
    ("B.Tech CSE (Hons.) Artificial Intelligence and Machine Learning", "₹3,50,000"),
    ("B.Tech ECE", "₹2,12,400"),
    ("B.Tech ECE (Hons.) AI and IoT", "₹2,33,500"),
    ("B.Tech ECE (Hons.) Semiconductor Design and Manufacturing", "₹2,33,500"),
    ("M.Tech ECE", "₹1,45,200"),
    ("B.Sc. (Hons.) Microbiology", "₹1,67,100"),
    ("B.Sc. Forensic Sciences", "₹1,40,000"),
]
FEE_NOTE = ("This is the annual total from the official fee page (AY 2027-28 "
            "snapshot). Components and instalments can vary - please confirm "
            "your exact programme and year on the official fee page or with "
            "the admission helpdesk (+91-129-4259000).")

_add("Fees", "What is the fee structure?",
     "Fees depend on the programme and academic year - tell me which programme "
     "you mean (e.g. “B.Tech CSE fee”).\n\nSelected annual totals "
     "(official fee page, AY 2027-28 snapshot):\n" +
     "\n".join(f"• {n}: {a}" for n, a in FEES) +
     "\n\nFee components can include tuition, development, university, "
     "student-resource, training-partner and international-pathway fees. This is "
     "only a selected list - please check the official fee page for your exact "
     "programme, year and instalments.",
     "fee fees tuition cost price charges annual total programme wise")
for _n, _a in FEES:
    _add("Fees", f"What is the fee of {_n}?",
         f"{_n}: annual total {_a}.\n\n{FEE_NOTE}", "annual total tuition")
_add("Fees", "What does the fee include?",
     "Fee components can include tuition, development, university, student "
     "resource, training partner and international pathway fees. The fee page "
     "shows an annual total as well as instalments, so always check which one "
     "you are looking at.",
     "fee component include breakdown instalment installment tuition development")

# ---------------------------------------------------------- Scholarships
_add("Scholarships", "Are scholarships available?",
     "Yes. Examples for 2026-27:\n"
     "• MRNAT 2026 Utkarsh - up to 100% tuition waiver\n"
     "• UG qualifying-exam marks - up to 100% (except BDS)\n"
     "• B.Tech JEE Main 2026 rank - up to 100%\n\n"
     "Other schemes may apply for SAT, CUET, NEET and categories. Check the "
     "current policy, deadlines, programme exclusions and seat availability.",
     "scholarship waiver discount concession financial aid merit")
_add("Scholarships", "What does the MRNAT Utkarsh scholarship offer?",
     "MRNAT 2026 Utkarsh (tuition waiver, as published):\n"
     "• 90% and above → 100%\n• 80% to below 90% → 50%\n• 70% to below 80% → 25%\n\n"
     "Published Utkarsh admission window: 25 Jan - 15 May 2026.",
     "mrnat utkarsh scholarship waiver tuition")
_add("Scholarships", "Is there a scholarship for Class 12 marks?",
     "UG qualifying-exam scholarship (except BDS):\n"
     "• 95% and above → 100%\n• 90% - 94.99% → 50%\n• 86% - 89.99% → 25%\n"
     "• 80% - 85.99% → 15%",
     "scholarship class 12 marks percentage qualifying exam board merit")
_add("Scholarships", "Is there a scholarship for JEE Main rank?",
     "B.Tech JEE Main 2026 overall AIR:\n• Up to 50,000 → 100%\n"
     "• 50,001 - 1,00,000 → 50%\n• 1,00,001 - 1,50,000 → 25%",
     "scholarship jee main rank air btech engineering")
_add("Scholarships", "How can I get a 100% scholarship?",
     "Published 100% tuition-waiver routes (2026-27):\n"
     "• MRNAT 2026 Utkarsh: 90% and above\n"
     "• UG qualifying exam (except BDS): 95% and above\n"
     "• B.Tech JEE Main 2026 overall AIR up to 50,000\n\n"
     "Please check the current policy, deadlines, programme exclusions and seat availability.",
     "scholarship 100 percent full free waiver highest")

# --------------------------------------------------------------- Hostel
HOSTELS = {
    "Boys Hostel 1": [
        (2, "Non-AC", "1,99,200", "2,04,200"), (2, "AC", "2,08,700", "2,28,700"),
        (4, "Non-AC", "1,67,000", "1,72,000"), (4, "AC", "1,84,800", "2,04,800"),
        (6, "AC", "1,79,200", "1,99,200")],
    "Boys Hostel 2": [
        (2, "AC", "2,30,300", "2,50,300"), (2, "Non-AC", "2,27,700", "2,32,700"),
        (3, "AC", "2,13,000", "2,33,000"), (3, "Non-AC", "2,10,800", "2,15,800")],
    "Girls Hostel": [
        (2, "AC", "2,52,500", "2,72,500"), (4, "AC", "1,84,800", "2,04,800"),
        (4, "Non-AC", "1,67,000", "1,72,000"), (6, "Non-AC", "1,64,600", "1,69,600")],
    "Studio Apartment": [(2, "AC", "2,98,100", "3,18,100")],
}
_add("Hostel", "Is hostel facility available?",
     "Yes. Separate boys' and girls' hostel accommodation is available on campus, "
     "with AC / non-AC rooms in multiple sharing categories, a mess, Wi-Fi, RO "
     "drinking water and laundry/support facilities. A studio apartment option "
     "is also listed.",
     "hostel accommodation dorm stay room boys girls mess wifi")
_add("Hostel", "What is the hostel fee?",
     "Published 2026-27 hostel fees range from about ₹1,64,600 to ₹2,98,100 a "
     "year, depending on the hostel, sharing and AC / non-AC.\n\n"
     "Ask for a specific one: Boys Hostel 1, Boys Hostel 2, Girls Hostel or "
     "Studio Apartment.\n\n20 electricity units/student/month are included; "
     "extra usage may be charged. Confirm current rates and vacancy on the "
     "official hostel page.",
     "hostel fee fees cost charges rent annual price")
for _h, _rows in HOSTELS.items():
    _lines = "\n".join(
        f"• {n}-sharing, {t} - ₹{a}/year (initial payment incl. advance ₹{i})"
        for n, t, a, i in _rows)
    _add("Hostel", f"What is the fee of {_h}?",
         f"{_h} - published 2026-27 fees:\n{_lines}\n\n20 electricity units/"
         f"student/month are included; extra usage may be charged. Confirm "
         f"current rates and vacancy.", "hostel fee annual sharing ac non")
_add("Hostel", "How does hostel allotment work?",
     "Registration / allotment is first-come-first-served. I can't see live "
     "vacancy, so please confirm availability with the hostel office or the "
     "helpdesk (+91-129-4198000).",
     "hostel allotment registration vacancy seats booking first come")
_add("Hostel", "Is electricity included in the hostel fee?",
     "The hostel page says 20 electricity units per student per month are "
     "included; extra usage may be charged.",
     "hostel electricity units power bill included")

# --------------------------------------------------------------- Campus
BLOCKS = {
    "A": ["Corporate Relations & Career Development Centre", "Mitsubishi Electric Lab",
          "Intel Intelligent Systems Lab", "Auditorium", "Peace Corridor",
          "Centre for Medicinal Plant Pathology", "Squash court (second floor)"],
    "B": ["True Spirit Shop", "Nescafe outlet (shared with Q Block)",
          "Volleyball court in front", "Basketball court in front"],
    "C": ["Honda Automotive Research Centre", "Butterfly Garden"],
    "E": ["Kinwar Design Lab", "Solar Photovoltaic (PV) Systems",
          "Basketball/tennis court in front of E & F"],
    "F": ["Radio Manav Rachna", "Centre for Media & Communications / Media Shala",
          "Bunk Yard Bistro", "Basketball/tennis court in front of E & F"],
    "G": ["Moot Court", "RL Lahoti Memorial Law Library", "Mandala Auditorium"],
    "J": ["Sports Science Centre", "Centre for Advanced Learning"],
    "K": ["Cricket ground in front of K and L Blocks"],
    "L": ["Cricket ground in front of K and L Blocks"],
    "Q": ["Centre for Dental Excellence", "Physiotherapy Centre", "Food Science Lab",
          "Centre for Sports Excellence", "Centre for Culinary Arts",
          "Centre of Advanced Water Technology", "Indoor sports arena (basement)",
          "Two 10-metre indoor shooting ranges", "Nescafe outlet (shared with B Block)"],
    "T": ["Dr. O.P. Bhalla Central Library", "WH Smith"],
}

_add("Campus", "What facilities are available?",
     "Campus facilities include:\n"
     "• 📚 Dr. O.P. Bhalla Central Library (T Block)\n"
     "• 🔬 Specialised labs and research centres\n"
     "• ⚽ Indoor & outdoor sports - arena, courts, cricket ground, shooting ranges, pool\n"
     "• 🏠 Boys' and girls' hostels\n"
     "• 🍽 Cafeterias and a food court\n"
     "• 🏥 Dispensary, ambulance and first-aid room\n"
     "• 🚌 Transport with nearby metro stations\n"
     "• 🎭 Student societies via the Department of Student Welfare",
     "facility facilities amenities campus infrastructure available")
_add("Campus", "What is in each campus block?",
     "Known public mappings (2025 campus guide - not a complete directory):\n"
     "• A - Career Development Centre, Mitsubishi & Intel labs, Auditorium\n"
     "• B - True Spirit Shop, Nescafe, volleyball & basketball courts\n"
     "• C - Honda Automotive Research Centre, Butterfly Garden\n"
     "• E - Kinwar Design Lab, Solar PV Systems\n"
     "• F - Radio Manav Rachna, Media Shala, Bunk Yard Bistro\n"
     "• G - Moot Court, RL Lahoti Law Library, Mandala Auditorium\n"
     "• J - Sports Science Centre, Centre for Advanced Learning\n"
     "• K & L - Cricket ground in front\n"
     "• Q - Dental, Physio, Food Science, Culinary, Sports Excellence, indoor arena\n"
     "• T - Dr. O.P. Bhalla Central Library, WH Smith\n\n"
     "Ask for details, e.g. “What is in Q Block?”",
     "block blocks directory map list buildings")
_add("Campus", "Which block is my department in?",
     "I only have selected facility-to-block mappings and I won't guess a "
     "department's block or room number. Ask me about a specific facility "
     "(e.g. “Where is the Moot Court?”) or check with your department / the "
     "helpdesk (+91-129-4198000).",
     "which block department room classroom where located my")
_add("Campus", "Which labs and research centres are there?",
     "Labs / centres listed by MRIIRS: Pre-clinical Conservative Lab, Food Science "
     "Lab, Electrotherapy Lab, Economics Department Computer Lab, Manovriti, "
     "Advanced Structural Analysis Laboratory, Mitsubishi Lab, Centre of AI/ML, "
     "Basic Training Kitchen, Business Lab and the Centre for Medicinal Plant Pathology.\n\n"
     "Also: Intel Intelligent Systems Lab (A Block), Honda Automotive Research "
     "Centre (C Block) and Kinwar Design Lab (E Block).",
     "lab labs laboratory research centre centres list")
_add("Campus", "Where is the computer lab?",
     "Computer-related labs I can place: Intel Intelligent Systems Lab and "
     "Mitsubishi Electric Lab (A Block), plus the Centre of AI/ML and the "
     "Economics Department Computer Lab. I don't have a complete room-by-room "
     "directory, so department computer labs can't be located exactly - please "
     "ask your department.",
     "computer lab labs it systems")
_add("Campus", "Is there a medical facility on campus?",
     "Healthcare on campus: dispensary, doctor and nursing staff, ambulance "
     "service, first-aid room, separate sick bays, dental and physiotherapy OPD, "
     "and a medical consultant during specified working hours.",
     "medical doctor dispensary hospital health ambulance clinic first aid")
_add("Campus", "Is there a canteen or cafeteria?",
     "Yes - campus cafeterias and a food court. The official page lists Subway, "
     "Café Woody's, 34 Chowringhee Lane, Juice Lounge, Dosa Plaza, Momo Box, "
     "Sugar Shacks, Indian Kitchen, Chai Garam, Needs and WH Smith. Bunk Yard "
     "Bistro is in F Block and a Nescafe outlet is shared by B and Q Blocks.\n\n"
     "Outlet availability can change.",
     "canteen cafeteria food eat restaurant cafe court outlet")
_add("Campus", "What are the college timings?",
     "I don't have a published class timetable - timings depend on your "
     "programme and department. Published hours I do have: the Central Library "
     "is open 8 AM-8 PM Mon-Sat and 9 AM-5 PM Sunday, and the Q Block indoor "
     "arena runs 8 AM-8 PM.",
     "timing timings hours schedule class timetable open")

FACILITIES = [
    ("Corporate Relations & Career Development Centre", "A Block",
     "placement cell career training recruiters"),
    ("Mitsubishi Electric Lab", "A Block", ""),
    ("Intel Intelligent Systems Lab", "A Block", "intel ai"),
    ("Auditorium", "A Block", "hall"),
    ("Peace Corridor", "A Block", ""),
    ("Centre for Medicinal Plant Pathology", "A Block", "plant"),
    ("True Spirit Shop", "B Block", "shop store"),
    ("Nescafe outlet", "B Block (shared with Q Block)", "coffee cafe"),
    ("Honda Automotive Research Centre", "C Block", "automotive honda car research"),
    ("Butterfly Garden", "C Block", "garden"),
    ("Kinwar Design Lab", "E Block", "design lab"),
    ("Solar Photovoltaic (PV) Systems", "E Block", "solar energy"),
    ("Radio Manav Rachna", "F Block", "radio station fm"),
    ("Centre for Media & Communications (Media Shala)", "F Block", "media studio"),
    ("Bunk Yard Bistro", "F Block", "cafe restaurant food"),
    ("Moot Court", "G Block", "law court"),
    ("RL Lahoti Memorial Law Library", "G Block", "law library"),
    ("Mandala Auditorium", "G Block", "auditorium hall"),
    ("Sports Science Centre", "J Block", "sport"),
    ("Centre for Advanced Learning", "J Block", ""),
    ("Centre for Dental Excellence", "Q Block", "dental clinic"),
    ("Physiotherapy Centre", "Q Block", "physio clinic"),
    ("Food Science Lab", "Q Block", ""),
    ("Centre for Sports Excellence", "Q Block", "sport"),
    ("Centre for Culinary Arts", "Q Block", "culinary kitchen chef"),
    ("Centre of Advanced Water Technology", "Q Block", "water"),
    ("WH Smith", "T Block", "bookstore books shop"),
]
for _f, _b, _k in FACILITIES:
    _add("Campus", f"Where is the {_f}?",
         f"The {_f} is in {_b} (2025 campus guide).\n\nTip: ask “What is in "
         f"{_b[0]} Block?” to see everything known for that block.", _k)

# -------------------------------------------------------------- Library
_add("Library", "Where is the library?",
     "The Dr. O.P. Bhalla Central Library is in T Block. The RL Lahoti Memorial "
     "Law Library is in G Block.",
     "library books reading central bhalla")
_add("Library", "What are the library timings?",
     "Dr. O.P. Bhalla Central Library (T Block), published hours:\n"
     "• Monday - Saturday: 8 AM - 8 PM\n• Sunday: 9 AM - 5 PM\n"
     "• Selected holidays: closed\n\nPlease confirm current policies.",
     "library timing hours open close schedule")
_add("Library", "How many books can I borrow from the library?",
     "According to the library FAQ, students may borrow up to five books for 28 "
     "days. Please confirm current policies with the library.",
     "library borrow books issue limit days return")
_add("Library", "Can outsiders use the library?",
     "External on-site membership is listed at ₹2,000, with no borrowing. "
     "Please confirm current policies with the library.",
     "library external outside membership guest visitor non student")
_add("Library", "What is the library contact number?",
     "Library reference desk: +91-129-4268901 / +91-129-4268902.",
     "library phone number contact reference desk")

# --------------------------------------------------------------- Sports
_add("Sports", "Is there a sports facility?",
     "Yes - extensive sports facilities:\n"
     "• Q Block basement indoor arena (about 7,000 sq ft)\n"
     "• Indoor shooting ranges (one 25 m and two 10 m)\n"
     "• Volleyball, basketball and tennis courts\n"
     "• Cricket ground with floodlights\n"
     "• Half-Olympic-size swimming pool, lawn tennis courts, table tennis "
     "academy and soccer facilities (verify current operating status)\n"
     "• Centre for Sports Excellence (Q Block) and Sports Science Centre (J Block)",
     "sport sports ground game games play facility")
_add("Sports", "What is in the indoor sports arena?",
     "Q Block basement arena (about 7,000 sq ft): one badminton court, six "
     "table-tennis tables, four chess stations, four carrom stations, two "
     "billiards tables and one pool table.\n\nPublished hours: 8 AM - 8 PM.",
     "indoor arena badminton table tennis chess carrom billiards pool snooker q")
_add("Sports", "Is there a shooting range?",
     "Yes - three indoor shooting ranges: one 25-metre and two 10-metre ranges. "
     "The two 10-metre ranges are in Q Block.",
     "shooting range rifle pistol 10 metre 25 metre")
_add("Sports", "Where are the basketball and volleyball courts?",
     "• Volleyball court: in front of B Block\n"
     "• Three basketball courts: in front of E/F Blocks, in front of B Block and "
     "in front of the International Boys Hostel\n"
     "• Basketball/tennis court: in front of E & F Blocks",
     "basketball volleyball tennis court courts")
_add("Sports", "Is there a cricket ground?",
     "Yes. The cricket ground is in front of K and L Blocks, described as "
     "40 × 40 metres with floodlights and two turf pitches.",
     "cricket ground pitch turf floodlights k l")
_add("Sports", "Is there a swimming pool?",
     "A half-Olympic-size swimming pool is listed on the sports page. Please "
     "verify the current operating status.",
     "swimming pool swim half olympic")
_add("Sports", "Is there a squash court?",
     "Yes - a squash court is on the second floor of A Block.",
     "squash court a block")
_add("Sports", "Is there a tennis court?",
     "Yes - lawn tennis courts with floodlights are listed, and there is a "
     "basketball/tennis court in front of E & F Blocks. Verify current operating status.",
     "tennis lawn court")

# ------------------------------------------------------------ Transport
_add("Transport", "Is there a college bus or transport facility?",
     "The official transport page lists route labels: Badli, Delhi Camp, Dwarka, "
     "Najafgarh, New Gurugram and Old Gurugram.\n\n⚠ Please confirm current "
     "student routes, stops and tariffs with the transport office. The tariffs "
     "displayed on the official page are school-transport tariffs, not verified "
     "MRIIRS student bus fees.",
     "bus transport shuttle route routes pickup")
_add("Transport", "Which metro station is near the college?",
     "Published nearby metro stations: Sarai, NHPC Chowk, Badkal Mor, "
     "Sector 28 and Mewala Maharajpur.",
     "metro station nearest reach train public")
_add("Transport", "What is the bus fee?",
     "I can't give a verified MRIIRS student bus fee. The tariffs shown on the "
     "official transport page for 2025-26 are school-transport tariffs, so I "
     "won't reuse them. Please confirm student routes, stops and tariffs with "
     "the transport office.",
     "bus transport fee cost charges tariff price")
_add("Transport", "Which bus routes are available?",
     "Published route labels: Badli, Delhi Camp, Dwarka, Najafgarh, New Gurugram "
     "and Old Gurugram. Please confirm current routes and stops with the "
     "transport office - I don't have live stop information.",
     "bus route routes stops pickup delhi gurugram dwarka najafgarh badli")

# ----------------------------------------------------------- Placements
_add("Placements", "Does the college provide placements?",
     "Yes. The MRIIRS placement page cites 880+ recruiters. The Corporate "
     "Relations & Career Development Centre is in A Block.\n\nRecruiters "
     "displayed include ADP, Accenture, Apollo, Axis Bank, BCG, Capgemini, "
     "Cognizant, Deloitte, IBM, Infosys, KPMG, PwC, Wipro, Honda, Nokia, "
     "Blinkit, HDFC, ICICI and Jio.\n\nFor batch-wise numbers, see the latest "
     "dated placement report.",
     "placement placements job jobs recruit recruitment campus drive career")
_add("Placements", "What is the highest package?",
     "Official Manav Rachna pages show different figures: 40 LPA on the MRIIRS "
     "About page, a 45 LPA student success-gallery entry and a separate 32 LPA "
     "highlight. The wider MREI group page shows 60 LPA. These may refer to "
     "different cohorts or scopes; please consult the latest dated placement "
     "report for the current batch.",
     "highest maximum top package ctc lpa salary")
_add("Placements", "Which companies visit for placements?",
     "Recruiter examples displayed: ADP, Accenture, Apollo, Axis Bank, BCG, "
     "Capgemini, Coforge, Cognizant, Deloitte, Ericsson, Genpact, HCL, IBM, "
     "Infosys, KPMG, Lenskart, Maruti Suzuki, Medanta, NTT DATA, PwC, Tech "
     "Mahindra, Wipro, Honda, Nokia, Blinkit, HDFC, ICICI, ITC and Jio.\n\n"
     "The placement page cites 880+ recruiters.",
     "companies recruiters visit hire list top")
_add("Placements", "What are the MBA placement statistics?",
     "MBA placement statistics page:\n• 2024-25: 47 students placed, highest "
     "package 10.02 LPA\n• 2023-24: 62 students placed, highest package 10 LPA",
     "mba placement statistics students placed management")
_add("Placements", "What is the average package?",
     "I don't have a verified average-package figure and won't guess one. "
     "Please check the latest dated placement report on the official placement page.",
     "average median package salary ctc lpa")
_add("Placements", "Who are the placement success stories?",
     "Examples shown in the placement overview gallery:\n"
     "• Sarthak Rastogi - B.Tech CSE, Microsoft, 45 LPA\n"
     "• Karan Aditya - B.Tech ECE, Amazon, 32 LPA\n"
     "• Ananya Sharma - B.Tech CSE, Google, 28 LPA\n"
     "• Rohan Mehra - B.Tech CSE, Deloitte, 25 LPA\n"
     "• Pranav Agarwal - B.Tech CSE, 32 LPA (placement highlight)",
     "success stories students toppers microsoft amazon google gallery")

# --------------------------------------------------------- Student life
_add("Student Life", "What is student welfare?",
     "The Department of Student Welfare supports student leadership, "
     "extracurricular activities, academic counselling and student development.",
     "student welfare dsw counselling support activities")
_add("Student Life", "Which clubs and societies are there?",
     "Named examples: AAREKH (Arts Society), PAIGAM (Theatre Society) and AAIRA "
     "(Fashion Society), run with the Department of Student Welfare.",
     "club clubs society societies aarekh paigam aaira extracurricular arts theatre fashion")
_add("Student Life", "What are the Manav Rachna group achievements?",
     "MREI group-level metrics (not MRIIRS-only): 46K+ global alumni, 7,700+ "
     "research papers, 880+ recruiters, 440+ filed/granted patents, 135+ global "
     "academic collaborations, 100+ alumni/in-campus startups, 60+ countries "
     "and a 60 LPA highest CTC.",
     "mrei group metrics alumni research papers patents collaborations startups")

POPULAR = [
    "Which courses are available?", "What is the fee structure?",
    "What is the admission process?", "Is hostel facility available?",
    "What is the highest package?", "Are scholarships available?",
]

# ======================================================================
# 2. TEXT PRE-PROCESSING
# ======================================================================
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "am", "be", "do", "does",
    "did", "i", "me", "my", "you", "your", "we", "us", "of", "in", "on", "at",
    "to", "for", "and", "or", "it", "this", "that", "there", "can", "could",
    "will", "would", "please", "tell", "about", "which", "what", "how", "any",
    "have", "has", "get", "give", "know", "want", "need", "with", "much",
    "many", "also", "just", "like", "here", "pls", "plz", "some", "show",
    "from", "by", "as", "its", "so", "if", "into", "than", "then", "kindly",
}

SYNONYMS = {
    "campus": "college", "university": "college", "institute": "college",
    "institution": "college", "course": "course", "program": "course",
    "programme": "course", "degree": "course", "stream": "course",
    "branch": "department", "dept": "department", "address": "location",
    "situated": "location", "located": "location", "place": "location",
    "where": "location", "phone": "contact", "call": "contact",
    "email": "contact", "number": "contact", "reach": "contact",
    "helpline": "contact", "apply": "admission", "enroll": "admission",
    "enrol": "admission", "register": "admission", "enrollment": "admission",
    "fees": "fee", "tuition": "fee", "cost": "fee", "price": "fee",
    "charges": "fee", "bus": "transport", "buses": "transport",
    "shuttle": "transport", "dorm": "hostel", "accommodation": "hostel",
    "canteen": "cafeteria", "mess": "cafeteria", "food": "cafeteria",
    "restaurant": "cafeteria", "cafe": "cafeteria", "eat": "cafeteria",
    "job": "placement", "jobs": "placement", "recruit": "placement",
    "recruitment": "placement", "salary": "placement", "package": "placement",
    "ctc": "placement", "lpa": "placement", "timing": "time",
    "timings": "time", "hours": "time", "schedule": "time", "open": "time",
    "labs": "lab", "laboratory": "lab", "books": "library", "sports": "sport",
    "ground": "sport", "game": "sport", "games": "sport", "stands": "full",
    "stand": "full", "abbreviation": "full", "meaning": "full",
    "discount": "scholarship", "waiver": "scholarship",
    "concession": "scholarship", "doctor": "medical", "dispensary": "medical",
    "health": "medical", "hospital": "medical", "ambulance": "medical",
    "clinic": "medical", "docs": "document", "certificate": "document",
    "marksheet": "document", "deadline": "date", "when": "date",
    "accredited": "naac", "accreditation": "naac", "grade": "naac",
    "approved": "naac", "recognised": "naac", "recognized": "naac",
    "ugc": "naac", "nba": "naac", "established": "history",
    "founded": "history", "origin": "history", "doctorate": "phd",
    "physio": "physiotherapy", "cs": "cse",
}

GREETINGS = {"hi", "hello", "hey", "hii", "hola", "namaste", "yo"}
THANKS = {"thanks", "thank", "thankyou", "thx"}
EXIT_WORDS = {"exit", "quit", "bye", "goodbye"}

CONFIDENT = 0.42   # show the answer directly
POSSIBLE = 0.20    # ask "Did you mean ...?"


def normalize(text):
    """Lowercase and unify things like B.Tech / b tech / btech -> btech."""
    t = text.lower()
    t = re.sub(r"\bph\.?\s?d\b", "phd", t)
    t = re.sub(r"(?<![a-z])([a-z])\.\s*([a-z]{2,4})(?![a-z])", r"\1\2", t)
    t = re.sub(r"\b([bm])\s+(tech|com|sc|des|ed)\b", r"\1\2", t)
    return t.replace("&", " and ")


def tokenize(text):
    return re.findall(r"[a-z0-9]+", normalize(text))


def stem(word):
    """Very light stemmer: courses -> course, facilities -> facility."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith(("ches", "shes", "xes", "sses")):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    if len(word) > 5 and word.endswith("ing"):
        return word[:-3]
    return word


def build_vocabulary(entries):
    vocab = set(SYNONYMS)
    for e in entries:
        vocab.update(tokenize(e.question + " " + e.keywords))
    return sorted(vocab)


def correct_spelling(word, vocab):
    if len(word) < 4 or word in vocab:
        return word
    match = difflib.get_close_matches(word, vocab, n=1, cutoff=0.8)
    return match[0] if match else word


def preprocess(text, vocab=None):
    out = []
    for word in tokenize(text):
        if vocab is not None:
            word = correct_spelling(word, vocab)
        word = SYNONYMS.get(word, word)
        if word in STOP_WORDS:
            continue
        word = stem(word)
        out.append(SYNONYMS.get(word, word))
    return out


# ======================================================================
# 3. TF-IDF + COSINE SIMILARITY (from scratch)
# ======================================================================
class TfidfModel:
    def __init__(self, documents):
        self.n_docs = len(documents)
        doc_freq = Counter()
        for doc in documents:
            doc_freq.update(set(doc))
        self.idf = {t: math.log((1 + self.n_docs) / (1 + df)) + 1
                    for t, df in doc_freq.items()}
        self.doc_vectors = [self.vectorize(d) for d in documents]

    def vectorize(self, tokens):
        counts = Counter(t for t in tokens if t in self.idf)
        vec = {t: c * self.idf[t] for t, c in counts.items()}
        norm = math.sqrt(sum(w * w for w in vec.values()))
        return {t: w / norm for t, w in vec.items()} if norm else {}

    @staticmethod
    def cosine(a, b):
        if len(a) > len(b):
            a, b = b, a
        return sum(w * b.get(t, 0.0) for t, w in a.items())

    def rank(self, tokens):
        q = self.vectorize(tokens)
        scores = [(self.cosine(q, d), i) for i, d in enumerate(self.doc_vectors)]
        return sorted(scores, reverse=True)


# ======================================================================
# 4. CHATBOT BRAIN
# ======================================================================
class Reply:
    """What the bot sends back to the GUI."""

    def __init__(self, text, kind="answer", score=None, category=None,
                 related=None, source=None):
        self.text = text
        self.kind = kind            # answer | suggest | multi | unknown | info
        self.score = score
        self.category = category
        self.related = related or []
        self.source = source


BLOCK_RE = re.compile(r"\b([a-z])[\s\-]*block\b|\bblock[\s\-]*([a-z])\b")


class CampusBot:
    def __init__(self, entries):
        self.entries = entries
        self.vocab = build_vocabulary(entries)
        docs = [preprocess(e.question + " " + e.keywords) for e in entries]
        self.model = TfidfModel(docs)
        self.index = {e.question: i for i, e in enumerate(entries)}

    # ---- helpers -----------------------------------------------------
    def by_category(self, cat):
        return [e.question for e in self.entries if e.category == cat]

    def _related(self, ranking, skip, cat, n=3):
        out = []
        for s, i in ranking[:12]:
            q = self.entries[i].question
            if i != skip and s >= 0.12 and q not in out:
                out.append(q)
            if len(out) == n:
                return out
        for q in self.by_category(cat):
            if q != self.entries[skip].question and q not in out:
                out.append(q)
            if len(out) == n:
                break
        return out

    def block_lookup(self, text):
        for m in BLOCK_RE.finditer(text.lower()):
            letter = (m.group(1) or m.group(2)).upper()
            if letter == "A" and not re.search(
                    r"\bA[\s\-]*[Bb]lock\b|\b[Bb]lock[\s\-]*A\b", text):
                continue                      # "a block" is just an article
            if letter in BLOCKS:
                items = "\n".join(f"• {x}" for x in BLOCKS[letter])
                name = "K and L Blocks" if letter in "KL" else f"{letter} Block"
                return Reply(
                    f"{name} - known facilities (2025 campus guide):\n{items}\n\n"
                    "This is a partial list, not a complete room-by-room directory.",
                    "answer", 1.0, "Campus",
                    ["What is in each campus block?", "Which block is my department in?"],
                    CAT_SOURCE["Campus"])
            return Reply(
                f"I don't have a published facility list for {letter} Block and "
                "I won't guess. Known blocks: A, B, C, E, F, G, J, K, L, Q and T.",
                "unknown", None, "Campus",
                ["What is in each campus block?", "Which block is my department in?"])
        return None

    # ---- main entry ----------------------------------------------------
    def reply(self, user_text):
        words = set(tokenize(user_text))
        low = user_text.strip().lower()

        if not words:
            return Reply("Please type a question.", "info")
        if low in EXIT_WORDS or low == "q":
            return Reply("Thank you for chatting! Come back any time. 👋", "info")
        if words & GREETINGS and len(words) <= 3:
            return Reply("Hello! 👋 I'm your MRIIRS campus assistant. Ask me about "
                         "admissions, fees, scholarships, hostels, campus blocks, "
                         "placements and more - or tap a topic on the left.",
                         "info", related=POPULAR[:4])
        if words & THANKS and len(words) <= 3:
            return Reply("You're welcome! 😊 Ask me anything else about MRIIRS.", "info")
        if low in ("help", "topics", "menu"):
            i = self.index["What can you help me with?"]
            return Reply(self.entries[i].answer, "info", related=POPULAR[:4])

        blk = self.block_lookup(user_text)
        if blk:
            return blk

        ranking = self.model.rank(preprocess(user_text, self.vocab))
        best, bi = ranking[0]
        entry = self.entries[bi]

        if best >= CONFIDENT:
            close = [(s, i) for s, i in ranking[:4]
                     if s >= best * 0.93 and s >= CONFIDENT]
            if len(close) > 1 and len({self.entries[i].answer for _, i in close}) > 1:
                return Reply("That could match a few topics - tap the one you mean:",
                             "multi", best, None,
                             [self.entries[i].question for _, i in close])
            return Reply(entry.answer, "answer", best, entry.category,
                         self._related(ranking, bi, entry.category),
                         CAT_SOURCE.get(entry.category))

        if best >= POSSIBLE:
            return Reply(f"I'm not fully sure - did you mean “{entry.question}”?\n\n"
                         f"{entry.answer}", "suggest", best, entry.category,
                         self._related(ranking, bi, entry.category),
                         CAT_SOURCE.get(entry.category))

        return Reply("Sorry, I don't have that information yet.\n\nFor anything "
                     "not covered, please call the helpdesk: +91-129-4198000 "
                     "(admissions: +91-129-4259000) or email "
                     "admissions@manavrachna.edu.in.\n\nHere are some things I can help with:",
                     "unknown", best, None, POPULAR[:4])

    def suggest(self, text, n=4):
        """Live suggestions while the user is typing."""
        low = text.strip().lower()
        if len(low) < 3:
            return []
        out = [e.question for e in self.entries if low in e.question.lower()]
        for s, i in self.model.rank(preprocess(text, self.vocab))[:8]:
            if s < 0.22:
                break
            q = self.entries[i].question
            if q not in out:
                out.append(q)
        return out[:n]


# ======================================================================
# 5. GUI
# ======================================================================
THEMES = {
    "light": dict(
        bg="#F3F5FB", side="#FFFFFF", side_hover="#EEF2FF", side_active="#E0E7FF",
        text="#0F172A", muted="#64748B", border="#E2E8F0",
        accent="#4F46E5", accent_hover="#4338CA", hdr_a="#4338CA", hdr_b="#9333EA",
        hdr_fg="#FFFFFF", user_bg="#4F46E5", user_fg="#FFFFFF",
        bot_bg="#FFFFFF", bot_fg="#0F172A", suggest_bg="#FFF6DD",
        unknown_bg="#FDEBEB", info_bg="#EAEFFF", chip_bg="#FFFFFF",
        chip_fg="#4338CA", chip_border="#C7D2FE", chip_hover="#EEF2FF",
        input_bg="#FFFFFF", good="#059669", warn="#D97706", bad="#DC2626",
        card_bg="#FFFFFF"),
    "dark": dict(
        bg="#0B1020", side="#111827", side_hover="#1F2937", side_active="#312E81",
        text="#E5E7EB", muted="#94A3B8", border="#273449",
        accent="#6366F1", accent_hover="#818CF8", hdr_a="#1E1B4B", hdr_b="#581C87",
        hdr_fg="#FFFFFF", user_bg="#6366F1", user_fg="#FFFFFF",
        bot_bg="#172033", bot_fg="#E5E7EB", suggest_bg="#3B2A0A",
        unknown_bg="#3F1518", info_bg="#1E1B4B", chip_bg="#111827",
        chip_fg="#C7D2FE", chip_border="#3730A3", chip_hover="#1E1B4B",
        input_bg="#172033", good="#34D399", warn="#FBBF24", bad="#F87171",
        card_bg="#111827"),
}

QUICK_CHIPS = [
    ("💰 Fees", "What is the fee structure?"),
    ("🏠 Hostel fee", "What is the hostel fee?"),
    ("💼 Highest package", "What is the highest package?"),
    ("📍 Location", "Where is the college located?"),
    ("📞 Contact", "How can I contact the college?"),
]

HERO_CARDS = [
    ("🎓", "Courses", "Programmes & schools", "Which courses are available?"),
    ("📝", "Admissions", "Steps & documents", "What is the admission process?"),
    ("💰", "Fees", "Programme-wise fees", "What is the fee structure?"),
    ("🏅", "Scholarships", "Up to 100% waiver", "Are scholarships available?"),
    ("🏠", "Hostel", "Rooms, fees & rules", "Is hostel facility available?"),
    ("💼", "Placements", "Recruiters & packages", "Does the college provide placements?"),
]

FONT = "TkDefaultFont"
UI_SCALE = 1.0
PLACEHOLDER = "Ask about fees, hostel, placements, blocks…"
CHIPS_PER_PAGE = 8


def px(n):
    return int(n * UI_SCALE)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def round_rect(cv, x1, y1, x2, y2, r, **kw):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(pts, smooth=True, **kw)


def pick_font(root):
    avail = set(tkfont.families(root))
    for f in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter", "Roboto",
              "Ubuntu", "Noto Sans", "DejaVu Sans", "Arial"):
        if f in avail:
            return f
    return "TkDefaultFont"


class Header(tk.Canvas):
    """Gradient title bar with pill buttons."""

    def __init__(self, app):
        super().__init__(app, height=px(80), highlightthickness=0, bd=0)
        self.app = app
        self.count = 0
        self.bind("<Configure>", lambda e: self.redraw())

    def set_count(self, n):
        self.count = n
        self.redraw()

    def redraw(self):
        t = self.app.t
        w, h = self.winfo_width(), self.winfo_height()
        if w < 50:
            return
        self.delete("all")
        steps = 160
        for i in range(steps):
            c = mix(t["hdr_a"], t["hdr_b"], i / (steps - 1))
            self.create_rectangle(int(i * w / steps), 0, int((i + 1) * w / steps) + 1,
                                  h, fill=c, outline=c)
        # soft decorative circles
        self.create_oval(w - px(210), -px(70), w - px(40), px(80),
                         fill=mix(t["hdr_b"], "#FFFFFF", 0.10), outline="")
        self.create_oval(w - px(330), px(30), w - px(250), px(110),
                         fill=mix(t["hdr_a"], "#FFFFFF", 0.08), outline="")
        # avatar
        cx, cy, r = px(48), h // 2, px(25)
        self.create_oval(cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3,
                         fill=mix(t["hdr_a"], "#FFFFFF", 0.35), outline="")
        self.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#FFFFFF", outline="")
        self.create_text(cx, cy, text="🎓", font=(FONT, 20))
        # titles
        self.create_text(px(92), h // 2 - px(11), text="MRIIRS Campus Assistant",
                         anchor="w", fill=t["hdr_fg"], font=(FONT, 16, "bold"))
        self.create_oval(px(92), h // 2 + px(9), px(100), h // 2 + px(17),
                         fill="#34D399", outline="")
        n = self.count
        self.create_text(px(108), h // 2 + px(13), anchor="w",
                         text=f"Online  •  {n} question{'s' if n != 1 else ''} answered",
                         fill=mix(t["hdr_fg"], t["hdr_b"], 0.2), font=(FONT, 10))
        # pill buttons (right to left)
        theme_label = "☀  Light" if self.app.theme_name == "dark" else "🌙  Dark"
        buttons = [("clear", "🗑  Clear", self.app.clear_chat),
                   ("save", "💾  Save", self.app.save_chat),
                   ("theme", theme_label, self.app.toggle_theme)]
        bw, bh, x = px(100), px(36), w - px(22)
        for key, label, cmd in buttons:
            x1, y1 = x - bw, (h - bh) // 2
            base = mix(t["hdr_a"], t["hdr_b"], (x1 + bw / 2) / w)
            fill, hover = mix(base, "#FFFFFF", 0.20), mix(base, "#FFFFFF", 0.34)
            tag = "btn_" + key
            round_rect(self, x1, y1, x1 + bw, y1 + bh, bh // 2, fill=fill,
                       outline="", tags=(tag, tag + "_bg"))
            self.create_text(x1 + bw / 2, y1 + bh / 2, text=label, fill="#FFFFFF",
                             font=(FONT, 10, "bold"), tags=(tag,))
            self.tag_bind(tag, "<Enter>", lambda e, tg=tag, hv=hover: (
                self.itemconfigure(tg + "_bg", fill=hv), self.config(cursor="hand2")))
            self.tag_bind(tag, "<Leave>", lambda e, tg=tag, fl=fill: (
                self.itemconfigure(tg + "_bg", fill=fl), self.config(cursor="")))
            self.tag_bind(tag, "<Button-1>", lambda e, c=cmd: c())
            x = x1 - px(10)


class Bubble(tk.Canvas):
    """Rounded chat bubble sized to its text (text can be revealed gradually)."""

    def __init__(self, parent, text, fill, fg, outer, wrap, border=None):
        super().__init__(parent, bg=outer, highlightthickness=0, bd=0)
        padx, pady = px(15), px(11)
        self.lbl = tk.Label(self, text=text, bg=fill, fg=fg, font=(FONT, 11),
                            justify="left", anchor="nw", wraplength=wrap)
        w, h = self.lbl.winfo_reqwidth(), self.lbl.winfo_reqheight()
        bw, bh = w + 2 * padx, h + 2 * pady
        self.configure(width=bw, height=bh)
        round_rect(self, 1, 1, bw - 1, bh - 1, px(18), fill=fill,
                   outline=border or fill)
        self.create_window(padx, pady, window=self.lbl, anchor="nw", width=w, height=h)

    def set_text(self, text):
        self.lbl.configure(text=text)


class Chip(tk.Label):
    """Clickable suggestion pill."""

    def __init__(self, parent, text, command, t, wrap=0, anchor="w"):
        super().__init__(parent, text=text, bg=t["chip_bg"], fg=t["chip_fg"],
                         font=(FONT, 10), padx=px(13), pady=px(6), cursor="hand2",
                         highlightthickness=1, highlightbackground=t["chip_border"],
                         anchor=anchor, justify="left", wraplength=wrap)
        self.bind("<Enter>", lambda e: self.configure(bg=t["chip_hover"]))
        self.bind("<Leave>", lambda e: self.configure(bg=t["chip_bg"]))
        self.bind("<Button-1>", lambda e: command())


class InputBar(tk.Canvas):
    """Rounded input pill with an embedded send button."""

    def __init__(self, parent, app):
        super().__init__(parent, height=px(60), highlightthickness=0, bd=0)
        self.app = app
        t = app.t
        self.focused = False
        self.placeholder_on = False
        self.entry = tk.Entry(self, font=(FONT, 12), relief="flat", bd=0,
                              bg=t["input_bg"], fg=t["text"],
                              insertbackground=t["text"])
        self.entry.bind("<FocusIn>", self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)
        self.bind("<Configure>", lambda e: self.redraw())
        self.bind("<Button-1>", lambda e: self.entry.focus_set())
        self._show_placeholder()

    # placeholder helpers ------------------------------------------------
    def _show_placeholder(self):
        if not self.entry.get():
            self.placeholder_on = True
            self.entry.insert(0, PLACEHOLDER)
            self.entry.configure(fg=self.app.t["muted"])

    def _focus_in(self, _):
        if self.placeholder_on:
            self.entry.delete(0, "end")
            self.placeholder_on = False
            self.entry.configure(fg=self.app.t["text"])
        self.focused = True
        self.redraw()

    def _focus_out(self, _):
        self.focused = False
        self._show_placeholder()
        self.redraw()

    def get(self):
        return "" if self.placeholder_on else self.entry.get()

    def set(self, text):
        if self.placeholder_on:
            self.placeholder_on = False
            self.entry.configure(fg=self.app.t["text"])
        self.entry.delete(0, "end")
        self.entry.insert(0, text)
        self.entry.icursor("end")

    def clear(self):
        self.entry.delete(0, "end")
        self.placeholder_on = False
        self.entry.configure(fg=self.app.t["text"])
        if not self.focused:
            self._show_placeholder()

    # drawing ------------------------------------------------------------
    def redraw(self):
        t = self.app.t
        w, h = self.winfo_width(), self.winfo_height()
        if w < 80:
            return
        self.configure(bg=t["bg"])
        self.delete("all")
        border = t["accent"] if self.focused else t["border"]
        round_rect(self, 2, 2, w - 2, h - 2, h // 2 - 2, fill=t["input_bg"],
                   outline=border, width=2 if self.focused else 1)
        r = px(21)
        cx, cy = w - px(10) - r - 4, h // 2
        self.create_window(px(26), h // 2, window=self.entry, anchor="w",
                           width=max(60, w - px(26) - 2 * r - px(40)), height=px(30))
        self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=t["accent"],
                         outline="", tags=("send", "send_bg"))
        self.create_text(cx, cy, text="➤", fill="#FFFFFF", font=(FONT, 13, "bold"),
                         tags=("send",))
        self.tag_bind("send", "<Enter>", lambda e: (
            self.itemconfigure("send_bg", fill=t["accent_hover"]),
            self.config(cursor="hand2")))
        self.tag_bind("send", "<Leave>", lambda e: (
            self.itemconfigure("send_bg", fill=t["accent"]), self.config(cursor="")))
        self.tag_bind("send", "<Button-1>", lambda e: self.app.submit())


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        global FONT, UI_SCALE
        try:                                   # crisp text on Windows
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        FONT = pick_font(self)
        try:
            UI_SCALE = max(1.0, self.winfo_fpixels("1i") / 96.0)
        except tk.TclError:
            UI_SCALE = 1.0

        self.title("MRIIRS Campus Assistant")
        self.geometry(f"{px(1120)}x{px(780)}")
        self.minsize(px(880), px(620))

        self.bot = CampusBot(ENTRIES)
        self.theme_name = "light"
        self.t = THEMES["light"]
        self.history = []          # chat items (dicts) - source of truth
        self.sent = []             # typed questions for Up/Down recall
        self.hpos = 0
        self.busy = False
        self.asked = 0
        self.active_cat = None
        self.typing_job = None
        self.typing_row = None
        self.wrap = 440
        self._resize_job = None

        self.build_ui()
        self.bind_all("<MouseWheel>", self.on_wheel)
        self.bind_all("<Button-4>", lambda e: self._scroll(-1))
        self.bind_all("<Button-5>", lambda e: self._scroll(1))
        self.bind("<Control-t>", lambda e: self.toggle_theme())
        self.bind("<Control-l>", lambda e: self.clear_chat())
        self.bind("<Escape>", lambda e: self.hide_suggestions())

    # ------------------------------------------------------------------
    # layout
    # ------------------------------------------------------------------
    def build_ui(self):
        for w in self.winfo_children():
            w.destroy()
        t = self.t
        self.configure(bg=t["bg"])
        self.header = Header(self)
        self.header.pack(fill="x")
        self.header.count = self.asked
        body = tk.Frame(self, bg=t["bg"])
        body.pack(fill="both", expand=True)
        self.build_sidebar(body)
        tk.Frame(body, width=1, bg=t["border"]).pack(side="left", fill="y")
        self.build_chat(body)

    def build_sidebar(self, parent):
        t = self.t
        side = tk.Frame(parent, width=px(250), bg=t["side"])
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="BROWSE TOPICS", bg=t["side"], fg=t["muted"],
                 font=(FONT, 9, "bold"), anchor="w").pack(
            fill="x", padx=px(20), pady=(px(16), px(6)))

        self.cat_rows = {}
        for name, icon in CATEGORIES:
            row = tk.Frame(side, bg=t["side"], cursor="hand2")
            row.pack(fill="x", padx=px(10), pady=1)
            bar = tk.Frame(row, width=4, bg=t["side"])
            bar.pack(side="left", fill="y")
            lbl = tk.Label(row, text=f"  {icon}   {name}", bg=t["side"], fg=t["text"],
                           font=(FONT, 11), anchor="w", pady=px(5), cursor="hand2")
            lbl.pack(side="left", fill="x", expand=True)
            self.cat_rows[name] = (row, bar, lbl)
            for w in (row, bar, lbl):
                w.bind("<Button-1>", lambda e, n=name: self.show_category(n))
                w.bind("<Enter>", lambda e, n=name: self._cat_paint(n, hover=True))
                w.bind("<Leave>", lambda e, n=name: self._cat_paint(n, hover=False))
        for n in self.cat_rows:
            self._cat_paint(n)

        # footer card
        foot = tk.Frame(side, bg=t["side"])
        foot.pack(side="bottom", fill="x", padx=px(14), pady=px(14))
        card = tk.Frame(foot, bg=t["info_bg"], highlightthickness=1,
                        highlightbackground=t["border"])
        card.pack(fill="x")
        tk.Label(card, text="Need a human?", bg=t["info_bg"], fg=t["text"],
                 font=(FONT, 10, "bold"), anchor="w").pack(fill="x", padx=px(12), pady=(px(9), 0))
        tk.Label(card, text="📞 +91-129-4259000\n✉ admissions@manavrachna.edu.in",
                 bg=t["info_bg"], fg=t["muted"], font=(FONT, 9), justify="left",
                 anchor="w").pack(fill="x", padx=px(12), pady=(px(2), px(6)))
        site = tk.Label(card, text="🌐  Open official website", bg=t["accent"],
                        fg="#FFFFFF", font=(FONT, 10, "bold"), pady=px(7),
                        cursor="hand2")
        site.pack(fill="x", padx=px(10), pady=(0, px(10)))
        site.bind("<Enter>", lambda e: site.configure(bg=t["accent_hover"]))
        site.bind("<Leave>", lambda e: site.configure(bg=t["accent"]))
        site.bind("<Button-1>", lambda e: webbrowser.open(SITE + "/mriirs"))

    def _cat_paint(self, name, hover=False):
        t = self.t
        row, bar, lbl = self.cat_rows[name]
        active = name == self.active_cat
        bg = t["side_active"] if active else (t["side_hover"] if hover else t["side"])
        for w in (row, lbl):
            w.configure(bg=bg)
        bar.configure(bg=t["accent"] if active else bg)
        lbl.configure(fg=t["accent"] if active else t["text"])

    def build_chat(self, parent):
        t = self.t
        col = tk.Frame(parent, bg=t["bg"])
        col.pack(side="left", fill="both", expand=True)
        col.grid_rowconfigure(0, weight=1)
        col.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(col, bg=t["bg"], highlightthickness=0, bd=0,
                                yscrollincrement=px(30))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll = tk.Scrollbar(col, orient="vertical", command=self.canvas.yview,
                                   width=px(10), bd=0, relief="flat",
                                   troughcolor=t["bg"], bg=t["border"],
                                   activebackground=t["muted"])
        self.scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.msgs = tk.Frame(self.canvas, bg=t["bg"])
        self.win = self.canvas.create_window((0, 0), window=self.msgs, anchor="nw")
        self.msgs.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # live suggestions (hidden until typing)
        self.sugg = tk.Frame(col, bg=t["bg"])
        self.sugg.grid(row=1, column=0, columnspan=2, sticky="ew",
                       padx=px(22), pady=(0, px(2)))
        self.sugg.grid_remove()

        # quick chips
        chips = tk.Frame(col, bg=t["bg"])
        chips.grid(row=2, column=0, columnspan=2, sticky="ew", padx=px(22), pady=(px(4), 0))
        for label, q in QUICK_CHIPS:
            Chip(chips, label, lambda q=q: self.ask(q), t, anchor="center").pack(
                side="left", padx=(0, px(8)))

        self.inputbar = InputBar(col, self)
        self.inputbar.grid(row=3, column=0, columnspan=2, sticky="ew",
                           padx=px(18), pady=(px(8), px(14)))
        self.inputbar.entry.bind("<Return>", lambda e: self.submit())
        self.inputbar.entry.bind("<Up>", self.history_up)
        self.inputbar.entry.bind("<Down>", self.history_down)
        self.inputbar.entry.bind("<Tab>", self.accept_suggestion)
        self.inputbar.entry.bind("<KeyRelease>", self.on_key)
        self.sugg_items = []

        self.redraw_history()

    # ------------------------------------------------------------------
    # scrolling
    # ------------------------------------------------------------------
    def on_canvas_configure(self, e):
        self.canvas.itemconfigure(self.win, width=e.width)
        new_wrap = max(260, min(580, int(e.width * 0.62)))
        if abs(new_wrap - self.wrap) > 40:
            self.wrap = new_wrap
            if self._resize_job:
                self.after_cancel(self._resize_job)
            self._resize_job = self.after(250, self.redraw_history)

    def _scroll(self, n):
        try:
            self.canvas.yview_scroll(n, "units")
        except (tk.TclError, AttributeError):
            pass

    def on_wheel(self, e):
        if sys.platform == "darwin":
            self._scroll(-e.delta)
        else:
            self._scroll(-1 if e.delta > 0 else 1)

    def scroll_bottom(self):
        try:
            self.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.yview_moveto(1.0)
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # rendering
    # ------------------------------------------------------------------
    def redraw_history(self):
        for w in self.msgs.winfo_children():
            w.destroy()
        self.draw_hero()
        for it in self.history:
            self.render_item(it, animate=False)
        self.scroll_bottom()

    def draw_hero(self):
        t = self.t
        hero = tk.Frame(self.msgs, bg=t["bg"])
        hero.pack(fill="x", pady=(px(26), px(6)))
        tk.Label(hero, text="Hi, I'm your campus assistant 👋", bg=t["bg"], fg=t["text"],
                 font=(FONT, 22, "bold")).pack()
        tk.Label(hero, text="Ask me anything about MRIIRS - or start with one of these.",
                 bg=t["bg"], fg=t["muted"], font=(FONT, 11)).pack(pady=(px(4), px(16)))
        grid = tk.Frame(hero, bg=t["bg"])
        grid.pack()
        for i, (icon, title, sub, q) in enumerate(HERO_CARDS):
            card = tk.Frame(grid, bg=t["card_bg"], highlightthickness=1,
                            highlightbackground=t["border"], cursor="hand2")
            card.grid(row=i // 3, column=i % 3, padx=px(7), pady=px(7))
            parts = [
                tk.Label(card, text=icon, bg=t["card_bg"], font=(FONT, 22)),
                tk.Label(card, text=title, bg=t["card_bg"], fg=t["text"],
                         font=(FONT, 11, "bold")),
                tk.Label(card, text=sub, bg=t["card_bg"], fg=t["muted"], font=(FONT, 9)),
            ]
            parts[0].pack(padx=px(22), pady=(px(14), 0))
            parts[1].pack()
            parts[2].pack(padx=px(22), pady=(0, px(14)))

            def enter(e, c=card, ps=parts):
                c.configure(bg=t["side_active"], highlightbackground=t["accent"])
                for p in ps:
                    p.configure(bg=t["side_active"])

            def leave(e, c=card, ps=parts):
                c.configure(bg=t["card_bg"], highlightbackground=t["border"])
                for p in ps:
                    p.configure(bg=t["card_bg"])
            for w in [card] + parts:
                w.bind("<Enter>", enter)
                w.bind("<Leave>", leave)
                w.bind("<Button-1>", lambda e, q=q: self.ask(q))
                w.configure(cursor="hand2")

    def make_avatar(self, parent):
        t = self.t
        s = px(38)
        cv = tk.Canvas(parent, width=s, height=s, bg=t["bg"], highlightthickness=0)
        cv.create_oval(1, 1, s - 1, s - 1, fill=t["accent"], outline="")
        cv.create_text(s // 2, s // 2, text="🤖", font=(FONT, 15))
        return cv

    def bubble_colors(self, it):
        t = self.t
        if it["who"] == "user":
            return t["user_bg"], t["user_fg"], None
        fill = {"answer": t["bot_bg"], "suggest": t["suggest_bg"],
                "multi": t["info_bg"], "unknown": t["unknown_bg"],
                "info": t["info_bg"], "menu": t["info_bg"]}.get(it["kind"], t["bot_bg"])
        return fill, t["bot_fg"], t["border"]

    def render_item(self, it, animate=False):
        t = self.t
        row = tk.Frame(self.msgs, bg=t["bg"])
        row.pack(fill="x", padx=px(20), pady=px(6))
        fill, fg, border = self.bubble_colors(it)

        if it["who"] == "user":
            col = tk.Frame(row, bg=t["bg"])
            col.pack(side="right")
            Bubble(col, it["text"], fill, fg, t["bg"], self.wrap).pack(anchor="e")
            tk.Label(col, text=it["stamp"], bg=t["bg"], fg=t["muted"],
                     font=(FONT, 8)).pack(anchor="e", pady=(px(2), 0))
            return

        holder = tk.Frame(row, bg=t["bg"])
        holder.pack(side="left", anchor="n")
        self.make_avatar(holder).pack(side="left", anchor="n", padx=(0, px(10)))
        col = tk.Frame(holder, bg=t["bg"])
        col.pack(side="left")
        cat = it.get("category")
        if cat:
            tk.Label(col, text=f"{CAT_ICON.get(cat, '')}  {cat.upper()}", bg=t["bg"],
                     fg=t["accent"], font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, px(3)))
        bub = Bubble(col, it["text"], fill, fg, t["bg"], self.wrap, border)
        bub.pack(anchor="w")
        if animate:
            bub.set_text("")
            self.typewriter(bub, it["text"], 0, lambda: self.finish_bot(col, it, True))
        else:
            self.finish_bot(col, it, False)

    def typewriter(self, bub, full, i, done):
        if not bub.winfo_exists():
            return
        step = max(3, len(full) // 45)
        i = min(len(full), i + step)
        bub.set_text(full[:i])
        self.scroll_bottom()
        if i < len(full):
            self.after(14, lambda: self.typewriter(bub, full, i, done))
        else:
            done()

    def finish_bot(self, col, it, scroll):
        t = self.t
        if not col.winfo_exists():
            return
        meta = tk.Frame(col, bg=t["bg"])
        meta.pack(anchor="w", pady=(px(3), 0))
        tk.Label(meta, text=it["stamp"], bg=t["bg"], fg=t["muted"],
                 font=(FONT, 8)).pack(side="left")
        sc = it.get("score")
        if sc is not None and it["kind"] in ("answer", "suggest"):
            pct = int(min(sc, 1.0) * 100)
            colr = t["good"] if sc >= 0.7 else (t["warn"] if sc >= CONFIDENT else t["bad"])
            tk.Label(meta, text=f"  •  ● {pct}% match", bg=t["bg"], fg=colr,
                     font=(FONT, 8, "bold")).pack(side="left")
        if it.get("source"):
            link = tk.Label(meta, text="   ↗ Official source", bg=t["bg"], fg=t["accent"],
                            font=(FONT, 8, "underline"), cursor="hand2")
            link.pack(side="left")
            link.bind("<Button-1>", lambda e, u=it["source"]: webbrowser.open(u))

        chips = it.get("chips") or it.get("related") or []
        if chips:
            lab = "Related questions" if it["kind"] in ("answer", "suggest") else None
            if lab:
                tk.Label(col, text=lab, bg=t["bg"], fg=t["muted"],
                         font=(FONT, 8, "bold")).pack(anchor="w", pady=(px(8), px(2)))
            else:
                tk.Frame(col, height=px(6), bg=t["bg"]).pack()
            for q in chips:
                Chip(col, q, lambda q=q: self.ask(q), t, wrap=self.wrap).pack(
                    anchor="w", pady=px(2))
        if it.get("more"):
            cat, start = it["more"]
            Chip(col, "More questions  ▸", lambda: self.show_category(cat, start),
                 t, anchor="center").pack(anchor="w", pady=px(2))
        if scroll:
            self.scroll_bottom()
        self.busy = False

    # ------------------------------------------------------------------
    # typing indicator
    # ------------------------------------------------------------------
    def show_typing(self):
        t = self.t
        self.typing_row = tk.Frame(self.msgs, bg=t["bg"])
        self.typing_row.pack(fill="x", padx=px(20), pady=px(6))
        self.make_avatar(self.typing_row).pack(side="left", padx=(0, px(10)))
        w, h = px(72), px(38)
        cv = tk.Canvas(self.typing_row, width=w, height=h, bg=t["bg"], highlightthickness=0)
        cv.pack(side="left")
        round_rect(cv, 1, 1, w - 1, h - 1, px(18), fill=t["bot_bg"], outline=t["border"])
        self.dots = [cv.create_oval(px(18) + i * px(14), h // 2 - 4,
                                    px(18) + i * px(14) + 8, h // 2 + 4,
                                    fill=t["muted"], outline="") for i in range(3)]
        self.dot_cv, self.dot_step = cv, 0
        self._tick_typing()
        self.scroll_bottom()

    def _tick_typing(self):
        if not self.typing_row or not self.typing_row.winfo_exists():
            return
        for i, d in enumerate(self.dots):
            self.dot_cv.itemconfigure(
                d, fill=self.t["accent"] if i == self.dot_step % 3 else self.t["muted"])
        self.dot_step += 1
        self.typing_job = self.after(230, self._tick_typing)

    def hide_typing(self):
        if self.typing_job:
            self.after_cancel(self.typing_job)
            self.typing_job = None
        if self.typing_row is not None:
            if self.typing_row.winfo_exists():
                self.typing_row.destroy()
            self.typing_row = None

    # ------------------------------------------------------------------
    # chat logic
    # ------------------------------------------------------------------
    def add_item(self, **kw):
        kw.setdefault("stamp", datetime.now().strftime("%I:%M %p").lstrip("0"))
        self.history.append(kw)
        return kw

    def submit(self):
        text = self.inputbar.get().strip()
        if text:
            self.inputbar.clear()
            self.ask(text)

    def ask(self, text):
        if self.busy:
            return
        self.hide_suggestions()
        self.sent.append(text)
        self.hpos = len(self.sent)
        self.asked += 1
        self.header.set_count(self.asked)
        it = self.add_item(who="user", text=text, kind="user")
        self.render_item(it)
        self.busy = True
        self.show_typing()
        self.scroll_bottom()
        self.after(520, lambda: self.respond(text))

    def respond(self, text):
        self.hide_typing()
        r = self.bot.reply(text)
        it = self.add_item(who="bot", text=r.text, kind=r.kind, score=r.score,
                           category=r.category, related=r.related, source=r.source)
        self.render_item(it, animate=True)
        self.scroll_bottom()

    def show_category(self, name, start=0):
        if self.busy and start == 0:
            return
        self.active_cat = name
        for n in self.cat_rows:
            self._cat_paint(n)
        qs = self.bot.by_category(name)
        page = qs[start:start + CHIPS_PER_PAGE]
        more = (name, start + CHIPS_PER_PAGE) if start + CHIPS_PER_PAGE < len(qs) else None
        intro = (f"{CAT_ICON[name]}  {name} - tap a question:" if start == 0
                 else f"{CAT_ICON[name]}  More about {name.lower()}:")
        it = self.add_item(who="bot", text=intro, kind="menu", chips=page, more=more)
        self.busy = True
        self.render_item(it, animate=False)
        self.scroll_bottom()

    # ------------------------------------------------------------------
    # history / suggestions
    # ------------------------------------------------------------------
    def history_up(self, _):
        if self.sent and self.hpos > 0:
            self.hpos -= 1
            self.inputbar.set(self.sent[self.hpos])
        return "break"

    def history_down(self, _):
        if self.hpos < len(self.sent) - 1:
            self.hpos += 1
            self.inputbar.set(self.sent[self.hpos])
        else:
            self.hpos = len(self.sent)
            self.inputbar.clear()
            self.inputbar.entry.focus_set()
            self.inputbar.entry.configure(fg=self.t["text"])
        return "break"

    def on_key(self, e):
        if e.keysym in ("Return", "Up", "Down", "Tab", "Escape", "Shift_L",
                        "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"):
            return
        text = self.inputbar.get()
        items = self.bot.suggest(text) if text.strip() else []
        self.show_suggestions(items)

    def show_suggestions(self, items):
        t = self.t
        for w in self.sugg.winfo_children():
            w.destroy()
        self.sugg_items = items
        if not items:
            self.sugg.grid_remove()
            return
        box = tk.Frame(self.sugg, bg=t["card_bg"], highlightthickness=1,
                       highlightbackground=t["border"])
        box.pack(fill="x")
        for q in items:
            lbl = tk.Label(box, text=f"🔎   {q}", bg=t["card_bg"], fg=t["text"],
                           font=(FONT, 10), anchor="w", padx=px(14), pady=px(6),
                           cursor="hand2")
            lbl.pack(fill="x")
            lbl.bind("<Enter>", lambda e, w=lbl: w.configure(bg=t["side_hover"]))
            lbl.bind("<Leave>", lambda e, w=lbl: w.configure(bg=t["card_bg"]))
            lbl.bind("<Button-1>", lambda e, q=q: (self.inputbar.clear(), self.ask(q)))
        tk.Label(box, text="Tab to accept the first suggestion  •  Esc to close",
                 bg=t["card_bg"], fg=t["muted"], font=(FONT, 8), anchor="e",
                 padx=px(12)).pack(fill="x")
        self.sugg.grid()

    def hide_suggestions(self):
        try:
            self.show_suggestions([])
        except tk.TclError:
            pass

    def accept_suggestion(self, _):
        if self.sugg_items:
            self.inputbar.set(self.sugg_items[0])
            self.hide_suggestions()
        return "break"

    # ------------------------------------------------------------------
    # toolbar actions
    # ------------------------------------------------------------------
    def toggle_theme(self):
        draft = self.inputbar.get() if hasattr(self, "inputbar") else ""
        self.theme_name = "dark" if self.theme_name == "light" else "light"
        self.t = THEMES[self.theme_name]
        self.hide_typing()
        self.busy = False
        self.build_ui()
        if draft:
            self.inputbar.set(draft)
        self.after(50, self.header.redraw)

    def clear_chat(self):
        if self.busy:
            return
        self.history.clear()
        self.asked = 0
        self.active_cat = None
        self.header.set_count(0)
        for n in self.cat_rows:
            self._cat_paint(n)
        self.redraw_history()

    def save_chat(self):
        if not self.history:
            messagebox.showinfo("Nothing to save", "Start a chat first!")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text file", "*.txt")],
            initialfile="mriirs_chat.txt")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write("MRIIRS Campus Assistant - chat export\n" + "=" * 40 + "\n\n")
            for it in self.history:
                if it["kind"] == "menu":
                    continue
                who = "You" if it["who"] == "user" else "Assistant"
                f.write(f"[{it['stamp']}] {who}: {it['text']}\n\n")
        messagebox.showinfo("Saved", f"Chat saved to:\n{path}")


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
