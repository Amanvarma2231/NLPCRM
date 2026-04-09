from app.services.db_service import db_service

def clear_target_number():
    print("Checking settings for target number...")
    settings = db_service.get_settings()
    if settings.get('WHATSAPP_PHONE') == '9795529326':
        print("Found target number. Clearing...")
        db_service.save_setting('WHATSAPP_PHONE', '')
        print("Number cleared successfully.")
    else:
        print(f"Number not found or already changed. Current value: {settings.get('WHATSAPP_PHONE')}")

if __name__ == "__main__":
    clear_target_number()
