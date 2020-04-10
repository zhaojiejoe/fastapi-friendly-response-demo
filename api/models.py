from tortoise import fields, models


class Auth_User(models.Model):
    """
    The User model
    """

    id = fields.IntField(pk=True)
    #: This is a username
    username = fields.CharField(max_length=150, unique=True)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=150, null=True)
    email = fields.CharField(max_length=30, null=True)
    password = fields.CharField(max_length=128, null=True)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    date_joined = fields.DatetimeField(auto_now_add=True)
    last_login = fields.DatetimeField(auto_now=True)

    def full_name(self) -> str:
        """
        Returns the best name
        """
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.username

    def date_joined_str(self) -> str:
        return str(self.date_joined)    

    class PydanticMeta:
        computed = ["full_name", "date_joined_str"]


class Auth_Group(models.Model):
    """
    The User model
    """
    id = fields.IntField(pk=True)
    #: This is a username
    name = fields.CharField(max_length=150, unique=True)

    class PydanticMeta:
        exclude = ["id"]

