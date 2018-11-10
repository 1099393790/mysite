from django.db import models

# Create your models here.
class User(models.Model):
    gender = (
        ('nale', "男"),
        ('female', "女"),
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default="男")
    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-c_time']
        verbose_name = "用户"  # 最常用的元数据之一！用于设置模型对象的直观、人类可读的名称。可以用中文。如果你不指定它，那么Django会使用小写的模型名作为默认值。
        verbose_name_plural = "用户" # 英语有单数和复数形式。这个就是模型对象的复数名，比如“apples”。因为我们中文通常不区分单复数，所以保持和verbose_name一致也可以,如果不指定该选项，那么默认的复数名字是verbose_name加上‘s’

'''
各字段含义：
    name必填，最长不超过128个字符，并且唯一，也就是不能有相同姓名；
    password必填，最长不超过256个字符（实际可能不需要这么长）；
    email使用Django内置的邮箱类型，并且唯一；
    性别使用了一个choice，只能选择男或者女，默认为男；
    使用__str__帮助人性化显示对象信息；
    元数据里定义用户按创建时间的反序排列，也就是最近的最先显示；
    has_confirmed字段，这是个布尔值，默认为False，也就是未进行邮件注册
'''

class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + ":   " + self.code

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"


'''
说明：
    ConfirmString模型保存了用户和注册码之间的关系，一对一的形式；
    code字段是哈希后的注册码；
    user是关联的一对一用户；
    c_time是注册的提交时间。
'''