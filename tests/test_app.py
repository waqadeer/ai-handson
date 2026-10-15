import json

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home_page_has_no_logout_when_logged_out():
    response = client.get('/')
    assert response.status_code == 200
    html = response.text
    assert 'Log out' not in html
    assert 'Upload your requirement document' in html or 'Upload a requirement document' in html


def test_proposal_route_returns_valid_json_payload():
    response = client.post('/analyze-docs')
    assert response.status_code == 200, response.text
    payload = response.json()
    assert 'analysis' in payload
    assert isinstance(payload['analysis'], str)
    text = payload['analysis'].strip()
    assert 'summary' in text.lower()


def test_api_ticket_endpoints_still_work():
    tickets = client.get('/api/tickets')
    assert tickets.status_code == 200
    payload = tickets.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1


def test_mvp_page_has_logout_button_hidden_until_login():
    response = client.get('/mvp')
    assert response.status_code == 200
    html = response.text
    assert 'logoutBtn' in html
    assert 'Log out' in html
