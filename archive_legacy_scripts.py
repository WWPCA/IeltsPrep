#!/usr/bin/env python3
import os
import shutil
from datetime import datetime

def create_backup_directory():
    """Create a backup directory with timestamp"""
    backup_dir = f"legacy_test_scripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")
    return backup_dir

def move_files_to_backup(file_list, backup_dir):
    """Move specified files to the backup directory"""
    moved_count = 0
    for filename in file_list:
        if os.path.exists(filename):
            try:
                shutil.move(filename, os.path.join(backup_dir, filename))
                moved_count += 1
                print(f"Moved: {filename}")
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        else:
            print(f"File does not exist: {filename}")
    
    return moved_count

def main():
    # List of legacy test-related scripts to archive
    legacy_scripts = [
        # Check scripts
        "check_academic_reading_test.py",
        "check_academic_writing_tests.py",
        "check_all_test_counts.py",
        "check_and_fix_listening_test.py",
        "check_general_reading_test.py",
        "check_general_writing_tests.py",
        "check_listening_tests.py",
        "check_one_speaking_test.py",
        "check_reading_tests.py",
        "check_reading_test_structure.py",
        "check_speaking_tests.py",
        "check_speaking_test_structure.py",
        "check_test_database.py",
        "check_test_structure.py",
        "check_test_types.py",
        
        # Add scripts
        "add_general_reading_matching_features.py",
        "add_general_reading_multiple_choice.py",
        "add_general_reading_note_completion.py",
        "add_general_reading_sentence_completion.py",
        "add_general_reading_summary_completion.py",
        "add_general_reading_true_false_not_given.py",
        "add_more_tests.py",
        "add_writing_test_with_graphs.py",
        
        # Create scripts
        "create_general_reading_structure.py",
        "create_general_test_user.py",
        
        # Utility scripts
        "count_tests.py",
    ]
    
    # Create backup directory
    backup_dir = create_backup_directory()
    
    # Move files to backup directory
    moved_count = move_files_to_backup(legacy_scripts, backup_dir)
    
    print(f"\nArchiving complete: {moved_count} legacy test scripts moved to {backup_dir}")
    print(f"These files can be reviewed if needed, but should be considered deprecated.")

if __name__ == "__main__":
    main()