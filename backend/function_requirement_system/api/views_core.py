from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
from django.db.models import Q
from departments.models import Department
from halls.models import SeminarHall
from requests.models import FunctionRequest
from .serializers_core import DepartmentSerializer, SeminarHallSerializer

class IsSuperuserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role == 'MANAGEMENT')

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsSuperuserOrReadOnly]

class SeminarHallViewSet(viewsets.ModelViewSet):
    queryset = SeminarHall.objects.all()
    serializer_class = SeminarHallSerializer
    permission_classes = [IsSuperuserOrReadOnly]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def available(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date') or start_date_str
        time_from_str = request.query_params.get('time_from')
        time_to_str = request.query_params.get('time_to')
        exclude_req_id = request.query_params.get('exclude_request_id')

        halls = SeminarHall.objects.all()
        hall_data = []

        if not start_date_str or not time_from_str or not time_to_str:
            # If timing parameters are not fully provided, return all halls marked available
            for hall in halls:
                data = SeminarHallSerializer(hall).data
                data['is_available'] = True
                data['conflict_details'] = None
                hall_data.append(data)
            return Response(hall_data)

        try:
            start_d = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_d = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else start_d
            t_from = datetime.strptime(time_from_str[:5], '%H:%M').time()
            t_to = datetime.strptime(time_to_str[:5], '%H:%M').time()
        except ValueError:
            for hall in halls:
                data = SeminarHallSerializer(hall).data
                data['is_available'] = True
                data['conflict_details'] = None
                hall_data.append(data)
            return Response(hall_data)

        # Active requests occupying venues
        conflicting_requests = FunctionRequest.objects.exclude(
            status__in=['REJECTED', 'CANCELLED']
        ).filter(
            venue__isnull=False
        )

        if exclude_req_id:
            conflicting_requests = conflicting_requests.exclude(id=exclude_req_id)

        # Build booking map by venue_id
        conflicts_by_venue = {}
        for req in conflicting_requests:
            req_start = req.start_date
            req_end = req.end_date or req.start_date
            req_t_from = req.time_from
            req_t_to = req.time_to

            # Date overlap check: start_d <= req_end and end_d >= req_start
            date_overlaps = (start_d <= req_end) and (end_d >= req_start)
            # Time overlap check: t_from < req_t_to and t_to > req_t_from
            time_overlaps = (t_from < req_t_to) and (t_to > req_t_from)

            if date_overlaps and time_overlaps:
                conflicts_by_venue[req.venue_id] = {
                    'request_id': req.id,
                    'function_name': req.function_name,
                    'organizer_name': req.organizer_name,
                    'start_date': str(req.start_date),
                    'end_date': str(req.end_date or req.start_date),
                    'time_from': str(req.time_from),
                    'time_to': str(req.time_to),
                    'status': req.status
                }

        for hall in halls:
            data = SeminarHallSerializer(hall).data
            if hall.id in conflicts_by_venue:
                data['is_available'] = False
                data['conflict_details'] = conflicts_by_venue[hall.id]
            else:
                data['is_available'] = True
                data['conflict_details'] = None
            hall_data.append(data)

        return Response(hall_data)

