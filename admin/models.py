import forms
import front.models

class Member(forms.Form):
	model = front.models.Member
	show = ['name', 'bio', 'image']
	edit = show

registered = {'member': Member}