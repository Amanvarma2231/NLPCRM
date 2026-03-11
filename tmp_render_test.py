from app import create_app
from app.services.db_service import db_service
from flask import render_template

app = create_app()
with app.app_context():
    with app.test_request_context():
        contacts = db_service.get_contacts()
        try:
            render_template("contacts.html", contacts=contacts)
            print("Template rendering successful!")
        except Exception as e:
            import traceback
            traceback.print_exc()
