from datetime import datetime
from services.access_logic import build_notification_text, determine_event_type


def test_first_event_is_in():
    assert determine_event_type(None) == 'IN'


def test_after_in_is_out():
    assert determine_event_type('IN') == 'OUT'


def test_after_out_is_in():
    assert determine_event_type('OUT') == 'IN'


def test_notification_for_entry():
    text=build_notification_text('Иванов Иван Иванович','7А','IN',datetime(2026,9,28,8,15,0))
    assert 'вошел(а) в школу' in text and '28.09.2026 08:15:00' in text


def test_notification_for_exit():
    text=build_notification_text('Иванов Иван Иванович','7А','OUT',datetime(2026,9,28,15,10,0))
    assert 'вышел(ла) из школы' in text
