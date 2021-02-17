

class RoleURLParamError:
    msg = "Role parameter was not passed in URL. Use /users/?role=1 " \
          "to get clients profiles, or /users/?role=2 to get staff profiles."


class ExpireError:
    msg = "Subscription is expired!"
    code = 1