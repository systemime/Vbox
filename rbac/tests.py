from django.test import TestCase

# Create your tests here.

'''
# 元数据
data = [{
        'permissions__url': '/customer/list/',
        'permissions__title': '客户列表',
        'permissions__menu__title': '信息列表',
        'permissions__menu__icon': 'fa-code-fork',
        'permissions__menu_id': 1
    },
    {
        'permissions__url': '/customer/list/',
        'permissions__title': '用户列表',
        'permissions__menu__title': '信息列表',
        'permissions__menu__icon': 'fa-code-fork',
        'permissions__menu_id': 1
    }, {
        'permissions__url': '/customer/add/',
        'permissions__title': '增加客户',
        'permissions__menu__title': None,
        'permissions__menu__icon': None,
        'permissions__menu_id': None
    }, {
        'permissions__url': '/customer/edit/(\\d+)/',
        'permissions__title': '编辑客户',
        'permissions__menu__title': None,
        'permissions__menu__icon': None,
        'permissions__menu_id': None
    }]
# 目标数据
{ 
  1:{
      'title':'信息列表',
      'icon':'fa-code-fork',
    'children': [
        {'title': '客户列表','url':'/customer/list/ },
        {'title': '用户列表','url':'/customer/list/ }
    ]
      
  }

}
'''
