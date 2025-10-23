from wtforms import Form, PasswordField, StringField
from wtforms.validators import InputRequired


class SiteCreateForm(Form):
    address = StringField("Address", validators=[InputRequired()])
    username = StringField("Wp Username", validators=[InputRequired()])
    password = PasswordField("Wp Password", validators=[InputRequired()])
