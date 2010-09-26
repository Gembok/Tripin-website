import front.models

class Model:
	model = None
	show = []
	edit = []
	
class Member(Model):
	model = front.models.Member
	show = ['name', 'bio', 'image']
	edit = show

registered = {'member': Member}