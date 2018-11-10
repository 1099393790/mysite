from django.shortcuts import render
from django.shortcuts import redirect
from .models import User,ConfirmString
from .forms import UserForm, RegisterFrom
from django.conf import settings
import hashlib
import datetime
from django.utils import timezone

# Create your views here.
# 密码加密函数
def hash_code(s, salt="mysite"): # 加点料
    h = hashlib.sha3_256()
    s += salt
    h.update(s.encode())# update方法只接收bytes类型
    return h.hexdigest()

# 创建注册码方法
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    ConfirmString.objects.create(code=code, user=user,)
    return code
'''
    make_confirm_string()方法接收一个用户对象作为参数。
    首先利用datetime模块生成一个当前时间的字符串now，
    再调用我们前面编写的hash_code()方法以用户名为基础，now为‘盐’，
    生成一个独一无二的哈希值，再调用ConfirmString模型的create()方法，
    生成并保存一个确认码对象。最后返回这个哈希值。
'''

# 发送邮件、注册码函数
def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = '邮件主题'
    text_content = '如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！' \
                   'text_content是用于当HTML内容无效时的替代txt文本'
    html_content = '''
    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.liujiangblog.com</a>，\
    这里是刘江的博客和教程站点，专注于Python和Django技术的分享！</p>
    <p>请点击站点链接完成注册确认！</p>
     <p>此链接有效期为{}天！</p>
     '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS) # 一一对应html_content中{ }中的值

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email]) # subject：邮件主题 text_content, settings.EMAIL_HOST_USER：发件者邮箱 [email]：收件者邮箱
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def index(request):
    return render(request, 'login/index.html')

# 登陆函数
def login(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid(): # 如果form有效
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(name=username)
                if not user.has_confirmed:
                    message = "该用户还未通过邮件确认！"
                    return render(request, 'login/login.html', locals())
                if user.password == hash_code(password):# 哈希值和数据库内的值进行比对
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())

        # if username and password: # 确保用户名和密码都不为空
        #     username = username.strip() # 通过strip()方法，将用户名前后无效的空格剪除；
        #     # 用户名字符合法性验证
        #     # 密码长度验证
        #     # 更多的其它验证.....

'''
说明：
    1.每个视图函数都至少接收一个参数，并且是第一位置参数，该参数封装了当前请求的所有数据；
      通常将第一参数命名为request，当然也可以是别的；
    2.request.method中封装了数据请求的方法，如果是“POST”（全大写），将执行if语句的内容，如果不是，直接返回最后的render()结果；
    3.request.POST封装了所有POST请求中的数据，这是一个字典类型，可以通过get方法获取具体的值。
    4.类似get('username')中的键‘username’是HTML模板中表单的input元素里‘name’属性定义的值。所以在编写form表单的时候一定不能忘记添加name属性。
    5.利用print函数在开发环境中验证数据；
    6.利用redirect方法，将页面重定向到index页。
    
    7.对于非POST方法发送数据时，比如GET方法请求页面，返回空的表单，让用户可以填入数据；
    8.对于POST方法，接收表单数据，并验证；
    9.使用表单类自带的is_valid()方法一步完成数据验证工作；
    10.验证成功后可以从表单对象的cleaned_data数据字典中获取表单的具体值；
    11.如果验证不通过，则返回一个包含先前数据的表单给前端页面，方便用户修改。也就是说，它会帮你保留先前填写的数据内容，而不是返回一个空表！
    12.另外，这里使用了一个小技巧，Python内置了一个locals()函数，它返回当前所有的本地变量字典，
      我们可以偷懒的将这作为render函数的数据字典参数值，就不用费劲去构造一个形如{'message':message, 'login_form':login_form}的字典了。
      这样做的好处当然是大大方便了我们，但是同时也可能往模板传入了一些多余的变量数据，造成数据冗余降低效率。
    13.通过下面的if语句，我们不允许重复登录：
        if request.session.get('is_login',None):
           return redirect("/index/")
    14.通过下面的语句，我们往session字典内写入用户状态和数据：
         request.session['is_login'] = True
         request.session['user_id'] = user.id
         request.session['user_name'] = user.name
'''

# 注册函数
def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterFrom(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid(): # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2: # 判断两次密码是否相同
                message = "两次输入的密码不一样！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())
                else:
                    # 当一切都OK的情况下，创建新用户
                    new_user = User()
                    new_user.name = username
                    new_user.password = hash_code(password1)# 使用加密密码
                    new_user.email = email
                    new_user.sex = sex
                    new_user.save()

                    code = make_confirm_string(new_user)
                    send_email(email, code)
                    message = "请前往注册邮箱，进行邮箱确认！"
                    return render(request, 'login/confirm.html', locals())
                    # return redirect('/login/')  # 自动跳转到登录页面
    register_form = RegisterFrom()
    return render(request, 'login/register.html', locals())
'''
从大体逻辑上，也是先实例化一个RegisterForm的对象，然后使用is_valide()验证数据，再从cleaned_data中获取数据。
重点在于注册逻辑，首先两次输入的密码必须相同，其次不能存在相同用户名和邮箱，最后如果条件都满足，利用ORM的API，
创建一个用户实例，然后保存到数据库内。
'''

# 登出函数
def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index/")
'''
flush()方法是比较安全的一种做法，
而且一次性将session中的所有内容全部清空，确保不留后患。
但也有不好的地方，那就是如果你在session中夹带了一点‘私货’，会被一并删除，这一点一定要注意。
'''

''''
注意：
    1.在顶部额外导入了redirect，用于logout后，页面重定向到‘index’首页；
    2.四个视图都返回一个render()调用，render方法接收request作为第一个参数，
      要渲染的页面为第二个参数，以及需要传递给页面的数据字典作为第三个参数（可以为空），
      表示根据请求的部分，以渲染的HTML页面为主体，使用模板语言将数据字典填入，然后返回给用户的浏览器。
    3.渲染的对象为login目录下的html文件，这是一种安全可靠的文件组织方式。
'''

# 确认注册码方法
def user_confirm(request):
    code = request.GET.get('code', None) #获取在邮箱中点击链接后返回的code注册码
    message = ''
    try:
        confirm = ConfirmString.objects.get(code=code) # 获取ConfirmString数据表中的code判断是否已经通过邮箱验证
    except:
        message = "无效的确认请求！"
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time # 获取注册连接的提交时间
    now = timezone.now() # 获取当前的时间
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS): # 判断现在的时间是否大于注册连接的提交时间加上链接过期的限定天数
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())
'''
说明：
    通过request.GET.get('code', None)从请求的url地址中获取确认码;
    先去数据库内查询是否有对应的确认码;
    如果没有，返回confirm.html页面，并提示;
    如果有，获取注册的时间c_time，加上设置的过期天数，这里是7天，然后与现在时间点进行对比；
    如果时间已经超期，删除注册的用户，同时注册码也会一并删除，然后返回confirm.html页面，并提示;
    如果未超期，修改用户的has_confirmed字段为True，并保存，表示通过确认了。然后删除注册码，但不删除用户本身。最后返回confirm.html页面，并提示。
'''