from app import create_app
from flask import session

app = create_app()
app.config['TESTING'] = True

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['user_email'] = 'admin@nlpcrm.com'
    
    response = client.get('/contacts')
    if response.status_code == 500:
        print("500 ERROR CAUGHT!")
        print(response.data.decode('utf-8'))
    else:
        print(f"Status: {response.status_code}")
