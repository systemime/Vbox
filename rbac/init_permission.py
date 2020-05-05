from django.conf import settings


def init_permisson(request, user):
    """
        权限信息的初识化
        保存权限和菜单的信息
        :param request:
        :param user:
        :return:
     """
    # 登陆成功，保存权限的信息（可能存在创建了角色没有分配权限，有的用户拥有多个角色权限重复的要去重.distinct()）
    ret = user.role.all().filter(
        permissions__url__isnull=False
    ).values(
        'permissions__url', 'permissions__title', 'permissions__menu__title', 'permissions__menu_id'
    ).distinct()

    # 存放权限信息
    permission_list = []
    # 存放菜单信息
    menu_dict = {}
    for item in ret:
        # 将所有的权限信息添加到permission_list
        permission_list.append({'url': item['permissions__url']})
        # 构造菜单的数据结构
        menu_id = item.get('permissions__menu_id')

        # 表示当前的权限是不做菜单的权限
        if not menu_id:
            continue

        # 可以做菜单的权限
        if menu_id not in menu_dict:
            menu_dict[menu_id] = {
                'title': item['permissions__menu__title'],  # 一级菜单标题
                # 'icon': item['permissions__menu__icon'],
                'children': [
                    {'title': item['permissions__title'], 'url': item['permissions__url']},
                ]
            }
        else:
            if not [title for title in menu_dict[menu_id]['children'] if list(title.values())[0] == item['permissions__title']]:
                menu_dict[menu_id]['children'].append({
                    'title': item['permissions__title'],
                    'url': item['permissions__url']
                })

    # 保留权限信息到session
    request.session[settings.PERMISSION_SESSION_KEY] = permission_list
    # 保存菜单信息
    request.session[settings.PERMISSION_MENU_KEY] = menu_dict
    '''
    # permission_list
    [{'url': '/file/file_upload/'}, {'url': '/file/file_list/'}, {'url': '/selectos/select/'},
     {'url': '/selectos/delete_user_deployment/'}, {'url': '/webguacamole/terminal/<int:pod_id>'},
     {'url': '/webssh/webterminal/'}]
    # menu_dict
    {4: {'title': '文件操作',
         'children': [{'title': '文件上传', 'url': '/file/file_upload/'}, {'title': '文件列表', 'url': '/file/file_list/'}]}}
    '''


