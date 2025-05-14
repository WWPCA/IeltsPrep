"""
Update Reading Tests with New Question Types

This script updates the reading tests in the database with the enhanced question types
from the updated IELTS Reading Context File, including:
- Heading matching questions
- Multiple choice (select TWO) questions
- Summary completion questions
"""
import json
import sys
from datetime import datetime
import re

from app import app, db
from models import PracticeTest, CompletePracticeTest

def extract_headings_section(content):
    """Extract a heading matching section from the content"""
    # Look for a pattern like "Questions 14–17" followed by "List of Headings"
    headings_pattern = r'Questions\s+(\d+)[-–](\d+)\s*\n\s*The text has.*?sections.*?[\n\r]\s*List of Headings(.*?)(?=\n\s*[A-Z])'
    headings_match = re.search(headings_pattern, content, re.DOTALL)
    
    if not headings_match:
        # Try an alternative pattern if the first one doesn't match
        headings_pattern = r'Questions\s+(\d+)[-–](\d+)\s*\n\s*List of Headings(.*?)(?=Questions \d+[-–]\d+|$)'
        headings_match = re.search(headings_pattern, content, re.DOTALL)
        
        if not headings_match:
            return None
    
    # Extract the heading numbers and content
    start_q = int(headings_match.group(1))
    end_q = int(headings_match.group(2))
    headings_content = headings_match.group(3).strip()
    
    # Extract the list of headings
    heading_list = []
    for line in headings_content.split('\n'):
        line = line.strip()
        if line and re.match(r'^\d+\s+', line):
            match_result = re.match(r'^(\d+)\s+(.*?)$', line)
            if match_result:
                heading_number, heading_text = match_result.groups()
                heading_list.append({
                    'number': int(heading_number),
                    'text': heading_text
                })
    
    # Find the title and paragraphs
    title_pattern = r'(?:List of Headings.*?)[\n\r]\s*([A-Z][^\n]*?)(?=\n)'
    title_match = re.search(title_pattern, content[headings_match.start():], re.DOTALL)
    
    title = "Reading Passage"
    title_end = 0
    if title_match:
        title = title_match.group(1).strip()
        title_end = title_match.end()
    
    # Extract the paragraphs to match
    paragraphs_pattern = r'(.*?)(?=Questions \d+[-–]\d+|$)'
    # Start searching after the end of the headings and title
    search_start = headings_match.end() + title_end
    paragraphs_match = re.search(paragraphs_pattern, content[search_start:], re.DOTALL)
    
    paragraphs_text = ""
    if paragraphs_match:
        paragraphs_text = paragraphs_match.group(1).strip()
    else:
        # Try a simpler approach to extract the content
        next_heading = re.search(r'Questions\s+\d+[-–]\d+', content[headings_match.end():], re.DOTALL)
        if next_heading:
            paragraphs_text = content[headings_match.end():headings_match.end() + next_heading.start()].strip()
    
    # Extract individual paragraphs (text separated by blank lines)
    paragraphs = []
    paragraph_number = 1
    
    # Split on paragraph breaks (double newlines)
    for paragraph in re.split(r'\n\s*\n', paragraphs_text):
        if paragraph.strip():
            paragraphs.append({
                'number': paragraph_number,
                'text': paragraph.strip()
            })
            paragraph_number += 1
    
    return {
        'start_question': start_q,
        'end_question': end_q,
        'title': title,
        'headings': heading_list,
        'paragraphs': paragraphs,
        'type': 'heading_matching'
    }

def extract_multiple_select_section(content):
    """Extract multiple selection questions (select TWO) from the content"""
    # Look for patterns like "18–19" followed by "Which TWO options"
    multiple_select_pattern = r'(\d+)[-–](\d+)\s*\n\s*Which TWO\s+(options|statements)(.*?)(?=\d+[-–]\d+|Questions \d+[-–]\d+|$)'
    matches = re.finditer(multiple_select_pattern, content, re.DOTALL)
    
    multiple_select_questions = []
    
    for match in matches:
        start_q = int(match.group(1))
        end_q = int(match.group(2))
        question_type = match.group(3)  # "options" or "statements"
        question_content = match.group(4).strip()
        
        # Get question text
        question_text = ""
        q_text_match = re.search(r'(describe|reflect|express|.*?the\s+\w+\s+.*?)\?', question_content, re.IGNORECASE)
        if q_text_match:
            question_text = q_text_match.group(0).strip()
        
        # Extract the options
        options = []
        # Split by newlines and look for options
        for line in question_content.split('\n'):
            line = line.strip()
            # Skip empty lines and lines with question instruction
            if not line or 'Which TWO' in line or line.endswith('?'):
                continue
            # Add the line as an option if it's not just a letter or a short word
            if len(line) > 3:
                options.append(line)
        
        multiple_select_questions.append({
            'start_question': start_q,
            'end_question': end_q,
            'question_text': question_text,
            'options': options,
            'type': 'multiple_select_two'
        })
    
    return multiple_select_questions

def extract_summary_completion(content):
    """Extract summary completion questions from the content"""
    # Look for patterns like "Questions 24–26" followed by "Complete the summary"
    summary_pattern = r'Questions\s+(\d+)[-–](\d+)\s*\n\s*Complete the summary(.*?)(?=Questions \d+[-–]\d+|$)'
    summary_match = re.search(summary_pattern, content, re.DOTALL)
    
    if not summary_match:
        return None
    
    start_q = int(summary_match.group(1))
    end_q = int(summary_match.group(2))
    summary_content = summary_match.group(3).strip()
    
    # Extract the summary text with blanks
    instructions_split = re.split(r'Write ONE WORD ONLY.*?from the text', summary_content, flags=re.IGNORECASE | re.DOTALL)
    
    if len(instructions_split) > 1:
        summary_text = instructions_split[1].strip()
    else:
        # Try another pattern if the first one doesn't match
        instructions_split = re.split(r'Write ONE WORD ONLY', summary_content, flags=re.IGNORECASE | re.DOTALL)
        if len(instructions_split) > 1:
            summary_text = instructions_split[1].strip()
        else:
            summary_text = summary_content  # Use the whole content if we can't find the specific pattern
    
    # Find all blanks in the summary text
    blank_positions = []
    for match in re.finditer(r'\_\_\_\_\_\_\_\_', summary_text):
        blank_positions.append(match.start())
    
    # If we can't find blanks with 8 underscores, try with different numbers
    if not blank_positions:
        for underscore_count in range(4, 10):
            pattern = '_' * underscore_count
            for match in re.finditer(pattern, summary_text):
                # Only count it if it's not part of a longer sequence
                if not re.match(r'_{10,}', summary_text[max(0, match.start()-5):min(len(summary_text), match.end()+5)]):
                    blank_positions.append(match.start())
    
    return {
        'start_question': start_q,
        'end_question': end_q,
        'summary_text': summary_text,
        'blank_positions': blank_positions,
        'type': 'summary_completion'
    }

def process_reading_content(content):
    """
    Process reading test content to extract different question types
    
    Args:
        content (str): The raw reading test content
        
    Returns:
        dict: Structured questions by type
    """
    # Extract normal questions first (True/False/Not Given and Fill in the blanks)
    normal_questions = []
    
    # Extract questions in the format "(1-6: Choose True, False, or Not Given)"
    tf_pattern = r'\((\d+)-(\d+): Choose True, False, or Not Given\)(.*?)(?=\(|$)'
    tf_matches = re.finditer(tf_pattern, content, re.DOTALL)
    
    for match in tf_matches:
        start_num = int(match.group(1))
        end_num = int(match.group(2))
        questions_text = match.group(3).strip()
        
        # Extract each question
        for i, line in enumerate(questions_text.split('\n')):
            line = line.strip()
            if line and re.match(r'^\d+\.', line):
                match_result = re.match(r'^(\d+)\.\s+(.*?)$', line)
                if match_result:
                    question_number, question_text = match_result.groups()
                    
                    if int(question_number) >= start_num and int(question_number) <= end_num:
                        normal_questions.append({
                            'number': int(question_number),
                            'text': question_text,
                            'type': 'true_false_not_given',
                            'options': ['True', 'False', 'Not Given']
                        })
    
    # Extract Fill in the blank questions
    fill_pattern = r'\((\d+)-(\d+): Fill in the blank.*?\)(.*?)(?=\(|$)'
    fill_matches = re.finditer(fill_pattern, content, re.DOTALL)
    
    for match in fill_matches:
        start_num = int(match.group(1))
        end_num = int(match.group(2))
        questions_text = match.group(3).strip()
        
        # Extract each question
        for i, line in enumerate(questions_text.split('\n')):
            line = line.strip()
            if line and re.match(r'^\d+\.', line):
                match_result = re.match(r'^(\d+)\.\s+(.*?)$', line)
                if match_result:
                    question_number, question_text = match_result.groups()
                    
                    if int(question_number) >= start_num and int(question_number) <= end_num:
                        # Look for blank spaces in the question
                        if '________' in question_text:
                            normal_questions.append({
                                'number': int(question_number),
                                'text': question_text,
                                'type': 'fill_in_blank'
                            })
    
    # Extract heading matching questions
    heading_section = extract_headings_section(content)
    
    # Extract multiple select questions
    multiple_select_questions = extract_multiple_select_section(content)
    
    # Extract summary completion questions
    summary_section = extract_summary_completion(content)
    
    # Combine all question types
    result = {
        'normal_questions': normal_questions,
        'heading_section': heading_section,
        'multiple_select_questions': multiple_select_questions,
        'summary_section': summary_section
    }
    
    return result

def update_reading_test(test_id, content):
    """
    Update a reading test with new question types
    
    Args:
        test_id (int): The test ID to update
        content (str): The new reading content
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        test = PracticeTest.query.filter_by(id=test_id).first()
        if not test or test.test_type != 'reading':
            print(f"Test {test_id} not found or is not a reading test")
            return False
        
        # Parse the content to extract question types
        questions_data = process_reading_content(content)
        
        # Extract passage from content (first section before questions)
        passage_text = ""
        passage_match = re.search(r'\*\*\* PASSAGE \d+:.*?\*\*\*(.*?)(?=\*\* Questions|\(1-\d+:|Questions \d+)', content, re.DOTALL)
        if passage_match:
            passage_text = passage_match.group(1).strip()
        else:
            # Try another pattern
            passage_match = re.search(r'Read the text and answer questions.*?\n\n(.*?)(?=\*\* Questions|\(1-\d+:|Questions \d+)', content, re.DOTALL)
            if passage_match:
                passage_text = passage_match.group(1).strip()
            else:
                # Fallback to using the first part of the content
                passage_lines = []
                lines = content.split('\n')
                for line in lines:
                    if 'Questions ' in line or 'Choose True, False' in line:
                        break
                    passage_lines.append(line)
                passage_text = '\n'.join(passage_lines).strip()
        
        # Create updated questions data
        all_questions = []
        
        # Add normal questions
        for q in questions_data.get('normal_questions', []):
            all_questions.append(q)
        
        # Add heading matching questions
        if questions_data.get('heading_section'):
            heading_section = questions_data['heading_section']
            paragraphs = heading_section.get('paragraphs', [])
            
            # Include paragraph text in the heading section
            for q_num in range(heading_section['start_question'], heading_section['end_question'] + 1):
                paragraph_index = q_num - heading_section['start_question']
                paragraph_text = ""
                if paragraph_index < len(paragraphs):
                    paragraph_text = paragraphs[paragraph_index].get('text', '')
                
                all_questions.append({
                    'number': q_num,
                    'text': f'Which heading best matches paragraph {paragraph_index + 1}?',
                    'type': 'heading_matching',
                    'headings': heading_section['headings'],
                    'paragraph_index': paragraph_index,
                    'paragraph_text': paragraph_text
                })
        
        # Add multiple select questions
        for ms_section in questions_data.get('multiple_select_questions', []):
            question_text = ms_section.get('question_text', 'Select TWO correct options:')
            if not question_text:
                question_text = 'Select TWO correct options:'
                
            all_questions.append({
                'number': ms_section['start_question'],
                'text': question_text,
                'type': 'multiple_select_two',
                'options': ms_section['options']
            })
        
        # Add summary completion questions
        if questions_data.get('summary_section'):
            summary = questions_data['summary_section']
            blank_positions = summary.get('blank_positions', [])
            
            for i, q_num in enumerate(range(summary['start_question'], summary['end_question'] + 1)):
                if i < len(blank_positions):
                    blank_position = blank_positions[i]
                    # Get the context around the blank
                    start = max(0, blank_position - 50)
                    end = min(len(summary['summary_text']), blank_position + 50)
                    
                    # Replace underscores with a placeholder
                    context = summary['summary_text'][start:end]
                    # Find the blank in the context
                    blank_start = blank_position - start
                    blank_end = blank_start
                    while blank_end < len(context) and context[blank_end] == '_':
                        blank_end += 1
                    
                    # Replace the blank with a standardized blank
                    context = context[:blank_start] + '________' + context[blank_end:]
                    
                    all_questions.append({
                        'number': q_num,
                        'text': f'Complete the summary with ONE WORD from the passage: {context}',
                        'type': 'summary_completion'
                    })
        
        # Update the test questions
        updated_questions = {
            'passage': passage_text,
            'questions': sorted(all_questions, key=lambda q: q['number'])
        }
        
        test.questions = updated_questions
        db.session.commit()
        
        print(f"Successfully updated test {test_id} with new question types")
        return True
        
    except Exception as e:
        print(f"Error updating test {test_id}: {str(e)}")
        return False

def fix_duplicate_questions(test_id):
    """
    Fix the problem of duplicate questions by keeping only unique question numbers
    
    Args:
        test_id (int): The test ID to fix
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        test = PracticeTest.query.filter_by(id=test_id).first()
        if not test or test.test_type != 'reading':
            print(f"Test {test_id} not found or is not a reading test")
            return False
        
        # Get current questions
        if not isinstance(test.questions, dict) or 'questions' not in test.questions:
            print(f"Test {test_id} has invalid question format")
            return False
        
        # Group questions by number
        questions_by_number = {}
        for q in test.questions['questions']:
            q_num = q.get('number')
            if q_num not in questions_by_number:
                questions_by_number[q_num] = []
            questions_by_number[q_num].append(q)
        
        # Keep only the first question for each number
        unique_questions = []
        for q_num, q_list in questions_by_number.items():
            unique_questions.append(q_list[0])
        
        # Update with unique questions
        test.questions['questions'] = sorted(unique_questions, key=lambda q: q['number'])
        db.session.commit()
        
        print(f"Fixed test {test_id}: reduced from {len(test.questions['questions'])} to {len(unique_questions)} questions")
        return True
    
    except Exception as e:
        print(f"Error fixing test {test_id}: {str(e)}")
        return False

def update_all_reading_tests():
    """Update all reading tests with content from the IELTS Reading Context File"""
    try:
        # Read the content file
        with open('attached_assets/IELTS Reading Context File.txt', 'r') as f:
            content = f.read()
            
        # Look for test sections with part numbers
        test_pattern = r'Part (\d+) - Test (\d+)'
        test_matches = list(re.finditer(test_pattern, content))
        
        if not test_matches:
            print("No test sections found with the expected format")
            # Try to process the whole file as one test
            raw_tests = [content]
        else:
            # Split content based on test section markers
            raw_tests = []
            for i, match in enumerate(test_matches):
                start_pos = match.start()
                # If this is the last match, go to the end of the file
                if i == len(test_matches) - 1:
                    test_content = content[start_pos:]
                else:
                    end_pos = test_matches[i + 1].start()
                    test_content = content[start_pos:end_pos]
                raw_tests.append(test_content)
            
        print(f"Found {len(raw_tests)} raw test sections in the file.")
        
        # Get all reading tests
        reading_tests = PracticeTest.query.filter_by(test_type='reading').all()
        
        if not reading_tests:
            print("No reading tests found in the database")
            return
            
        print(f"Found {len(reading_tests)} reading tests in the database")
        
        # Group tests by complete test ID
        tests_by_complete_id = {}
        for test in reading_tests:
            if test.complete_test_id:
                if test.complete_test_id not in tests_by_complete_id:
                    tests_by_complete_id[test.complete_test_id] = []
                tests_by_complete_id[test.complete_test_id].append(test)
        
        # Get all complete tests
        complete_tests = CompletePracticeTest.query.filter(CompletePracticeTest.id.in_(list(tests_by_complete_id.keys()))).all()
        complete_tests_by_key = {}
        
        for test in complete_tests:
            key = f"{test.ielts_test_type}_{test.test_number}"
            complete_tests_by_key[key] = test
            
        # Process only the first test content for now
        test_content = raw_tests[0]
        
        # Update test 1 in each pair of academic/general tests
        for test_type in ['academic', 'general']:
            key = f"{test_type}_1"  # Only update test 1 for now
            
            if key in complete_tests_by_key:
                complete_test = complete_tests_by_key[key]
                if complete_test.id in tests_by_complete_id:
                    for test in tests_by_complete_id[complete_test.id]:
                        if test.test_type == 'reading':
                            print(f"Updating {test_type} test 1 (ID: {test.id})")
                            update_reading_test(test.id, test_content)
                            # Fix duplicates after update
                            fix_duplicate_questions(test.id)
            else:
                print(f"No complete test found for {key}")
                
        print("Reading tests updated successfully!")
        
    except Exception as e:
        print(f"Error updating reading tests: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        update_all_reading_tests()