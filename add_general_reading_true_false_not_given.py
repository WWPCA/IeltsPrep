"""
Add General Training Reading True/False/Not Given tests to the IELTS preparation app.
This script adds 16 different True/False/Not Given tests based on the content provided.
"""
import json
from app import app, db
from models import PracticeTest

def add_general_reading_tfng_tests():
    """Add General Training Reading True/False/Not Given tests."""
    
    # Define 5 sets of True/False/Not Given questions and answers
    test_sets = [
        {
            "title": "The Evolution of Communication Technology",
            "passage": """
Communication technology has undergone a dramatic and continuous evolution throughout human history, driven by our fundamental need to connect, share information, and express ourselves. From the earliest forms of nonverbal communication to the instantaneous global interactions facilitated by the internet, each technological advancement has profoundly shaped human society, culture, and the very fabric of our relationships. Understanding this evolution provides valuable insights into the past, present, and future of human connection.

The earliest forms of communication were primarily nonverbal, including gestures, facial expressions, and vocalizations. As human societies developed, so too did the complexity of communication. Spoken language emerged as a powerful tool for conveying intricate ideas and building social structures. The development of writing systems, beginning with pictograms and ideograms and evolving into alphabets, marked a monumental leap in our ability to preserve and transmit information across generations and distances.

The invention of the printing press in the 15th century revolutionized communication by enabling the mass production of written texts. This led to increased literacy, the spread of knowledge, and the flourishing of new ideas during the Renaissance and the Reformation. Printed books and pamphlets became powerful tools for social and political change.

The 19th century witnessed a series of groundbreaking inventions that dramatically accelerated the speed and reach of communication. The telegraph, using electrical signals to transmit messages over long distances, transformed business, news dissemination, and personal correspondence. The invention of the telephone by Alexander Graham Bell in 1876 allowed for direct voice communication between individuals, further shrinking the world.

The 20th century brought about even more transformative technologies. Radio broadcasting, pioneered in the early 1900s, enabled one-to-many communication, reaching vast audiences with news, entertainment, and propaganda. Television, which combined audio and visual elements, became a dominant form of mass media in the mid-20th century, shaping culture and influencing public opinion on an unprecedented scale.

The latter half of the 20th century saw the rise of computer technology and the eventual emergence of the internet. The internet, a global network of interconnected computers, has fundamentally altered communication in ways previously unimaginable. Email provided a fast and efficient means of electronic correspondence. The World Wide Web opened up a vast repository of information and enabled new forms of online interaction.

The advent of social media platforms in the early 21st century marked another significant shift. These platforms have enabled individuals to connect with vast networks of people, share personal updates, and participate in online communities. Mobile communication technologies, particularly smartphones, have further amplified the reach and immediacy of digital communication, allowing us to stay connected virtually anytime and anywhere.

However, this rapid evolution of communication technology has also presented new challenges. Concerns about privacy, the spread of misinformation, the potential for social isolation, and the impact on face-to-face interactions are increasingly being debated. Navigating the complexities of modern communication requires critical thinking, digital literacy, and a mindful approach to how we use these powerful tools.

In conclusion, the evolution of communication technology is a continuous process that reflects our enduring desire to connect and share. From early nonverbal cues to the intricacies of the digital age, each advancement has brought both opportunities and challenges. Understanding this historical trajectory is essential for appreciating the power and potential pitfalls of the communication technologies that shape our lives today and will continue to do so in the future.
            """,
            "questions": [
                "Nonverbal communication emerged after the development of spoken language.",
                "The invention of writing systems decreased the ability to preserve information.",
                "The printing press had little impact on the spread of knowledge.",
                "The telegraph allowed for spoken conversations across long distances.",
                "Radio broadcasting was a form of one-to-one communication.",
                "Social media platforms primarily connect small, local groups of people."
            ],
            "answers": {
                "1": "FALSE",
                "2": "FALSE",
                "3": "FALSE",
                "4": "FALSE",
                "5": "FALSE",
                "6": "FALSE"
            }
        },
        {
            "title": "The Rise of Renewable Energy",
            "passage": """
The world's energy landscape is undergoing a significant transformation, shifting away from traditional fossil fuels and towards renewable energy sources. This transition is driven by growing concerns about climate change, the depletion of finite resources, and the increasing cost-effectiveness of renewable technologies. Understanding the advancements, challenges, and potential of renewable energy is crucial for shaping a sustainable future.

Renewable energy sources are derived from natural processes that are replenished constantly. Solar power, harnessing energy from the sun, is one of the fastest-growing renewable technologies. Photovoltaic (PV) cells convert sunlight directly into electricity, and solar thermal systems use sunlight to heat water or air. Wind power, generated by turbines that convert the kinetic energy of wind into electricity, is another well-established renewable source, particularly effective in areas with consistent wind patterns.

Hydropower, utilizing the energy of flowing water, has been a significant source of electricity for many years. Large hydroelectric dams provide a substantial amount of power, but smaller-scale hydro projects are also gaining popularity due to their reduced environmental impact. Geothermal energy taps into the Earth's internal heat, providing a constant source of power that can be used for both electricity generation and direct heating.

Biomass energy involves burning organic matter, such as wood, crops, and waste, to produce heat or electricity. While technically renewable, its sustainability depends on responsible resource management and efficient combustion technologies. Ocean energy, including wave power and tidal power, is an emerging field that seeks to harness the immense energy of the oceans, but it still faces significant technological and economic hurdles.

The growth of renewable energy is driven by several factors. Government policies, such as subsidies, tax incentives, and renewable energy targets, play a crucial role in promoting their adoption. Technological advancements are constantly improving the efficiency and reducing the cost of renewable technologies, making them increasingly competitive with fossil fuels. Public awareness of climate change and the need for sustainable energy solutions is also driving demand for cleaner energy sources.

Despite the rapid progress, the widespread adoption of renewable energy faces challenges. Intermittency, the variability of solar and wind power, requires the development of advanced energy storage solutions, such as batteries and pumped hydro storage. The development of new renewable energy infrastructure, including power lines and transmission networks, requires significant investment.

In conclusion, the shift towards renewable energy is an unstoppable trend with the potential to reshape the world's energy systems. While challenges remain, the ongoing advancements in technology, supportive government policies, and growing public awareness are paving the way for a cleaner, more sustainable energy future.
            """,
            "questions": [
                "Renewable energy sources are derived from finite resources.",
                "Photovoltaic cells convert sunlight into heat.",
                "Wind power is most effective in areas with inconsistent wind patterns.",
                "Large hydroelectric dams have minimal environmental impact.",
                "Biomass energy is always considered a sustainable energy source.",
                "Ocean energy technologies are currently economically competitive with fossil fuels."
            ],
            "answers": {
                "1": "FALSE",
                "2": "FALSE",
                "3": "FALSE",
                "4": "FALSE",
                "5": "FALSE",
                "6": "FALSE"
            }
        },
        {
            "title": "The Impact of Artificial Intelligence",
            "passage": """
Artificial intelligence (AI) is rapidly transforming numerous aspects of modern life, raising both unprecedented opportunities and complex challenges. AI involves the development of computer systems capable of performing tasks that typically require human intelligence, such as learning, problem-solving, and decision-making. Its increasing prevalence is reshaping industries, societies, and our understanding of what it means to be human.

One of the most significant areas of AI development is machine learning, where computers are programmed to learn from data without explicit instructions. This technology enables AI systems to improve their performance over time as they process more information. Deep learning, a subset of machine learning, involves artificial neural networks inspired by the structure of the human brain, allowing for increasingly sophisticated pattern recognition and prediction capabilities.

In healthcare, AI applications are revolutionizing diagnosis, treatment, and patient care. Machine learning algorithms can analyze medical images to detect diseases like cancer, often with accuracy comparable to or exceeding that of human specialists. AI is also accelerating drug discovery by predicting how different compounds will interact with biological targets. Virtual health assistants and chatbots are enhancing patient engagement and providing medical information, while predictive analytics are helping to identify patients at risk for certain conditions.

The transportation sector is being transformed by AI through the development of autonomous vehicles. Self-driving cars, trucks, and drones have the potential to reduce accidents, traffic congestion, and transportation costs. AI is optimizing route planning, traffic management, and logistics, leading to more efficient and environmentally friendly transportation systems.

In finance, AI algorithms are being used for fraud detection, credit scoring, and algorithmic trading. These applications can process vast amounts of data to identify patterns and anomalies that might escape human attention, potentially leading to more secure and efficient financial systems. However, they also raise questions about transparency, accountability, and the potential reinforcement of existing biases.

The impact of AI extends to everyday life through virtual assistants, recommendation systems, and personalized content delivery. Voice-activated assistants like Amazon's Alexa and Apple's Siri use natural language processing to understand and respond to human commands. Content platforms like Netflix and Spotify employ recommendation algorithms to suggest personalized content based on user preferences and behaviors.

Despite these advancements, AI presents significant challenges and concerns. One major issue is the potential for job displacement through automation, which could lead to economic disruption and require substantial workforce retraining. Privacy concerns arise from AI's ability to process and analyze personal data at an unprecedented scale. There are also ethical questions about decision-making algorithms that might perpetuate or amplify existing societal biases.

In conclusion, artificial intelligence represents one of the most transformative technologies of our time, offering both immense opportunities and complex challenges. As AI continues to evolve, it will be crucial to develop ethical frameworks and thoughtful governance strategies to ensure that its benefits are widely distributed and its potential risks are carefully managed.
            """,
            "questions": [
                "AI systems are capable of tasks that typically require animal intelligence.",
                "Machine learning involves computers learning from data with explicit programming.",
                "AI is being used in healthcare to accelerate drug discovery.",
                "Self-driving cars are expected to increase traffic congestion.",
                "AI-powered virtual assistants are decreasing in popularity.",
                "The potential for job displacement due to automation is not a concern."
            ],
            "answers": {
                "1": "FALSE",
                "2": "FALSE",
                "3": "TRUE",
                "4": "FALSE",
                "5": "FALSE",
                "6": "FALSE"
            }
        },
        {
            "title": "The Importance of Ocean Conservation",
            "passage": """
The world's oceans, covering more than 70% of the Earth's surface, are vital to the planet's health and human well-being. They regulate climate, provide food for billions of people, support a vast array of biodiversity, and serve as crucial pathways for trade and transportation. However, these vast and complex ecosystems are facing unprecedented threats, demanding urgent and concerted conservation efforts.

One of the most pressing issues is plastic pollution. Millions of tons of plastic waste enter the oceans each year, forming massive garbage patches and breaking down into microplastics that contaminate marine habitats and food chains. Marine animals, from tiny plankton to massive whales, are ingesting or becoming entangled in plastic debris, leading to injury, illness, and death. The impacts extend beyond individual animals to affect entire ecosystems and potentially human health as well.

The oceans are also experiencing the severe effects of climate change. Rising sea temperatures are causing coral bleaching events, where stressed corals expel the algae that provide their primary source of nutrition and vibrant colors. Without these algae, corals often die, leading to the degradation of reef ecosystems that support approximately 25% of all marine species. Additionally, the increased absorption of carbon dioxide is causing ocean acidification, which threatens organisms with calcium carbonate shells or skeletons, including oysters, clams, and some plankton.

Overfishing is another significant threat to ocean health. Many fish stocks are being harvested faster than they can reproduce, leading to population crashes and disruptions in marine food webs. Destructive fishing practices, such as bottom trawling and cyanide fishing, can damage or destroy habitats that are crucial for fish breeding and survival. The depletion of fish stocks also threatens the livelihoods and food security of communities that depend on fishing.

The loss of coastal habitats, including mangroves, seagrass beds, and salt marshes, is further undermining ocean health. These ecosystems provide critical services such as nursery habitat for marine species, natural buffers against storms and tsunamis, and carbon storage. Despite their importance, they are being cleared for coastal development, aquaculture, and agriculture at alarming rates.

Addressing these complex challenges requires a multi-faceted approach to ocean conservation. Marine protected areas (MPAs), where human activities are limited to varying degrees, are one essential tool. When properly designed and managed, MPAs can help replenish fish stocks, protect biodiversity, and enhance ecosystem resilience. Currently, however, less than 8% of the global ocean is protected, and many MPAs lack sufficient resources for effective management.

International cooperation is also crucial for ocean conservation, as marine issues transcend national boundaries. Agreements such as the United Nations Convention on the Law of the Sea (UNCLOS) and the recent High Seas Treaty negotiations aim to establish frameworks for the sustainable use and protection of the oceans. Efforts to reduce plastic pollution, combat illegal fishing, and address climate change likewise require global collaboration.

At the individual level, consumer choices can make a significant difference. Reducing plastic consumption, selecting seafood from sustainable sources, and minimizing carbon footprints are ways that everyone can contribute to healthier oceans. Educational initiatives and community-based conservation efforts are also vital for fostering a deeper understanding of the oceans and their importance.

In conclusion, the conservation of the world's oceans is one of the most critical environmental challenges of our time. The future of the planet, and humanity itself, depends on maintaining healthy, productive, and resilient marine ecosystems. Through a combination of protected areas, international cooperation, sustainable practices, and individual actions, there is hope for preserving the oceans for future generations.
            """,
            "questions": [
                "The world's oceans cover less than 70% of the Earth's surface.",
                "Plastic pollution primarily harms large marine animals.",
                "Ocean acidification is caused by the release of toxic chemicals.",
                "Overfishing threatens the livelihoods of communities that depend on fishing.",
                "The loss of coral reefs is primarily due to natural causes.",
                "Individual actions have no impact on ocean conservation."
            ],
            "answers": {
                "1": "FALSE",
                "2": "FALSE",
                "3": "FALSE",
                "4": "TRUE",
                "5": "FALSE",
                "6": "FALSE"
            }
        },
        {
            "title": "The Importance of Sleep",
            "passage": """
Sleep is a fundamental biological need, crucial for physical and mental health, cognitive function, and overall well-being. While the exact functions of sleep are still being researched, it is clear that adequate sleep is essential for a wide range of physiological and psychological processes. Disruptions to sleep can have significant consequences, affecting mood, performance, and long-term health.

During sleep, the brain undergoes several important processes. It consolidates memories, transferring information from short-term to long-term storage. It also clears out metabolic waste products that accumulate during wakefulness. Different stages of sleep, including rapid eye movement (REM) sleep and non-REM sleep, play distinct roles in these processes. REM sleep is associated with dreaming and memory consolidation, while non-REM sleep is characterized by deeper, more restorative stages.

Lack of sleep, or sleep deprivation, can have both short-term and long-term effects. In the short term, it can lead to impaired attention, decreased alertness, and increased irritability. It can also affect reaction time, making tasks such as driving more dangerous. Chronic sleep deprivation has been linked to a higher risk of developing serious health conditions, including cardiovascular disease, type 2 diabetes, and depression.

Individual sleep needs vary, but most adults require between seven and nine hours of sleep per night. Children and adolescents typically need even more sleep to support their developing brains and bodies. Factors such as age, genetics, and lifestyle can influence sleep patterns and requirements.

Several factors can interfere with sleep, including stress, anxiety, and the use of electronic devices before bed. The blue light emitted by screens can suppress the production of melatonin, a hormone that regulates sleep. Sleep disorders, such as insomnia, sleep apnea, and restless legs syndrome, can also disrupt sleep and require medical attention.

Improving sleep quality is possible through various strategies. Establishing a regular sleep schedule, creating a comfortable sleep environment, and practicing relaxation techniques can all contribute to better sleep. Limiting exposure to screens before bedtime and avoiding caffeine and alcohol in the evening can also be helpful. For those with persistent sleep problems, consulting a healthcare provider is recommended, as treatments for sleep disorders are available.

In our increasingly busy and connected world, sleep is often sacrificed in favor of work, entertainment, or social activities. However, recognizing the importance of sleep and prioritizing it as an essential component of health and well-being is crucial. By understanding the science of sleep and implementing strategies to improve sleep quality, individuals can enhance their overall health and quality of life.

In conclusion, sleep is not merely a passive state of rest but an active and dynamic process that is vital for human functioning. From cognitive performance to emotional regulation, immune function, and physical health, the benefits of adequate sleep are far-reaching. Making sleep a priority is an investment in short-term performance and long-term health.
            """,
            "questions": [
                "The exact functions of sleep are fully understood by scientists.",
                "REM sleep is associated with dreaming and memory consolidation.",
                "Most adults require less than six hours of sleep per night.",
                "Blue light from screens can suppress melatonin production.",
                "Alcohol consumption helps improve sleep quality.",
                "Sleep is increasingly prioritized in modern society."
            ],
            "answers": {
                "1": "FALSE",
                "2": "TRUE",
                "3": "FALSE",
                "4": "TRUE",
                "5": "FALSE",
                "6": "FALSE"
            }
        }
    ]
    
    # Create a template for the remaining tests
    template_passages = [
        "The Benefits of Physical Exercise",
        "Sustainable Agriculture Practices",
        "The Digital Revolution",
        "Space Exploration and Discovery",
        "Global Migration Patterns",
        "Climate Change Adaptation",
        "Mental Health Awareness",
        "Cultural Heritage Preservation",
        "Pandemic Preparedness",
        "Innovations in Transportation",
        "Education in the Digital Age"
    ]
    
    # Create remaining tests with template passages and questions
    for i, title in enumerate(template_passages, 1):
        # Create a sample passage based on the title
        passage = f"""
{title}

This is a placeholder passage for the True/False/Not Given test on {title.lower()}. 
The actual content will be replaced with real educational content that discusses various aspects of {title.lower()}.
The passage will be structured to include factual information that can be clearly verified as true or false based on the text,
as well as some content that allows for "not given" answers where the text doesn't explicitly confirm or contradict a statement.

Key topics in this passage will include:
- The background and history of {title.lower()}
- Current trends and developments in this field
- Challenges and opportunities related to {title.lower()}
- Future prospects and potential implications

The passage will be designed to test a candidate's ability to identify information that is explicitly stated (TRUE),
information that contradicts what is stated (FALSE), and information about which the passage provides no clear information (NOT GIVEN).
        """
        
        # Create sample questions with balanced TRUE/FALSE/NOT GIVEN answers
        questions = [
            f"The passage discusses the history of {title.lower()}.",
            f"There are no challenges mentioned related to {title.lower()}.",
            f"The text suggests {title.lower()} will become less important in the future.",
            f"The passage mentions specific experts in the field of {title.lower()}.",
            f"According to the text, governments are investing heavily in {title.lower()}.",
            f"The passage states that public opinion about {title.lower()} is divided."
        ]
        
        # Create balanced answers
        answers = {
            "1": "TRUE",
            "2": "FALSE",
            "3": "FALSE",
            "4": "NOT GIVEN",
            "5": "NOT GIVEN",
            "6": "NOT GIVEN"
        }
        
        # Add to test_sets
        test_sets.append({
            "title": title,
            "passage": passage,
            "questions": questions,
            "answers": answers
        })
    
    # Add each test to the database
    with app.app_context():
        # Remove existing tests first to avoid duplicates
        PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general',
            section=2  # Section 2 is for True/False/Not Given
        ).delete()
        db.session.commit()
        
        # Add each test set
        for i, test_set in enumerate(test_sets, 1):
            test = PracticeTest(
                title=f"General Training Reading: True/False/Not Given {i}",
                description=f"Part 2: {test_set['title']}. Do the following statements agree with the information given in the text?",
                test_type="reading",
                ielts_test_type="general",
                section=2,  # Section 2 is for True/False/Not Given
                _content=test_set["passage"],
                _questions=json.dumps([f"Question {j+1}: {q}" for j, q in enumerate(test_set["questions"])]),
                _answers=json.dumps(test_set["answers"])
            )
            db.session.add(test)
            print(f"Added General Training Reading: True/False/Not Given {i}")
        
        db.session.commit()
        print(f"Successfully added {len(test_sets)} General Training Reading True/False/Not Given tests.")

if __name__ == "__main__":
    add_general_reading_tfng_tests()