""" Maps the tweet user into the requires data structure (the same as that used by the
    network script.)
    For each mentioned user the creation timestamp is the timestamp of the earliest
    tweet we see that has is present.
"""
def add_user(users_map,user_id,screen_name,created_ts):
    link = "https://twitter.com/%(n)s" % {'n': screen_name}
    user = {
        'uid': user_id,
        'created': created_ts,
        'name': screen_name,
        'link': link
    }
    if not(users_map.has_key(user_id)) or created_ts <= users_map[user_id]['created']:
        users_map[user_id] = user
    
""" We consider each user that has been mentioned (not only the mentioning users)
"""
def extract_users(tweets):
    users_map = {}
    
    for tweet in tweets:
        add_user(users_map, tweet['user_id'], tweet['screen_name'], tweet['created_ts'])
        for mention in tweet['user_mentions']:
            add_user(users_map, mention['user_id'], mention['screen_name'], tweet['created_ts'])
            
    return users_map.values()
    
""" Maps the tweet user into the required data structure for the nodes (used by the
    network script.)
    For each mentioned user the creation timestamp is the timestamp of the earliest
    tweet we see that has is present and the text is the tweet text.
    The node id is equal to the user id.
"""
def add_node(nodes_map,user_id,screen_name,created_ts,text):
    node = {
        'nid': user_id,
        'uid': user_id,
        'created': created_ts,
        'title': text
    }
    if not(nodes_map.has_key(user_id)) or created_ts <= nodes_map[user_id]['created']:
        nodes_map[user_id] = node

""" We consider for each user the earliest tweet where he was mentioned or their earliest tweet
"""
def extract_nodes(tweets):
    nodes_map = {}
    
    for tweet in tweets:
        add_node(nodes_map, tweet['user_id'], tweet['screen_name'], tweet['created_ts'], tweet['text'])
        for mention in tweet['user_mentions']:
            add_node(nodes_map, mention['user_id'], mention['screen_name'], tweet['created_ts'], tweet['text'])
            
    return nodes_map.values()
    
""" We consider each tweet a comment towards all the mentioned users
"""
def extract_comments(tweets):
    comments = []
    comment_id = 1
    
    for tweet in tweets:
        for mention in tweet['user_mentions']:
            comments.append({
                "cid": comment_id,
                "nid": mention['user_id'],
                "uid": tweet['user_id'],
                "created": tweet['created_ts'],
                "comment": tweet['text']
            })
            comment_id += 1
            
    return comments