from django.shortcuts import render
from users.models import UserProfile
# Create your views here.

from tools.tool import login_required

@login_required
def show_file_upload(request):
    return render(request, 'file/file_upload.html')


