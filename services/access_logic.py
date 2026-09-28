def determine_event_type(last_event):
    return 'IN' if last_event is None or last_event == 'OUT' else 'OUT'


def build_notification_text(full_name, class_name, event_type, event_time):
    action_ru = 'вошел(а) в школу' if event_type == 'IN' else 'вышел(ла) из школы'
    return f'{full_name}, класс {class_name}: {action_ru}. Время: {event_time:%d.%m.%Y %H:%M:%S}'
