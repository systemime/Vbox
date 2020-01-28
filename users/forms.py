from django import forms
from .models import UserProfile


class ProfileForm(forms.ModelForm):
    """
    从模型继承表单
    """

    class Meta:
        model = UserProfile
        fields = ['nick_name', 'mobile', 'address']

class LoginForm(forms.Form):
    # captcha = CaptchaField(error_messages={"invalid": "验证码错误"})
    username = forms.CharField(label="用户名", min_length=1, max_length=64)
    password = forms.CharField(label="密码", min_length=6, max_length=32, widget=forms.PasswordInput)





