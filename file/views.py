from django.shortcuts import render
from django.http import JsonResponse
from users.models import UserProfile
from django.views.generic import View
from tools.logs import event_log, save_file_log
from tools.tool import login_required
from Vbox import celery_app
import os
# 对类视图使用装饰器需要使用这个方法
from django.utils.decorators import method_decorator


@celery_app.task
def save_file(username, file_obj, nickname, REMOTE_ADDR, HTTP_USER_AGENT):
    try:
        with open('%s/%s' % ('/home/soul/tools/' + username, file_obj.name),
                  "wb") as f:  # 打开文件
            for chunk in file_obj.chunks():
                f.write(chunk)  # chunk方式写入文件
        event_log.delay(nickname, 1, 23, '[{}] 文件上传成功'.format(nickname), REMOTE_ADDR,
                        HTTP_USER_AGENT, str(file_obj.name))
    except Exception as err:
        event_log.delay(nickname, 1, 23, '[{}] 文件上传失败'.format(nickname), REMOTE_ADDR,
                        HTTP_USER_AGENT, str(err))

@celery_app.task
def delete_file(PATH, FILENAME):
    os.remove(PATH + FILENAME)


@method_decorator(login_required, name='dispatch')
class File_upload(View):

    def get(self, request):
        img = UserProfile.objects.get(username=request.session.get('username', None)).avatar
        nickname = request.session.get('nickname', None)
        role = request.session.get('role', None)
        page = '文件上传'
        event_log.delay(nickname, 1, 22, '[{}] 访问文件上传页面'.format(nickname),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        str(request.headers))
        return render(request, 'file/file_upload.html', locals())

    def post(self, request):
        # if request.is_ajax():
        username = request.session.get('username', None)
        nickname = request.session.get('nickname', None)
        REMOTE_ADDR = request.META.get('REMOTE_ADDR', None)
        HTTP_USER_AGENT = request.META.get('HTTP_USER_AGENT', None)
        for k, file_obj in request.FILES.items():  # 获取前端传过来的文件数据
            SIZE = file_obj.size
            FILENAME = file_obj.name
            save_file(username, file_obj, nickname, REMOTE_ADDR, HTTP_USER_AGENT)
            save_file_log(username, FILENAME, SIZE, nickname, REMOTE_ADDR, HTTP_USER_AGENT)
        return JsonResponse({'status': 200, 'error': '上传成功'})

@login_required
def del_file(request):
    PATH = '/home/soul/tools/' + request.session.get('username', None) + '/'
    print('当前路径下文件如下：%s' % os.listdir(PATH))
    for k, file_obj in request.FILES.items():
        FILENAME = file_obj.name
        # 判断文件是否存在
        if os.path.exists(PATH + FILENAME):
            try:
                delete_file(PATH, FILENAME)
                event_log.delay(request.session.get('nickname', None), 1, 25,
                                '[{}] 文件删除成功'.format(request.session.get('nickname', None)),
                                request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                                str(FILENAME))
                return JsonResponse({'status': 200, 'message': '删除成功'})
            except Exception as err:
                event_log.delay(request.session.get('nickname', None), 1, 25,
                                '[{}] 文件删除失败'.format(request.session.get('nickname', None)),
                                request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                                str(FILENAME))
                return JsonResponse({'status': err, 'message': '删除失败'})
        else:
            event_log.delay(request.session.get('nickname', None), 1, 25,
                            '[{}] 文件不存在'.format(request.session.get('nickname', None)),
                            request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                            str(FILENAME))
            return JsonResponse({'status': 25, 'message': '文件不存在'})



# ['DEFAULT_CHUNK_SIZE', '__bool__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__enter__',
# '__eq__', '__exit__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__
# ', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__',
# '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_get_name', '_name',
# '_set_name', 'charset', 'chunks', 'close', 'closed', 'content_type', 'content_type_extra', 'encoding', 'field_name',
# 'file', 'fileno', 'flush', 'isatty', 'multiple_chunks', 'name', 'newlines', 'open', 'read', 'readable', 'readinto',
# 'readline', 'readlines', 'seek', 'seekable', 'size', 'tell', 'truncate', 'writable', 'write', 'writelines']

