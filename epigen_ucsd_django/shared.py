

def is_member(user,group):
    return user.groups.filter(name=group).exists()


