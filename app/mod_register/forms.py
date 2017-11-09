from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class RegisterInstagramUserForm(FlaskForm):
    class Meta:
        csrf=False
    insta_handle = StringField('Instagram Handle', validators=[DataRequired("Instagram Handle is Required.")])
