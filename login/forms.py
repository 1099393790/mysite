from django import forms
from captcha.fields import CaptchaField

class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=128, widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "请输入用户名", 'required': 'required '}))
    password = forms.CharField(label='密码', max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control', "placeholder": "请输入密码", 'required': 'required '}))
    captcha = CaptchaField(label='验证码') # 为生成的验证码图片，以及输入框,文本框

'''
说明：
    1.要先导入forms模块,所有的表单类都要继承forms.Form类
    2.每个表单字段都有自己的字段类型比如CharField，
        它们分别对应一种HTML语言中<form>内的一个input元素。
        这一点和Django模型系统的设计非常相似。
    3.label参数用于设置<label>标签
    4.max_length限制字段输入的最大长度。它同时起到两个作用，
        一是在浏览器页面限制用户输入不可超过字符数，二是在后端服务器验证用户输入的长度也不可超过。
    5.widget=forms.PasswordInput用于指定该字段在form表单里表现为<input type='password' />，也就是密码输入框。
    6.attrs={'class': 'form-control'} 给input标签增加class属性
    7.注意需要提前导入from captcha.fields import CaptchaField，然后就像写普通的form字段一样添加一个captcha字段就可以了！
    8.required:必填字段
'''

class RegisterFrom(forms.Form):
    gender = (
        ('male', "男"),
        ('female', "女"),
    )
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(label='性别', choices=gender)
    captcha = CaptchaField(label='验证码')
'''
说明：
    gender字典和User模型中的一样，其实可以拉出来作为常量共用，为了直观，特意重写一遍；
    password1和password2，用于输入两遍密码，并进行比较，防止误输密码；
    email是一个邮箱输入框；
    sex是一个select下拉框；
'''