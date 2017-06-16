from django import forms
from .models import *
class Profilepic(forms.Form):
	userimage = forms.FileField()
	name=forms.CharField(max_length=20)

# class UploadImage(forms.ModelForm):
 
#     class Meta:
#         model = Useruploads   
#         fields=("name","image")


class Loginform(forms.Form):    
    username = forms.CharField(max_length=250)
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': "form-control input-lg",}),
        label='Password'
    )


class RegistrationForm(forms.Form):
    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30,),), label=("Username"), error_messages={ 'invalid': ("This value must contain only letters, numbers and underscores.") })
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=("Email address"))
    password = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=("Password (again)"))


class LoginForm(forms.Form):
    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30,),), label=("Username"), error_messages={ 'invalid': ("This value must contain only letters, numbers and underscores.") })
    password = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False,)), label=("Password"))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control input-sm'
        #self.fields['email'].widget.attrs['class'] = 'form-control input-sm'
        self.fields['password'].widget.attrs['class'] = 'form-control input-sm'
        #self.fields['password2'].widget.attrs['class'] = 'form-control input-sm'


class TaggingForm(forms.Form):
    username = forms.CharField(max_length=100)
    occupation = forms.CharField(max_length=100,required=False)
    mobile=forms.CharField(max_length=15,required=False)


class VisitorReportsForm(forms.Form):
    startdate = forms.CharField(max_length=100)
    enddate = forms.CharField(max_length=100,required=False)

class LockscreenForm(forms.Form):
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': "form-control input-lg",}),
        label='Password'
    )

  

    # def __init__(self, *args, **kwargs):
    #     super(LoginForm, self).__init__(*args, **kwargs)
    #     self.fields['username'].widget.attrs['class'] = 'form-control input-sm'
    #     #self.fields['email'].widget.attrs['class'] = 'form-control input-sm'
    #     self.fields['password'].widget.attrs['class'] = 'form-control input-sm'
    #     #self.fields['password2'].widget.attrs['class'] = 'form-control input-sm'
