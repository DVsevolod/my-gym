from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.core.validators import validate_email

from .models import UserModel, TokenModel


# authentication app: LoginView
def write_refresh_token_to_db(user_id, refresh_token):
    user = UserModel.objects.get(pk=user_id)
    try:
        token_model_obj = TokenModel.objects.get(user=user)
        token_model_obj.refresh_token = refresh_token
        token_model_obj.save()
    except TokenModel.DoesNotExist:
        TokenModel.objects.create(user=user, refresh_token=refresh_token)


# my_gym app: ProfileFilter
def get_expire_date(month):
    return datetime.now().date() - relativedelta(months=month)


def check_user_data(user_data):
    first_name = user_data.get('first_name', None)
    last_name = user_data.get('last_name', None)
    email = user_data.get('email', None)
    password = user_data.get('password', None)

    id_ = user_data.get('id', None)
    role = user_data.get('role', None)
    is_active = user_data.get('is_active', None)

    if email:
        validate_email(email)

    if role or id_ or is_active:
        raise PermissionError('Only admin can change fields: "id", "role", "is_active".')

    if first_name and first_name.isdigit():
            raise ValueError('First name could not be an integer.')
    if last_name and last_name.isdigit():
        raise ValueError('Last name could not be an integer.')

    if password and not isinstance(password, str):
        raise ValueError('Password must be a string.')

def check_subscription_data(sub_data):
    month_tuple = (1,6,12)
    month = sub_data.get('month', None)
    updated_at = sub_data.get('updated_at', None)

    id_ = sub_data.get('id', None)

    if id_:
        raise PermissionError('Only admin can change field "id".')

    if month and int(month) not in month_tuple:
        raise ValueError('Month must be: [1, 6, 12].')

    if updated_at:
        try:
            date(*[int(item) for item in updated_at.split('-')])
        except Exception:
            raise ValueError('Date must be a string in YYYY-MM-DD format.')
