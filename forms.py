from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class AddUserForm(FlaskForm):
    """Form for adding Users"""

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(
                min=5, max=15, message="Username must be between 5 and 15 characters."
            ),
        ],
    )
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            Length(min=5, message="Password must be at least 5 characters long.")
        ],
    )
    image_url = StringField("(Optional) Image URL")


class LoginUserForm(FlaskForm):
    """Form for logging in Users"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=5)])


class EditUserForm(FlaskForm):
    """Form for editing/updating User profile"""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[Length(min=5)])
    image_url = StringField("(Optional) Image URL")
    bio = TextAreaField("(Optional) Share whatever you'd like")


class PostForm(FlaskForm):
    """Form for creating/editing blog posts"""

    text = TextAreaField("Text Area", validators=[DataRequired()])
    song_id = StringField("Spotify Song", validators=[Optional()])
