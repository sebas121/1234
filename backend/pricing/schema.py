import json
import graphene

from . import models


def check_missing_months(city):
    missing_months = []
    months = [item[0] for item in models.CleaningPrice.MONTHS_CHOICES]
    for month in months:
        if not city.prices.filter(number_of_months=month).exists():
            missing_months.append(month)
    return missing_months


def check_missing_sessions(city):
    missing_sessions = []
    sessions = [item[0] for item in models.CleaningPrice.NUMBER_OF_SESSIONS]
    for session in sessions:
        if not city.prices.filter(sessions_per_week=session).exists():
            missing_sessions.append(session)
    return missing_sessions


def check_combinations(city):
    missing_combinations = []
    months = [item[0] for item in models.CleaningPrice.MONTHS_CHOICES]
    combinations = []
    for month in months:
        combinations.extend(
            [month, item[0]]
            for item in models.CleaningPrice.NUMBER_OF_SESSIONS)
    for combination in combinations:
        if not city.prices.filter(
                number_of_months=combination[0],
                sessions_per_week=combination[1]).exists():
            missing_combinations.append(combination)
    return missing_combinations


class Query(object):
    get_calculated_hours = graphene.String(
        city=graphene.String(),
        zip=graphene.String(),
        schedule=graphene.String(),
        months=graphene.String(),
        bedrooms=graphene.String(),
        baths=graphene.String(),
        extras=graphene.String(),
        hours_override=graphene.String(),
        email=graphene.String(),
        address=graphene.String(),
        first_visit=graphene.String(),
    )

    get_health_check_report = graphene.String()

    def resolve_get_calculated_hours(self, info, **args):
        requested_number_of_rooms = args.get('bedrooms', 0)

        result = {}

        # Hours
        min_rooms = models.CleaningHour.objects.get().min_rooms
        extra_rooms = int(requested_number_of_rooms) - min_rooms
        extra_rooms = extra_rooms if extra_rooms >= 1 else None
        hours = models.CleaningHour.objects.get().get_work_hours(
            extra_rooms=extra_rooms)
        result['hours'] = hours
        return result

    def resolve_get_health_check_report(self, info, **args):
        response = {}
        has_error = False
        cities = models.City.objects.all()
        for city in cities:
            response[city.name] = {}

            missing_months = check_missing_months(city)
            response[city.name]['missing_months'] = missing_months

            missing_sessions = check_missing_sessions(city)
            response[city.name]['missing_sessions'] = missing_sessions

            missing_month_session_combinations = check_combinations(city)
            response[city.name][
                'missing_combinations'] = missing_month_session_combinations

            if (missing_months or missing_sessions
                    or missing_month_session_combinations):
                has_error = True
            else:
                continue

        if has_error:
            response['status'] = 'ERRORS FOUND!'
        else:
            response['status'] = 'EVERYTHING IS GOOD'

        return json.dumps(response)
