"""
Schemas for serializing and deserializing.
"""

from flask_marshmallow.sqla import ModelSchema
from marshmallow import ValidationError
from marshmallow.fields import Method

from .models import User, UserType, File


class UserSchema(ModelSchema):
    """Schema for user model."""

    class Meta:
        """Options for model schema."""
        model = User
        exclude = ('id', 'created_at')

    user_type = Method(deserialize='usertype_name_to_id')

    def usertype_name_to_id(self, user_type_input):
        """Custom method for deserialization of usertype name to id"""

        usertype = UserType.query.filter_by(name=user_type_input).first()

        if usertype is None:
            raise ValidationError(message='user type not supported')

        return usertype.id


class UserTypeSchema(ModelSchema):
    """Schema for usertype model."""

    class Meta:
        """Options for model schema."""
        model = UserType

class FileSchema(ModelSchema):
    """Schema for File model."""

    class Meta:
        """Options for model schema."""
        model = File
        exclude = ('id', 'user', 'last_updated')
