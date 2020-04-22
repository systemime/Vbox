from django.contrib import admin
from users import models as user_models
from rbac import models as rbac_models
# Register your models here.


admin.site.register(user_models.UserProfile)
admin.site.register(rbac_models.Role)
admin.site.register(rbac_models.Permission)

