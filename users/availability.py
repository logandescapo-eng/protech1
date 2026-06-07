"""Worker weekly availability helpers."""

from datetime import datetime

from .models import WorkerAvailability


def get_worker_availability(worker):
    """Return list of dicts for template (one row per weekday)."""
    existing = {
        a.day_of_week: a
        for a in WorkerAvailability.objects.filter(worker=worker, is_available=True)
    }
    rows = []
    for day_val, day_label in WorkerAvailability.DAYS_OF_WEEK:
        slot = existing.get(day_val)
        rows.append({
            'day_of_week': day_val,
            'day_label': day_label,
            'enabled': slot is not None,
            'start_time': slot.start_time.strftime('%H:%M') if slot else '09:00',
            'end_time': slot.end_time.strftime('%H:%M') if slot else '17:00',
        })
    return rows


def save_worker_availability(worker, post_data):
    """Persist availability from settings form POST."""
    WorkerAvailability.objects.filter(worker=worker).delete()
    for day_val, _label in WorkerAvailability.DAYS_OF_WEEK:
        if post_data.get(f'avail_{day_val}_enabled'):
            start = post_data.get(f'avail_{day_val}_start', '09:00')
            end = post_data.get(f'avail_{day_val}_end', '17:00')
            WorkerAvailability.objects.create(
                worker=worker,
                day_of_week=int(day_val),
                start_time=start,
                end_time=end,
                is_available=True,
            )


def check_slot_available(worker, scheduled_date, scheduled_time):
    """
    Return (ok, message). If worker has no availability rows, any time is allowed.
    """
    slots = list(WorkerAvailability.objects.filter(worker=worker, is_available=True))
    if not slots:
        return True, ''
    weekday = scheduled_date.weekday()
    matching = [s for s in slots if s.day_of_week == weekday]
    if not matching:
        day_name = dict(WorkerAvailability.DAYS_OF_WEEK).get(weekday, 'that day')
        return False, f'Worker is not available on {day_name}.'
    for slot in matching:
        if slot.start_time <= scheduled_time <= slot.end_time:
            return True, ''
    return False, 'Selected time is outside the worker\'s available hours.'
