"""
Generate improved listening test audio files using AWS Polly following official IELTS format.
"""
import os
import time
from aws_services import generate_polly_speech
from models import PracticeTest
from app import app, db
import json

def generate_ielts_style_listening_audio():
    """Generate audio for an IELTS listening test section following the official format."""
    
    # This script follows the official IELTS format with proper instructions and pauses
    script = """
    NARRATOR: IELTS Listening. Test 1.
    
    You will hear a number of different recordings and you will have to answer questions on what you hear.
    
    There will be time for you to read the instructions and questions, and you will have a chance to check your work.
    
    All the recordings will be played once only.
    
    The test is in four sections. Now turn to section 1.
    
    [5-second pause]
    
    NARRATOR: Section 1. You will hear a conversation between a travel agent and a customer who wants to book a holiday.
    
    First, you have some time to look at questions 1 to 5.
    
    [30-second pause]
    
    NARRATOR: You will see that there is an example that has been done for you. On this occasion only, the conversation relating to this will be played first.
    
    [2-second pause]
    
    AGENT: Good morning, Welcome to Sunshine Travel. How can I help you today?
    
    CUSTOMER: Hello. I'd like to book a holiday for me and my husband.
    
    AGENT: Of course. May I have your name please?
    
    CUSTOMER: It's Johnson. Sarah Johnson.
    
    NARRATOR: The customer's name is Sarah Johnson, so "Johnson" has been written in the space. Now we shall begin. You should answer the questions as you listen, because you will not hear the recording a second time. Listen carefully and answer questions 1 to 5.
    
    [2-second pause]
    
    AGENT: Good morning, Welcome to Sunshine Travel. How can I help you today?
    
    CUSTOMER: Hello. I'd like to book a holiday for me and my husband. We're thinking of going somewhere warm in June.
    
    AGENT: June is a great time to travel. Do you have a specific destination in mind?
    
    CUSTOMER: We're considering Spain or Greece, but we're open to suggestions.
    
    AGENT: Both are excellent choices for June. The weather will be lovely - warm but not too hot. Do you have a specific budget in mind?
    
    CUSTOMER: We're thinking around £1000 pounds in total for the two of us, including flights and accommodation.
    
    AGENT: I see. That's quite a reasonable budget for a European destination. How long are you planning to stay?
    
    CUSTOMER: We're thinking of a one-week holiday, possibly from the 15th to the 22nd.
    
    AGENT: Let me check what we have available for those dates.
    
    [typing sounds]
    
    AGENT: I have several options for you. There's a lovely beach resort in Costa del Sol, Spain. It's a 3-star hotel with breakfast included, and it's just a 5-minute walk from the beach. The total for two people would be £950.
    
    CUSTOMER: That sounds promising. What about in Greece?
    
    AGENT: For Greece, I have a nice apartment on the island of Crete. It's self-catering, so no meals are included, but it has a fully equipped kitchen. It's about a 10-minute walk to the beach and costs £880 total.
    
    CUSTOMER: The Crete option sounds good. Are there any restaurants near the apartment?
    
    AGENT: Yes, there are several tavernas within walking distance. The area is called Agios Nikolaos, which is a beautiful traditional town with lots of local restaurants and shops.
    
    CUSTOMER: That sounds perfect. I think we'll go with the Crete option.
    
    AGENT: Excellent choice. Now, I'll need some information from you to make the booking. I already have your name, Sarah Johnson. Could I have a contact number, please?
    
    CUSTOMER: Sure, it's 07700 900 123.
    
    AGENT: Thank you. And an email address?
    
    CUSTOMER: It's sarahjohnson@email.com.
    
    AGENT: Great. Now, I'll need the full names of both travelers as they appear on your passports.
    
    CUSTOMER: Sarah Johnson and Michael Johnson.
    
    AGENT: Thank you. Now, what's your preferred location in Agios Nikolaos? We have apartments near the center or closer to the beach.
    
    CUSTOMER: We'd prefer to be closer to the beach, please.
    
    NARRATOR: Before you hear the rest of the conversation, you have some time to look at questions 6 to 10.
    
    [30-second pause]
    
    NARRATOR: Now listen and answer questions 6 to 10.
    
    AGENT: Before we finalize the booking, I should mention that we offer some optional extras that might enhance your holiday experience. For instance, would you like to pre-book airport transfers?
    
    CUSTOMER: How much would that cost?
    
    AGENT: A return transfer for two people would be an additional £45.
    
    CUSTOMER: Yes, let's add that. It would be more convenient than finding a taxi.
    
    AGENT: Absolutely. Also, we can arrange car rental if you'd like to explore the island. A compact car for the week would be £120.
    
    CUSTOMER: Actually, I don't think we'll need a car. We're planning to mostly relax at the beach and explore the local area on foot.
    
    AGENT: That's fine. Agios Nikolaos is very walkable, and there are local buses if you want to visit other towns. Now, would you like to purchase travel insurance through us?
    
    CUSTOMER: No, thank you. We already have annual travel insurance.
    
    AGENT: Great. One last thing - we can arrange some excursions for you in advance. There's a popular day trip to the island of Spinalonga, which has an interesting history as a former leper colony. It costs £30 per person.
    
    CUSTOMER: That sounds interesting. Yes, let's book that as well.
    
    AGENT: Perfect. I'll add that to your booking. So, with the apartment at £880, airport transfers at £45, and the Spinalonga excursion at £60 for two people, your new total comes to £985.
    
    CUSTOMER: That still fits our budget, so that's fine.
    
    AGENT: Great. The deposit today will be £197. Now, just a few practical details: your flights will depart from London Gatwick at 10:30 AM on the 15th, arriving in Heraklion at 4:15 PM local time. The return flight on the 22nd leaves Heraklion at 5:30 PM, arriving back at Gatwick at 7:45 PM UK time.
    
    CUSTOMER: That sounds good. Do we need to arrange visas?
    
    AGENT: No, as British citizens you don't need visas for Greece as it's in the EU. You just need to ensure your passports are valid for at least 6 months beyond your return date.
    
    CUSTOMER: That's fine, our passports are valid until 2028.
    
    AGENT: Perfect. Now, I'll process the payment for your deposit. Once that's done, I'll send all the booking details to your email. You'll receive confirmation within the next hour.
    
    CUSTOMER: Great, thank you for your help.
    
    AGENT: You're very welcome. I'm sure you'll have a wonderful time in Crete. Please don't hesitate to contact us if you have any questions before your trip. Have a lovely day!
    
    CUSTOMER: Thank you, you too!
    
    NARRATOR: That is the end of section 1. You now have half a minute to check your answers.
    
    [30-second pause]
    
    NARRATOR: Now turn to section 2.
    
    [5-second pause]
    """
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join('static', 'uploads', 'audio')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp to avoid caching issues
    timestamp = int(time.time())
    filename = f"ielts_listening_section1_{timestamp}.mp3"
    output_path = os.path.join(output_dir, filename)
    
    # Use AWS Polly to generate the audio file
    success = generate_polly_speech(script, output_path)
    
    if success:
        print(f"Successfully generated audio file at: {output_path}")
        
        # Update the database with the new audio file path and improved questions
        with app.app_context():
            # Find the first listening test
            test = PracticeTest.query.filter_by(test_type='listening').first()
            
            if test:
                # Update the audio URL
                test.audio_url = output_path.replace('static/', '')
                
                # Update the title and description to match the new content
                test.title = "Section 1: Booking a Holiday"
                test.description = "A conversation between a travel agent and a customer who wants to book a holiday to Greece."
                
                # Create improved questions in the correct format for form completion
                questions = [
                    {
                        "number": "1-5",
                        "instructions": "Complete the form below. Write NO MORE THAN THREE WORDS AND/OR A NUMBER for each answer.",
                        "form_title": "HOLIDAY BOOKING FORM",
                        "form_fields": [
                            {
                                "field": "Customer contact number",
                                "answer_key": "1"
                            },
                            {
                                "field": "Total budget",
                                "answer_key": "2"
                            },
                            {
                                "field": "Holiday dates",
                                "answer_key": "3"
                            },
                            {
                                "field": "Accommodation type in Crete",
                                "answer_key": "4"
                            },
                            {
                                "field": "Preferred location",
                                "answer_key": "5"
                            }
                        ]
                    },
                    {
                        "number": "6-10",
                        "instructions": "Complete the table below about the additional services offered. Write NO MORE THAN TWO WORDS AND/OR A NUMBER for each answer.",
                        "table_title": "ADDITIONAL HOLIDAY SERVICES",
                        "table_headers": ["Service", "Cost", "Customer's Decision", "Notes"],
                        "table_rows": [
                            {
                                "facility": "Airport transfers",
                                "location": "£45",
                                "hours": "Accept",
                                "notes": "More ____ 6 than finding a taxi"
                            },
                            {
                                "facility": "Car rental",
                                "location": "£____ 7",
                                "hours": "Decline",
                                "notes": "Prefer to explore on foot"
                            },
                            {
                                "facility": "Travel insurance",
                                "location": "Not specified",
                                "hours": "Decline",
                                "notes": "Already have ____ 8 insurance"
                            },
                            {
                                "facility": "Excursion to ____ 9",
                                "location": "£30 per person",
                                "hours": "Accept",
                                "notes": "Former leper colony"
                            },
                            {
                                "facility": "Total cost",
                                "location": "£____ 10",
                                "hours": "Accept",
                                "notes": "Deposit: £197"
                            }
                        ]
                    }
                ]
                
                # Create answers
                answers = {
                    "1": "07700 900 123",
                    "2": "£1000",
                    "3": "15th to 22nd June",
                    "4": "self-catering apartment",
                    "5": "closer to the beach",
                    "6": "convenient",
                    "7": "120",
                    "8": "annual",
                    "9": "Spinalonga",
                    "10": "985"
                }
                
                # Update in the database
                test.questions = json.dumps(questions)
                test.answers = json.dumps(answers)
                
                db.session.commit()
                print(f"Updated database with new audio URL, questions, and answers")
            else:
                print("No listening test found in the database.")
        
        return output_path
    else:
        print("Failed to generate audio file.")
        return None

if __name__ == "__main__":
    generate_ielts_style_listening_audio()