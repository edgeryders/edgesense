def identity_map(data):
    return data

def nested_objects_map(root_name, object_name):
    def nested_map(data):
        return [d[object_name] for d in data[root_name]]
    return nested_map

methods = { 
    'identity': {
        'users':    identity_map,
        'nodes':    identity_map, 
        'comments': identity_map
    },
    'nested': {
        'users':    nested_objects_map('users', 'user'),
        'nodes':    nested_objects_map('nodes', 'node'), 
        'comments': nested_objects_map('comments', 'comment') 
    },
    
}

def is_team(user, admin_roles):
    if user.has_key('roles') and admin_roles:
        user_roles = set([e.strip() for e in user['roles'].split(",") if e.strip()])
        return len(user_roles & admin_roles)>0
    else:
        return user.has_key('roles') and user['roles']!=""
        
def extract(how, what, data):
    if methods.has_key(how) and methods[how].has_key(what):
        return methods[how][what](data)
    else:
        raise Exception("Extraction method %s / %s not implemented" % (how, what))
