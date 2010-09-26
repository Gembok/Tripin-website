from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

import front.models

class MemberForm(djangoforms.ModelForm):
    model = front.models.Member
    show = ['name', 'bio']
    class Meta:
        model = front.models.Member
        exclude = []

registered = {'member': MemberForm}