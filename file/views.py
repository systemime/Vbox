from django.shortcuts import render
from django.http import JsonResponse
from users.models import UserProfile
# Create your views here.

from tools.tool import login_required

@login_required
def show_file_upload(request):
    if request.method == 'GET':
        img = UserProfile.objects.get(username=request.session.get('username', None)).avatar
        nickname = request.session.get('nickname', None)
        role = request.session.get('role', None)
        page = '文件上传'
        return render(request, 'file/file_upload.html', locals())
    else:
        if request.is_ajax():  # 如果是ajax请求
            for k, file_obj in request.FILES.items():  # 获取前端传过来的文件数据
                with open('%s/%s' % ('/home/soul/tools/' + request.session.get('username', None), file_obj.name), "wb") as f:  # 打开文件
                    for chunk in file_obj.chunks():
                        f.write(chunk)  # chunk方式写入文件
            return JsonResponse({'status': 200, 'error': '上传成功'})


