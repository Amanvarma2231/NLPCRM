from app.services.contact_service import contact_service

print("--- Testing Smart Deduplication ---")

# Step 1: Insert initial data
payload_1 = {
    "name": "Jane Doe",
    "email": "jane.dedupe@test.com",
    "phone": "555-0001",
    "interest": "Low",
    "source": "Manual Test 1"
}

contact_service.add_contact(payload_1)
print(f"Inserted Jane (Payload 1) - Low Interest")

# Step 2: Insert with same email, but new phone / company / better interest
payload_2 = {
    "name": "Jane", 
    "email": "jane.dedupe@test.com", # Same primary email!
    "phone": "555-9999", # New phone
    "company": "Dedupe Inc.", # New data
    "interest": "High",
    "source": "Manual Test 2"
}

contact_service.add_contact(payload_2)
print(f"Inserted Jane (Payload 2) - High Interest, New Phone & Company")

# Step 3: Fetch and display to verify merge
contacts = contact_service.get_contacts()
merged_jane = next((c for c in contacts if c['email'] == 'jane.dedupe@test.com'), None)

if merged_jane:
    print("\n--- Merged Contact Record ---")
    print(f"Name: {merged_jane['name']}")
    print(f"Company: {merged_jane['company']} (Should be Dedupe Inc.)")
    print(f"Interest: {merged_jane['interest']} (Should be High)")
    print(f"Email: {merged_jane['email']}")
    print(f"Phone: {merged_jane['phone']}")
    print(f"Activities: Please check UI timeline")
else:
    print("Error: Could not find Jane in DB")
