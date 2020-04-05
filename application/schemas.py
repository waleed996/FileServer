"""
Schemas for serializing and deserializing.
"""

from marshmallow import ValidationError
from marshmallow.fields import Method
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .models import File, User, UserType, FilePermission


class UserSchema(SQLAlchemyAutoSchema):
    """Schema for user model."""

    class Meta:
        """Options for model schema."""
        model = User
        exclude = ('id', 'created_at')
        load_instance = True

    user_type = Method(deserialize='usertype_name_to_id')

    def usertype_name_to_id(self, user_type_input):
        """Custom method for deserialization of usertype name to id"""

        usertype = UserType.query.filter_by(name=user_type_input).first()

        if usertype is None:
            raise ValidationError(message='user type not supported')

        return usertype.id


class UserTypeSchema(SQLAlchemyAutoSchema):
    """Schema for usertype model."""

    class Meta:
        """Options for model schema."""
        model = UserType
        load_instance = True


class FilePermissionSchema(SQLAlchemyAutoSchema):
    """Schema for file permission model."""

    class Meta:
        """Options for model schema."""
        model = FilePermission
        load_instance = True


class FileSchema(SQLAlchemyAutoSchema):
    """Schema for File model."""

    class Meta:
        """Options for model schema."""
        model = File
        exclude = ('id', 'user', 'last_updated')
        load_instance = True
