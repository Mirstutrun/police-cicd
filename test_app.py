import uuid
from app import app, db, Officer

PAGES = ['/', '/officers', '/cases', '/suspects', '/evidence', '/interrogations']


def get_client():
    app.config['TESTING'] = True
    return app.test_client()


def test_pages_open():
    client = get_client()
    for page in PAGES:
        assert client.get(page).status_code == 200, f"Страница {page} не открылась"


def test_officer_crud():
    client = get_client()
    badge = 'T-' + uuid.uuid4().hex[:8]

    # Create
    r = client.post('/add_officer', data={'name': 'Тест', 'rank': 'Лейтенант', 'badge_number': badge})
    assert r.status_code == 302
    with app.app_context():
        officer = Officer.query.filter_by(badge_number=badge).first()
        assert officer is not None
        officer_id = officer.id

    # Update
    r = client.post(f'/update_officer/{officer_id}',
                    data={'name': 'Тест2', 'rank': 'Капитан', 'badge_number': badge})
    assert r.status_code == 302
    with app.app_context():
        assert db.session.get(Officer, officer_id).rank == 'Капитан'

    # Delete
    r = client.get(f'/delete_officer/{officer_id}')
    assert r.status_code == 302
    with app.app_context():
        assert db.session.get(Officer, officer_id) is None