"""
Add authentic Multiple Choice tests for General Training Reading.
This script adds real multiple choice questions to the database.
"""
import json
from app import app, db
from models import PracticeTest

def add_authentic_multiple_choice():
    """Add authentic Multiple Choice tests for General Training Reading."""
    
    # Define the 16 test sets
    test_sets = [
        {
            "title": "The Benefits of Volunteering",
            "passage": """Volunteering provides numerous benefits, enriching both individuals and communities. By dedicating their time to causes they care about, volunteers often experience a greater sense of purpose and personal fulfillment. This engagement can also lead to the development of valuable new skills and the expansion of their social networks. Furthermore, the act of volunteering has been shown to improve overall well-being and promote a more positive outlook on life. Communities also gain immensely from volunteer efforts, which address vital needs and foster a stronger sense of collective responsibility and connection.""",
            "question": "Which TWO benefits of volunteering are mentioned in the text?",
            "options": [
                "Financial gain",
                "Skill development",
                "Increased social isolation",
                "Sense of purpose",
                "Improved well-being"
            ],
            "answers": {
                "1": "B",
                "2": "D"
            }
        },
        {
            "title": "The Importance of Reading",
            "passage": """Reading is a fundamental skill that profoundly enriches lives in countless ways. It serves as a gateway to knowledge, significantly expands vocabulary, and enhances critical thinking abilities. The act of reading can also provide a source of entertainment and effectively reduce stress levels, and foster empathy and understanding of diverse perspectives. Cultivating regular reading habits contributes to lifelong learning, fueling personal growth, and intellectual development.""",
            "question": "Which TWO benefits of reading are given in the text?",
            "options": [
                "Reduced critical thinking",
                "Vocabulary expansion",
                "Stress reduction",
                "Financial gain",
                "Knowledge acquisition"
            ],
            "answers": {
                "1": "B",
                "2": "C"
            }
        },
        {
            "title": "The History of Coffee",
            "passage": """Coffee boasts a rich and fascinating history, with its origins traced back to Ethiopia before spreading across the globe. The stimulating effects of coffee were recognized centuries ago, and coffeehouses evolved into important social and cultural hubs, fostering intellectual exchange and community gatherings. Today, coffee stands as one of the world's most popular beverages, enjoyed in a diverse array of forms and traditions, deeply ingrained in daily routines and social rituals worldwide.""",
            "question": "According to the text, which TWO of the following are true about the history of coffee?",
            "options": [
                "It originated in South America.",
                "Coffeehouses were significant social centers.",
                "Its stimulating effects were discovered recently.",
                "It originated in Ethiopia.",
                "It is not a popular beverage."
            ],
            "answers": {
                "1": "B",
                "2": "D"
            }
        },
        {
            "title": "The Impact of Music",
            "passage": """Music exerts a profound impact on human emotions and overall well-being. It possesses the remarkable ability to evoke a wide spectrum of feelings, ranging from joy and excitement to deep sadness and tranquility. Music therapy is increasingly employed to address various physical and mental health conditions, while simply listening to music can effectively reduce stress and improve mood, promoting a greater sense of calm and focus.""",
            "question": "Which TWO of the following are mentioned in the text about music?",
            "options": [
                "It has no effect on emotions.",
                "It can evoke a wide range of feelings.",
                "It is not used in therapy.",
                "It can reduce stress.",
                "It can enhance cognitive function."
            ],
            "answers": {
                "1": "B",
                "2": "D"
            }
        },
        {
            "title": "The Benefits of Exercise",
            "passage": """Regular physical exercise is essential for maintaining optimal health and well-being. It plays a vital role in strengthening the cardiovascular system, effectively improving mood, and aiding in healthy weight management. Furthermore, consistent exercise significantly reduces the risk of developing chronic diseases, including heart disease, type 2 diabetes, and certain types of cancer, promoting a longer and healthier life.""",
            "question": "Which TWO benefits of exercise are mentioned in the text?",
            "options": [
                "Increased risk of chronic diseases",
                "Cardiovascular strengthening",
                "Mood improvement",
                "Weight gain",
                "Reduced risk of some cancers"
            ],
            "answers": {
                "1": "B",
                "2": "C"
            }
        },
        {
            "title": "The Importance of Sleep",
            "passage": """Adequate sleep is absolutely crucial for both physical and mental well-being. During sleep, the body undertakes essential repair processes, and the brain effectively consolidates memories, strengthening learning and cognitive function. Insufficient sleep, or sleep deprivation, can lead to persistent fatigue, impaired concentration, and a significantly increased risk of developing various health problems, negatively impacting overall quality of life.""",
            "question": "According to the text, which TWO of the following are true about sleep?",
            "options": [
                "The body repairs itself during sleep.",
                "Lack of sleep improves concentration.",
                "Adequate sleep is not important.",
                "The brain consolidates memories during sleep.",
                "Lack of sleep can lead to fatigue."
            ],
            "answers": {
                "1": "A",
                "2": "D"
            }
        },
        {
            "title": "The Role of Technology in Education",
            "passage": """Technology is rapidly transforming the landscape of education, providing educators and students with innovative new tools and resources for learning. Online courses offer flexible learning options, interactive simulations enhance engagement, and educational apps personalize instruction. Technology also facilitates seamless collaboration and communication between students and teachers, fostering a more dynamic and connected learning environment.""",
            "question": "Which TWO of the following are mentioned in the text about technology in education?",
            "options": [
                "It hinders collaboration.",
                "It provides new learning tools.",
                "It enhances the learning experience.",
                "It does not affect communication.",
                "It transforms education."
            ],
            "answers": {
                "1": "B",
                "2": "C"
            }
        },
        {
            "title": "The History of Photography",
            "passage": """Photography has revolutionized the way we capture and preserve memories, transforming how we document and share our experiences. From the early daguerreotypes to the sophisticated digital cameras of today, photography has undergone a remarkable evolution. It has emerged as a powerful art form, a crucial tool for documentation, and a versatile means of communication, shaping our understanding of the world and ourselves.""",
            "question": "Which TWO of the following are mentioned in the text about the history of photography?",
            "options": [
                "It has remained unchanged.",
                "It has evolved significantly.",
                "It is not an art form.",
                "It is a means of communication.",
                "It helps to preserve memories."
            ],
            "answers": {
                "1": "B",
                "2": "D"
            }
        },
        {
            "title": "The Impact of Climate Change",
            "passage": """Climate change represents a global challenge with far-reaching and potentially devastating consequences. Rising global temperatures, increasingly frequent and intense extreme weather events, and accelerating sea-level rise are profoundly affecting ecosystems, economies, and human societies worldwide. Addressing this complex issue demands urgent and concerted action on a global scale to aggressively reduce greenhouse gas emissions and implement effective adaptation strategies to mitigate its impact.""",
            "question": "Which TWO of the following are mentioned in the text about climate change?",
            "options": [
                "It has limited consequences.",
                "It causes rising temperatures.",
                "It leads to extreme weather events.",
                "It does not affect economies.",
                "It requires urgent action."
            ],
            "answers": {
                "1": "B",
                "2": "C"
            }
        },
        {
            "title": "The Importance of Water Conservation",
            "passage": """Water is an exceptionally precious resource that is absolutely essential for sustaining all forms of life on Earth. Conserving water is therefore of paramount importance to ensure its continued availability for future generations. Even simple, everyday actions, such as reducing water usage within the home and actively supporting water-efficient practices in agriculture and industry, can collectively make a substantial difference in safeguarding this vital resource.""",
            "question": "Which TWO of the following are mentioned in the text about water conservation?",
            "options": [
                "Water is not essential for life.",
                "Water is a precious resource.",
                "Conserving water is not important.",
                "Reducing water usage at home helps.",
                "Supporting water-efficient practices helps."
            ],
            "answers": {
                "1": "B",
                "2": "D"
            }
        },
        {
            "title": "The Benefits of Travel",
            "passage": """Travel offers a multitude of benefits, significantly broadening horizons, exposing individuals to diverse cultures, and creating lasting, cherished memories. It serves to enhance personal growth, increase understanding and empathy, and promote tolerance and open-mindedness. Furthermore, travel plays a vital role in supporting local economies and fostering meaningful connections between people from different parts of the world, contributing to a more interconnected global community.""",
            "question": "Which TWO benefits of travel are mentioned in the text?",
            "options": [
                "It narrows horizons.",
                "It exposes people to new cultures.",
                "It creates lasting memories.",
                "It decreases understanding.",
                "It hinders personal growth."
            ],
            "answers": {
                "1": "B",
                "2": "C"
            }
        },
        {
            "title": "The Impact of Social Media",
            "passage": """Social media has profoundly transformed communication and social interaction on a global scale. It connects individuals across geographical boundaries, facilitates the rapid sharing of information, and provides platforms for diverse forms of self-expression. However, this widespread connectivity also raises significant concerns regarding privacy, the spread of misinformation, and the prevalence of cyberbullying, demanding careful consideration of its ethical and societal implications.""",
            "question": "Which TWO impacts of social media are mentioned in the text?",
            "options": [
                "It has not transformed communication.",
                "It connects people globally.",
                "It facilitates information sharing.",
                "It does not raise privacy concerns.",
                "It provides platforms for self-expression."
            ],
            "answers": {
                "1": "B",
                "2": "C"
            }
        },
        {
            "title": "The Importance of a Healthy Diet",
            "passage": """A healthy and well-balanced diet provides the essential nutrients that the body requires to function optimally and maintain overall well-being. Such a diet emphasizes a diverse variety of fruits, vegetables, whole grains, and lean protein sources. Consistently consuming a balanced diet can significantly improve energy levels, effectively support immune function, and substantially reduce the risk of developing chronic diseases, promoting a healthier and more vibrant life.""",
            "question": "Which TWO of the following are mentioned in the text about a healthy diet?",
            "options": [
                "It includes only processed foods",
                "It provides essential nutrients.",
                "It improves energy levels.",
                "It reduces immune function.",
                "It increases the risk of chronic diseases."
            ],
            "answers": {
                "1": "B",
                "2": "C"
            }
        },
        {
            "title": "The Role of Renewable Energy",
            "passage": """Renewable energy sources, including solar, wind, and hydropower, are playing an increasingly crucial role in meeting the world's growing energy demands. These sources offer a cleaner and more sustainable alternative to traditional fossil fuels, significantly reducing greenhouse gas emissions and mitigating the adverse effects of climate change, paving the way for a more environmentally responsible energy future.""",
            "question": "Which TWO of the following are mentioned in the text about renewable energy?",
            "options": [
                "They are not important for global energy demands.",
                "Solar is a type of renewable energy.",
                "They are a cleaner alternative to fossil fuels.",
                "They increase greenhouse gas emissions.",
                "Wind power is a renewable energy."
            ],
            "answers": {
                "1": "B",
                "2": "C"
            }
        },
        {
            "title": "The Benefits of Lifelong Learning",
            "passage": """Lifelong learning, the continuous and voluntary pursuit of knowledge and skills throughout one's life, offers numerous benefits for personal and professional development. It enhances individuals' adaptability to change, expands career opportunities, and promotes active participation in society. Embracing a lifelong learning mindset empowers individuals to thrive in a dynamic and ever-evolving world, fostering resilience and a growth-oriented approach to life.""",
            "question": "Which TWO benefits of lifelong learning are mentioned in the text?",
            "options": [
                "It limits personal development.",
                "It expands career opportunities.",
                "It promotes active citizenship.",
                "It hinders adaptation to change.",
                "It is not important for a dynamic world."
            ],
            "answers": {
                "1": "B",
                "2": "C"
            }
        },
        {
            "title": "The Impact of E-commerce",
            "passage": """E-commerce has revolutionized the way people conduct transactions, transforming how individuals buy and sell goods and services. Online shopping offers unparalleled convenience, a wider selection of products, and often more competitive prices compared to traditional brick-and-mortar stores. This digital marketplace has also created unprecedented opportunities for businesses to expand their reach and access global markets, fostering economic growth and innovation.""",
            "question": "Which TWO of the following are mentioned in the text about e-commerce?",
            "options": [
                "It has limited the way people buy goods.",
                "Online shopping offers convenience.",
                "It provides a narrower selection.",
                "It has created new opportunities for businesses.",
                "It offers competitive prices."
            ],
            "answers": {
                "1": "B",
                "2": "D"
            }
        }
    ]
    
    with app.app_context():
        # Remove existing Multiple Choice tests (section 1)
        PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general',
            section=1
        ).delete()
        db.session.commit()
        
        # Add each test set
        for i, test_set in enumerate(test_sets, 1):
            # Format the questions
            questions = []
            for j, option in enumerate(test_set["options"]):
                option_letter = chr(65 + j)  # A, B, C, D, E
                questions.append(f"Option {option_letter}: {option}")
            
            test = PracticeTest(
                title=f"General Training Reading: Multiple Choice {i}",
                description=f"Part 1: {test_set['title']}. {test_set['question']}",
                test_type="reading",
                ielts_test_type="general",
                section=1,  # Section 1 is for Multiple Choice
                _content=test_set["passage"],
                _questions=json.dumps([f"Question {q+1}: {questions[q]}" for q in range(len(questions))]),
                _answers=json.dumps(test_set["answers"])
            )
            db.session.add(test)
            print(f"Added authentic Multiple Choice test {i}: {test_set['title']}")
        
        db.session.commit()
        print(f"Successfully added {len(test_sets)} authentic Multiple Choice tests.")

if __name__ == "__main__":
    add_authentic_multiple_choice()