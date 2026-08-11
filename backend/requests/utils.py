from .models import FunctionRequest

def check_double_booking(venue, start_date, end_date, time_from, time_to, exclude_req_id=None):
    """
    Checks if there is an existing APPROVED request overlapping with the given venue, date range, and time range.
    """
    if not venue or not start_date or not end_date or not time_from or not time_to:
        return False

    overlapping = FunctionRequest.objects.filter(
        venue=venue,
        status='APPROVED',
        start_date__lte=end_date,
        end_date__gte=start_date,
        time_from__lt=time_to,
        time_to__gt=time_from
    )

    if exclude_req_id:
        overlapping = overlapping.exclude(id=exclude_req_id)

    return overlapping.exists()
