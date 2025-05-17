import pytest
from .utils import compute_diff
import json
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from text_analysis.models import TypingEvent, Exercise
from django.urls import reverse
from django.contrib.auth import get_user_model
from text_analysis.models import Exercise, SavedText

def test_insert_diff():
    d = compute_diff('', 'a')
    assert d == {'action':'insert','char':'a','position':0}

def test_delete_diff():
    d = compute_diff('ab', 'a')
    assert d == {'action':'delete','char':'b','position':1}

def test_no_change_raises():
    with pytest.raises(ValueError):
        compute_diff('abc', 'abc')

def test_multi_char_error():
    with pytest.raises(ValueError):
        compute_diff('', 'ab')


User = get_user_model()

@pytest.mark.django_db
def test_save_typing_data_view():
    # crée user + exo
    user = User.objects.create_user(username='u', password='p')
    exo  = Exercise.objects.create(author=user, title='T', content='')
    client = Client()
    client.force_login(user)

    payload = {
        'final_text': 'test',
        'context': 'c',
        'text_type': 'narratif',
        'time_list': [1000, 2000, 3000, 4000],
        'text_list': ['t','te','tes','test'],
        'cursor_list': ['1','2','3','4'],
        'student_id': str(user.id),
        'exercise_id': str(exo.id),
    }

    resp = client.post(reverse('save_typing_data'),
                       data=json.dumps(payload),
                       content_type='application/json')
    assert resp.status_code == 200
    assert TypingEvent.objects.filter(exercise=exo, student=user).count() == 4



User = get_user_model()

@pytest.mark.django_db
def test_home_view_contains_exercise_and_saved_texts(client):
    user = User.objects.create_user(username='u', password='p')
    client.force_login(user)
    exo = Exercise.objects.create(author=user, title='Exo', content='Contenu')
    saved = SavedText.objects.create(text='T1', score=5)
    resp = client.get(reverse('text_analysis:home') + f'?exercise={exo.id}')
    assert resp.status_code == 200
    ctx = resp.context
    assert 'exercises' in ctx
    assert ctx['exercise'].id == exo.id
    assert 'saved_texts' in ctx and saved in ctx['saved_texts']

