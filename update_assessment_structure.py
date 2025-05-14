"""
Update assessment structure data in the database to match official IELTS test types.
"""
import json
from app import app, db
from models import AssessmentStructure

# Assessment structure data based on https://ielts.org/take-a-test/test-types
assessment_structures = [
    {
        "test_type": "academic",
        "description": "IELTS Academic measures your English language proficiency for academic study and professional registration purposes. It reflects aspects of academic language and assesses if you're ready to begin training or studying in English.",
        "format_details": {
            "listening": "Listening: 30 minutes, 4 sections with 40 questions. A variety of question types including multiple choice, matching, plan/map/diagram labeling, form completion, note completion, table completion, flow-chart completion, summary completion, sentence completion, and short-answer questions.",
            "reading": "Reading: 60 minutes, 3 sections with 40 questions. Each section contains one long text of up to 900 words. Texts are authentic from books, journals, magazines, newspapers, and online sources.",
            "writing": "Writing: 60 minutes, 2 tasks. Task 1: Describe and interpret visual information (graph, table, chart, diagram). Task 2: Respond to an argument or problem with a 250-word essay.",
            "speaking": "Speaking: 11-14 minutes, three-part face-to-face interview with an examiner. Part 1: Introduction and general questions. Part 2: Individual long turn on a familiar topic. Part 3: Two-way discussion related to Part 2."
        },
        "sample_image_url": "https://takeielts.britishcouncil.org/sites/default/files/styles/bc_image_1x1/public/ielts_academic_0.jpg"
    },
    {
        "test_type": "general_training",
        "description": "IELTS General Training measures your English language proficiency in a practical, everyday context. It's suitable for those planning to study or train in English at below degree level, work or undertake work-related training in an English-speaking environment, or migrate to an English-speaking country.",
        "format_details": {
            "listening": "Listening: 30 minutes, 4 sections with 40 questions. A variety of question types including multiple choice, matching, plan/map/diagram labeling, form completion, note completion, table completion, flow-chart completion, summary completion, sentence completion, and short-answer questions.",
            "reading": "Reading: 60 minutes, 3 sections with 40 questions. Section 1: Contains two or three short factual texts. Section 2: Contains two short factual texts focusing on work-related issues. Section 3: Contains one longer, more complex text on a topic of general interest.",
            "writing": "Writing: 60 minutes, 2 tasks. Task 1: Write a letter in response to a given situation (personal, semi-formal or formal style). Task 2: Write an essay in response to an argument or problem.",
            "speaking": "Speaking: 11-14 minutes, three-part face-to-face interview with an examiner. Part 1: Introduction and general questions. Part 2: Individual long turn on a familiar topic. Part 3: Two-way discussion related to Part 2."
        },
        "sample_image_url": "https://takeielts.britishcouncil.org/sites/default/files/styles/bc_image_1x1/public/ielts_general_training.jpg"
    },
    {
        "test_type": "ukvi",
        "description": "IELTS for UK Visas and Immigration (UKVI) is an IELTS test specifically designed for UK visa and immigration purposes. Both Academic and General Training versions are available, with the test conducted in UKVI-approved locations with increased security protocols.",
        "format_details": {
            "listening": "Same content and format as standard IELTS Listening, but conducted in an approved UKVI test center.",
            "reading": "Same content and format as standard IELTS Reading (Academic or General Training), but conducted in an approved UKVI test center.",
            "writing": "Same content and format as standard IELTS Writing (Academic or General Training), but conducted in an approved UKVI test center.",
            "speaking": "Same content and format as standard IELTS Speaking, but conducted in an approved UKVI test center."
        },
        "sample_image_url": "https://takeielts.britishcouncil.org/sites/default/files/styles/bc_image_16_9/public/2022-06/ielts-ukvi-information-700x394.jpg"
    },
    {
        "test_type": "life_skills",
        "description": "IELTS Life Skills is an English test for people who need to demonstrate their English speaking and listening skills at Levels A1, A2 or B1 of the Common European Framework of Reference for Languages (CEFR). It's specifically designed for UK visa and immigration purposes.",
        "format_details": {
            "listening_and_speaking": "The test takes 16-18 minutes for CEFR Level A1, 20 minutes for CEFR Level A2, and 22 minutes for CEFR Level B1. It consists of a face-to-face speaking and listening test with one examiner and two test takers. This provides a more realistic and interactive context for test takers to demonstrate communication in English.",
            "tasks": "Tasks include asking for and giving personal information, communicating needs, expressing feelings, expressing opinions, explaining, presenting information, and turn-taking. The test is assessed based on the ability to obtain key information from spoken text, understand instructions, and speak to communicate basic information, opinions, and feelings."
        },
        "sample_image_url": "https://takeielts.britishcouncil.org/sites/default/files/styles/bc_image_16_9/public/2022-06/ielts-life-skills-700x394.jpg"
    },
    {
        "test_type": "ielts_online",
        "description": "IELTS Online is a new test option that offers you the convenience of taking your IELTS Academic test from your home or another suitable location. It offers the same trusted IELTS quality but with the flexibility of online delivery.",
        "format_details": {
            "format": "The test has the same content, format, and level of difficulty as the paper-based and computer-delivered IELTS Academic test. It includes Listening, Reading, Writing, and Speaking sections, with the Speaking test conducted face-to-face online with a trained IELTS Examiner.",
            "security": "Advanced security measures are in place, including ID verification, facial recognition, and human proctoring throughout the test.",
            "requirements": "Test takers need a quiet, private room, a computer with camera, microphone, and speakers/headphones, a stable internet connection, and a smartphone for room security checks."
        },
        "sample_image_url": "https://takeielts.britishcouncil.org/sites/default/files/styles/bc_image_16_9/public/2023-02/ielts-online-information-700x394.jpg"
    }
]

with app.app_context():
    # Clear existing assessment structures
    AssessmentStructure.query.delete()
    
    # Add new assessment structures
    for structure_data in assessment_structures:
        assessment_structure = AssessmentStructure(
            test_type=structure_data["test_type"],
            description=structure_data["description"],
            format_details=json.dumps(structure_data["format_details"]),
            sample_image_url=structure_data["sample_image_url"]
        )
        db.session.add(assessment_structure)
    
    db.session.commit()
    print("Updated assessment structure data with official IELTS assessment types")