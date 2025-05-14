"""
Add General Training Reading Multiple Choice tests to the IELTS preparation app.
This script adds 16 different multiple choice tests based on the content provided.
"""
import json
from app import app, db
from models import PracticeTest

def add_general_reading_multiple_choice_tests():
    """Add General Training Reading Multiple Choice tests."""
    
    # Define the 16 sets of Multiple Choice questions and answers
    test_sets = [
        {
            "title": "For Sale - Used Cars",
            "passage": """
A: Reliable Sedan - 2018 model, low mileage, excellent condition.
• Power windows and locks
• Air conditioning
• Regularly maintained
• Asking $12,500

B: Spacious SUV - 2020 model, seats 7, all-wheel drive.
• Leather seats
• Sunroof
• Navigation system
• Asking $28,000

C: Fuel-Efficient Hatchback - 2022 model, great for city driving.
• Hybrid engine
• Backup camera
• Bluetooth connectivity
• Asking $16,000

D: Sporty Coupe - 2019 model, powerful engine, sleek design.
• Premium sound system
• Alloy wheels
• Low profile tires
• Asking $21,000

E: Durable Truck - 2017 model, heavy-duty, tow package.
• Crew cab
• Bed liner
• Four-wheel drive
• Asking $25,000

F: Compact Car - 2021 model, easy to park, economical.
• Manual transmission
• Good fuel economy
• Basic features
• Asking $11,000
            """,
            "questions": [
                "This vehicle has a feature to help with parking.",
                "This vehicle has been well taken care of.",
                "This vehicle can carry a large number of passengers.",
                "This vehicle is designed for off-road conditions.",
                "This vehicle has an upgraded audio system.",
                "This vehicle is relatively new and environmentally friendly."
            ],
            "answers": {
                "1": "C",
                "2": "A",
                "3": "B",
                "4": "E",
                "5": "D",
                "6": "C"
            }
        },
        {
            "title": "For Sale - Vacation Packages",
            "passage": """
A: Tropical Getaway - 7 nights in Maui, beachfront hotel.
• Daily breakfast included
• Sunset cruise
• Optional snorkeling excursion
• Price: $1800 per person

B: European Adventure - 10-day tour of Italy (Rome, Florence, Venice).
• Guided tours of major attractions
• Hotel accommodation
• Some meals included
• Price: $2500 per person

C: Mountain Retreat - 5 nights in Banff, cozy cabin stay.
• Hiking trails nearby
• Fireplace in cabin
• Optional ski passes
• Price: $1200 per person

D: City Break - 4 nights in New York City, central hotel.
• Tickets to a Broadway show
• Museum passes
• Hop-on hop-off bus tour
• Price: $1500 per person

E: Relaxing Cruise - 7-night Caribbean cruise, various islands.
• All-inclusive meals and drinks
• Onboard entertainment
• Shore excursions available
• Price: $1100 per person

F: Adventure Trip - 6 days in Costa Rica, rainforest exploration.
• Ziplining and rafting
• Eco-lodge accommodation
• Guided nature walks
• Price: $1900 per person
            """,
            "questions": [
                "This package includes transportation between different locations.",
                "This package offers the chance to see a live performance.",
                "This package is ideal for someone who enjoys being active outdoors.",
                "This package includes all your food and beverages.",
                "This package offers the opportunity to experience marine life.",
                "This package involves staying in a rustic type of accommodation."
            ],
            "answers": {
                "1": "B",
                "2": "D",
                "3": "F",
                "4": "E",
                "5": "A",
                "6": "C"
            }
        },
        {
            "title": "For Sale - Electronic Devices",
            "passage": """
A: High-Performance Laptop - Latest processor, large storage.
• 15-inch screen
• Long battery life
• Dedicated graphics card
• Price: $1200

B: Versatile Tablet - Lightweight, portable, multi-touch screen.
• 10-inch display
• Front and rear cameras
• Expandable storage
• Price: $400

C: Smartwatch - Tracks fitness, receives notifications.
• Heart rate monitor
• Water-resistant
• Multiple watch faces
• Price: $250

D: Wireless Headphones - Noise-canceling, comfortable fit.
• Bluetooth connectivity
• Built-in microphone
• Long playtime
• Price: $300

E: Digital Camera - High resolution, optical zoom.
• 4K video recording
• Image stabilization
• Compact design
• Price: $700

F: E-reader - Paper-like display, stores thousands of books.
• Weeks of battery life
• Adjustable font size
• Built-in light
• Price: $150
            """,
            "questions": [
                "This device is specifically designed for reading.",
                "This device is suitable for gaming or graphic-intensive tasks.",
                "This device can be used to take photos and videos.",
                "This device helps monitor your physical activity.",
                "This device allows for hands-free communication.",
                "This device has a screen that responds to touch."
            ],
            "answers": {
                "1": "F",
                "2": "A",
                "3": "E",
                "4": "C",
                "5": "D",
                "6": "B"
            }
        },
        {
            "title": "For Sale - Furniture Items",
            "passage": """
A: Comfortable Sofa - Seats three, soft fabric upholstery.
• Includes throw pillows
• Sturdy wooden frame
• Neutral color
• Price: $800

B: Elegant Dining Table - Seats six, solid wood.
• Includes four matching chairs
• Extendable leaf
• Classic design
• Price: $1200

C: Spacious Wardrobe - Two doors, hanging rod and shelves.
• Full-length mirror
• Ample storage space
• Easy to assemble
• Price: $500

D: Adjustable Office Chair - Ergonomic design, lumbar support.
• Swivel base with wheels
• Breathable mesh back
• Adjustable height
• Price: $350

E: Modern Coffee Table - Glass top, metal legs.
• Lower shelf for storage
• Sleek appearance
• Easy to clean
• Price: $200

F: Cozy Bed Frame - Queen size, upholstered headboard.
• Slatted base for mattress support
• Stylish design
• Requires assembly
• Price: $600 (mattress not included)
            """,
            "questions": [
                "This item is designed to help with posture while working.",
                "This item is made primarily of wood.",
                "This item includes reflective glass.",
                "This item provides a place to hang clothes.",
                "This item comes with extra cushions.",
                "This item has a surface that is easy to wipe clean."
            ],
            "answers": {
                "1": "D",
                "2": "B",
                "3": "C",
                "4": "C",
                "5": "A",
                "6": "E"
            }
        },
        {
            "title": "For Sale - Musical Instruments",
            "passage": """
A: Acoustic Guitar - Six-string, dreadnought body.
• Spruce top
• Mahogany back and sides
• Warm tone
• Price: $400

B: Digital Piano - 88 weighted keys, multiple voices.
• Built-in speakers
• Headphone jack
• Sustain pedal included
• Price: $750

C: Electric Drum Kit - Multiple pads and cymbals.
• Adjustable sensitivity
• Headphone output
• Compact for storage
• Price: $600

D: Tenor Saxophone - Brass body, lacquered finish.
• Includes mouthpiece and case
• Suitable for intermediate players
• Rich sound
• Price: $900

E: Ukulele - Soprano size, four nylon strings.
• Lightweight and portable
• Easy to learn
• Bright tone
• Price: $80

F: Violin - Full size, spruce top, maple back and sides.
• Includes bow and case
• Requires rosin (not included)
• Classical instrument
• Price: $500
            """,
            "questions": [
                "This instrument is known for its portability and ease of learning.",
                "This instrument does not require external amplification to be heard.",
                "This instrument allows for silent practice.",
                "This instrument is typically played with a bow.",
                "This instrument has keys that respond to the pressure applied.",
                "This instrument is made of metal and produces a sound through breath."
            ],
            "answers": {
                "1": "E",
                "2": "A",
                "3": "C",
                "4": "F",
                "5": "B",
                "6": "D"
            }
        },
        {
            "title": "For Sale - Plants",
            "passage": """
A: Peace Lily - Low maintenance, air-purifying.
• Prefers indirect light
• Water when soil is dry
• White flowers
• Price: $20

B: Snake Plant - Very hardy, tolerates neglect.
• Can grow in low light
• Water sparingly
• Upright, sword-like leaves
• Price: $15

C: Orchid - Elegant blooms, various colors.
• Requires specific watering
• Bright, indirect light
• Long-lasting flowers
• Price: $30

D: Succulent Assortment - Variety of small, drought-tolerant plants.
• Needs plenty of sunlight
• Water infrequently
• Unique shapes and textures
• Price: $25 (set of 3)

E: Fern - Lush, green foliage, thrives in humidity.
• Prefers shade or low light
• Keep soil consistently moist
• Delicate fronds
• Price: $18

F: Cactus - Desert plant, requires minimal watering.
• Needs direct sunlight
• Handle with care (spines)
• Unique shapes and sizes
• Price: $12
            """,
            "questions": [
                "This plant is known for its ability to clean the air.",
                "This plant is well-suited for someone who often forgets to water.",
                "This plant is characterized by its soft, leafy growth.",
                "This plant typically has colorful, showy flowers.",
                "This plant is often sold as a collection of different types.",
                "This plant has sharp, protective features."
            ],
            "answers": {
                "1": "A",
                "2": "B",
                "3": "E",
                "4": "C",
                "5": "D",
                "6": "F"
            }
        },
        {
            "title": "For Sale - Pet Supplies",
            "passage": """
A: Dog Bed - Orthopedic foam, washable cover.
• Available in multiple sizes
• Provides joint support
• Comfortable for older dogs
• Price: $60

B: Cat Tree - Multiple levels, scratching posts.
• Provides climbing and resting spots
• Encourages exercise
• Saves furniture from scratching
• Price: $80

C: Fish Tank Kit - Includes tank, filter, and heater.
• Suitable for small fish
• Easy to set up
• Decorative gravel included
• Price: $50

D: Bird Cage - Large, with perches and food bowls.
• Suitable for parakeets or finches
• Easy to clean
• Secure latch
• Price: $70

E: Rabbit Hutch - Indoor/outdoor use, two tiers.
• Provides shelter and exercise area
• Easy access for cleaning
• Durable construction
• Price: $100

F: Hamster Cage - Includes wheel, water bottle, and food dish.
• Ventilated design
• Interactive tunnels
• Compact size
• Price: $40
            """,
            "questions": [
                "This item is designed to prevent damage to your home.",
                "This item is suitable for an animal that enjoys climbing.",
                "This item is designed to support an animal's joints.",
                "This item includes equipment for maintaining water quality.",
                "This item is designed for an animal that likes to burrow or hide.",
                "This item can be used both inside and outside."
            ],
            "answers": {
                "1": "B",
                "2": "B",
                "3": "A",
                "4": "C",
                "5": "F",
                "6": "E"
            }
        },
        {
            "title": "For Sale - Clothing Items",
            "passage": """
A: Winter Coat - Down-filled, waterproof.
• Hooded for extra warmth
• Multiple pockets
• Available in various colors
• Price: $150

B: Summer Dress - Lightweight fabric, floral print.
• Comfortable for warm weather
• Various sizes available
• Easy to care for
• Price: $40

C: Leather Boots - Durable, ankle-high.
• Good for all seasons
• Comfortable for walking
• Available in different sizes
• Price: $120

D: Cotton T-Shirt - Short-sleeved, plain color.
• Soft and breathable
• Multiple sizes available
• Basic wardrobe staple
• Price: $20

E: Wool Sweater - Warm and cozy, long sleeves.
• Ideal for cold weather
• Hand-wash recommended
• Various styles
• Price: $70

F: Denim Jeans - Classic style, straight leg.
• Durable fabric
• Various washes available
• Multiple waist and length sizes
• Price: $60
            """,
            "questions": [
                "This item is best suited for hot weather.",
                "This item is made from animal skin.",
                "This item is designed to keep you very warm.",
                "This item is a basic and versatile piece of clothing.",
                "This item is recommended to be cleaned by hand.",
                "This item has extra protection for the head."
            ],
            "answers": {
                "1": "B",
                "2": "C",
                "3": "A",
                "4": "D",
                "5": "E",
                "6": "A"
            }
        },
        {
            "title": "For Sale - Books",
            "passage": """
A: Mystery Novel - Thrilling plot, unexpected twists.
• Paperback edition
• Best-selling author
• Suitable for adults
• Price: $10

B: Science Fiction Epic - Interstellar adventure, complex world-building.
• Hardcover edition
• Award-winning series
• For mature readers
• Price: $25

C: Cookbook - Over 100 recipes, full-color photos.
• Includes vegetarian options
• Easy-to-follow instructions
• Spiral-bound for convenience
• Price: $20

D: Children's Storybook - Colorful illustrations, simple text.
• Ideal for ages 3-7
• Teaches a valuable lesson
• Durable board book
• Price: $8

E: Biography - Inspiring life story, historical context.
• Paperback edition
• Critically acclaimed
• Includes photographs
• Price: $15

F: Self-Help Guide - Practical advice, personal development.
• Workbook format
• Actionable steps
• Focuses on mindfulness
• Price: $18
            """,
            "questions": [
                "This book is designed to be easy for young children to handle.",
                "This book contains visual aids to enhance the content.",
                "This book focuses on improving oneself.",
                "This book is part of a larger series.",
                "This book is designed to keep the pages open easily.",
                "This book is known for its surprising events."
            ],
            "answers": {
                "1": "D",
                "2": "C",
                "3": "F",
                "4": "B",
                "5": "C",
                "6": "A"
            }
        },
        {
            "title": "For Sale - Outdoor Gear",
            "passage": """
A: Camping Tent - Sleeps 4, waterproof, easy setup.
• Lightweight and portable
• Includes carrying bag
• Good ventilation
• Price: $150

B: Hiking Boots - Durable leather, ankle support.
• Waterproof membrane
• Good traction
• Comfortable for long treks
• Price: $120

C: Backpack - Large capacity, multiple compartments.
• Adjustable straps
• Hydration compatible
• Durable material
• Price: $80

D: Sleeping Bag - Suitable for cold weather, compact when packed.
• Lightweight insulation
• Includes compression sack
• Mummy shape
• Price: $90

E: Portable Grill - Lightweight, propane-powered.
• Foldable legs
• Easy to clean
• Ideal for picnics
• Price: $60

F: Binoculars - High magnification, durable construction.
• Waterproof and fog-proof
• Good for birdwatching
• Includes carrying case
• Price: $100
            """,
            "questions": [
                "This item is designed to keep you warm while sleeping outdoors.",
                "This item is useful for carrying supplies on long walks.",
                "This item is designed to be easily transported and set up for cooking outdoors.",
                "This item helps you see distant objects more clearly.",
                "This item is designed to protect your feet and ankles during outdoor activities.",
                "This item is designed to provide shelter from the elements."
            ],
            "answers": {
                "1": "D",
                "2": "C",
                "3": "E",
                "4": "F",
                "5": "B",
                "6": "A"
            }
        },
        {
            "title": "For Sale - Kitchen Appliances",
            "passage": """
A: Blender - High-speed, multiple settings.
• Ideal for smoothies and soups
• Easy to clean
• Durable blades
• Price: $80

B: Toaster Oven - Bakes, broils, and toasts.
• Compact size
• Multiple rack positions
• Timer function
• Price: $70

C: Coffee Maker - Programmable, brews up to 12 cups.
• Keep-warm function
• Automatic shut-off
• Easy to use
• Price: $50

D: Food Processor - Chops, slices, and shreds.
• Multiple attachments included
• Large capacity bowl
• Powerful motor
• Price: $120

E: Electric Kettle - Rapid boil, cordless pouring.
• Automatic shut-off
• Water level indicator
• Energy efficient
• Price: $40

F: Slow Cooker - Programmable timer, multiple heat settings.
• Removable ceramic pot
• Glass lid
• Recipe book included
• Price: $60
            """,
            "questions": [
                "This appliance is designed to heat water quickly.",
                "This appliance can cook food over a long period of time at a low temperature.",
                "This appliance is versatile and can be used for cooking, reheating, or browning food.",
                "This appliance can cut ingredients into different shapes.",
                "This appliance is primarily used for making beverages.",
                "This appliance can break down solid foods into liquid form."
            ],
            "answers": {
                "1": "E",
                "2": "F",
                "3": "B",
                "4": "D",
                "5": "C",
                "6": "A"
            }
        },
        {
            "title": "For Sale - Health and Wellness Products",
            "passage": """
A: Fitness Tracker - Monitors steps, heart rate, and sleep.
• Water-resistant
• Smartphone notifications
• Week-long battery life
• Price: $100

B: Yoga Mat - Non-slip surface, eco-friendly material.
• Extra thick padding
• Carrying strap included
• Easy to clean
• Price: $40

C: Essential Oil Diffuser - Ultrasonic, multiple light settings.
• Automatic shut-off
• Quiet operation
• Covers medium-sized rooms
• Price: $35

D: Massage Pillow - Heat function, rotating nodes.
• Portable design
• Multiple speed settings
• Can be used on different body parts
• Price: $70

E: Air Purifier - HEPA filter, removes allergens and odors.
• Quiet operation
• Filter replacement indicator
• Multiple fan speeds
• Price: $150

F: Meditation Cushion - Ergonomic design, comfortable fabric.
• Promotes proper posture
• Removable cover for washing
• Filled with natural materials
• Price: $45
            """,
            "questions": [
                "This product provides data about your physical activity and health.",
                "This product helps relieve muscle tension.",
                "This product is designed to improve air quality.",
                "This product helps with relaxation through aromatherapy.",
                "This product is specifically designed for comfortable seated meditation.",
                "This product provides a cushioned surface for exercise."
            ],
            "answers": {
                "1": "A",
                "2": "D",
                "3": "E",
                "4": "C",
                "5": "F",
                "6": "B"
            }
        },
        {
            "title": "For Sale - Home Décor Items",
            "passage": """
A: Decorative Throw Pillows - Set of 2, various patterns.
• Soft fabric cover
• Removable for washing
• Adds color and texture
• Price: $30

B: Wall Art - Abstract canvas print, ready to hang.
• Modern design
• Large size (24"x36")
• Professionally framed
• Price: $120

C: Table Lamp - Ceramic base, fabric shade.
• Warm light
• 3-way switch
• Compact size
• Price: $65

D: Area Rug - Geometric pattern, soft texture.
• Durable material
• Non-slip backing
• Various sizes available
• Price: $90

E: Artificial Plants - Set of 3, realistic appearance.
• No watering needed
• Modern decorative pots
• Suitable for any room
• Price: $45

F: Wall Clock - Minimalist design, silent mechanism.
• Battery operated
• Easy to read
• Sleek appearance
• Price: $40
            """,
            "questions": [
                "This item provides illumination for a room.",
                "This item covers and protects flooring.",
                "This item tells you the current time.",
                "This item enhances wall space with color and design.",
                "This item requires no maintenance but looks like a living thing.",
                "This item adds comfort and color to furniture."
            ],
            "answers": {
                "1": "C",
                "2": "D",
                "3": "F",
                "4": "B",
                "5": "E",
                "6": "A"
            }
        },
        {
            "title": "For Sale - Travel Accessories",
            "passage": """
A: Travel Pillow - Memory foam, ergonomic design.
• Supports neck during travel
• Washable cover
• Compact when folded
• Price: $25

B: Luggage Set - Hard shell, spinner wheels, 3 pieces.
• Various sizes for different trips
• Built-in TSA locks
• Expandable capacity
• Price: $200

C: Universal Travel Adapter - Works in 150+ countries.
• Multiple USB ports
• Compact design
• Surge protection
• Price: $30

D: Toiletry Bag - Water-resistant, hanging design.
• Multiple compartments
• Transparent pockets
• Carry handle
• Price: $35

E: Packing Cubes - Set of 6, different sizes.
• Keeps luggage organized
• Mesh top for visibility
• Lightweight material
• Price: $40

F: Digital Luggage Scale - Accurate to 0.1 lbs.
• Compact size
• Easy-to-read display
• Long battery life
• Price: $15
            """,
            "questions": [
                "This item helps you avoid overweight baggage fees.",
                "This item helps keep your belongings sorted inside your suitcase.",
                "This item enables you to use electronic devices in foreign countries.",
                "This item provides comfort during long flights or car trips.",
                "This item helps transport and protect your personal care items.",
                "This item is a set of containers for transporting your clothes and belongings."
            ],
            "answers": {
                "1": "F",
                "2": "E",
                "3": "C",
                "4": "A",
                "5": "D",
                "6": "B"
            }
        },
        {
            "title": "For Sale - Sports Equipment",
            "passage": """
A: Tennis Racket - Lightweight frame, balanced weight.
• Includes protective cover
• Pre-strung
• Suitable for beginners to intermediates
• Price: $70

B: Yoga Block Set - High-density foam, set of 2.
• Provides stability and support
• Helps with proper alignment
• Lightweight and durable
• Price: $25

C: Basketball - Official size and weight.
• Good grip
• Suitable for indoor or outdoor use
• Durable construction
• Price: $30

D: Exercise Mat - Extra thick, non-slip surface.
• Cushions body during workouts
• Easy to clean
• Includes carrying strap
• Price: $40

E: Dumbbells - Set of 2, vinyl coated, 5 lbs each.
• Comfortable grip
• Won't damage floors
• Ideal for various exercises
• Price: $35

F: Jump Rope - Adjustable length, ball bearing handles.
• Smooth rotation
• Lightweight
• Portable workout tool
• Price: $15
            """,
            "questions": [
                "This item is useful for strength training.",
                "This item is designed for cardiovascular exercise.",
                "This item provides cushioning during floor exercises.",
                "This item is used in a racquet sport.",
                "This item can be used for support during stretching and poses.",
                "This item is spherical and used in a team sport."
            ],
            "answers": {
                "1": "E",
                "2": "F",
                "3": "D",
                "4": "A",
                "5": "B",
                "6": "C"
            }
        },
        {
            "title": "For Sale - Office Supplies",
            "passage": """
A: Desk Organizer - Multiple compartments, mesh design.
• Holds pens, paper clips, and notes
• Sturdy construction
• Space-saving design
• Price: $25

B: Wireless Mouse - Ergonomic design, silent clicks.
• Long battery life
• Adjustable DPI settings
• Compatible with multiple devices
• Price: $35

C: Notebook Set - Hardcover, ruled pages, set of 3.
• Acid-free paper
• Bookmark ribbon
• Elastic closure
• Price: $20

D: Desk Lamp - Adjustable arm, multiple brightness levels.
• USB charging port
• Touch controls
• Modern design
• Price: $45

E: Whiteboard - Magnetic surface, aluminum frame.
• Includes markers and eraser
• Easy wall mounting
• Dry-erase surface
• Price: $30

F: Label Maker - Portable, thermal printing.
• Various font styles and sizes
• No ink required
• QWERTY keyboard
• Price: $40
            """,
            "questions": [
                "This item helps keep desk items in their proper place.",
                "This item allows you to create customized adhesive tags.",
                "This item provides illumination for your workspace.",
                "This item allows you to write and display information that can be easily changed.",
                "This item helps you navigate a computer screen without using a touchpad.",
                "This item provides bound paper for writing notes or information."
            ],
            "answers": {
                "1": "A",
                "2": "F",
                "3": "D",
                "4": "E",
                "5": "B",
                "6": "C"
            }
        }
    ]
    
    # Add each test to the database
    with app.app_context():
        # Remove existing tests first to avoid duplicates
        PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general',
            section=1  # Section 1 is for Multiple Choice
        ).delete()
        db.session.commit()
        
        # Add each test set
        for i, test_set in enumerate(test_sets, 1):
            test = PracticeTest(
                title=f"General Training Reading: Multiple Choice {i}",
                description=f"Part 1: {test_set['title']}. Look at the six items (A-F) and answer questions 1-6 based on the information provided.",
                test_type="reading",
                ielts_test_type="general",
                section=1,  # Section 1 is for Multiple Choice
                _content=test_set["passage"],
                _questions=json.dumps([f"Question {j+1}: {q}" for j, q in enumerate(test_set["questions"])]),
                _answers=json.dumps(test_set["answers"])
            )
            db.session.add(test)
            print(f"Added General Training Reading: Multiple Choice {i}")
        
        db.session.commit()
        print(f"Successfully added {len(test_sets)} General Training Reading Multiple Choice tests.")

if __name__ == "__main__":
    add_general_reading_multiple_choice_tests()