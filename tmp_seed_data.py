import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.db_service import db_service

sample_contacts = [
    {
        "name": "Alex Rivera",
        "email": "alex.rivera@techflow.io",
        "phone": "+1 (555) 123-4567",
        "company": "TechFlow Solutions",
        "interest": "High",
        "email2": json.dumps([{"label": "Work", "value": "arivera@techflow.io"}]),
        "social_media": json.dumps([{"label": "LinkedIn", "value": "linkedin.com/in/alexrivera"}])
    },
    {
        "name": "Sarah Chen",
        "email": "s.chen@nexus-ai.com",
        "phone": "+1 (555) 987-6543",
        "company": "Nexus AI",
        "interest": "Medium",
        "email2": "[]",
        "social_media": json.dumps([{"label": "Twitter", "value": "twitter.com/sarahchen_ai"}])
    },
    {
        "name": "Marcus Thorne",
        "email": "mthorne@vanguard-corp.com",
        "phone": "+44 20 7946 0123",
        "company": "Vanguard Corporation",
        "interest": "Low",
        "email2": "[]",
        "social_media": "[]"
    },
    {
        "name": "Elena Rodriguez",
        "email": "elena.r@swift-logistics.es",
        "phone": "+34 912 345 678",
        "company": "Swift Logistics",
        "interest": "Very High",
        "email2": json.dumps([{"label": "Personal", "value": "elena.rodriguez.dev@gmail.com"}]),
        "social_media": json.dumps([{"label": "LinkedIn", "value": "linkedin.com/in/elenarog"}]),
        "job_title": "CTO"
    },
    {
        "name": "Jordan Smith",
        "email": "jordan@elevate-media.co",
        "phone": "+1 (555) 246-8135",
        "company": "Elevate Media",
        "interest": "New",
        "email2": "[]",
        "social_media": "[]"
    }
]

def seed():
    print("Seeding sample contacts and interactions...")
    interactions_pool = [
        ("whatsapp_sync", "Received update about project milestones."),
        ("zoom_meeting", "Discussed quarterly budget and resource allocation."),
        ("email_received", "Sent follow-up regarding the proposal."),
        ("system_sync", "Contact details updated from LinkedIn."),
        ("teams_meeting", "Technical deep dive on architecture.")
    ]
    
    import random
    
    for contact in sample_contacts:
        success = db_service.add_contact(contact)
        if success:
            print(f"Added Contact: {contact['name']}")
            # Add 2-3 random interactions per contact
            num_int = random.randint(2, 4)
            for _ in range(num_int):
                i_type, i_content = random.choice(interactions_pool)
                db_service.add_interaction(contact['email'], i_type, i_content)
            print(f"  Added {num_int} interactions.")
        else:
            print(f"Failed to add: {contact['name']}")
    print("Done!")

if __name__ == "__main__":
    seed()
