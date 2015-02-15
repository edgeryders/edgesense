"""

Contains code adapted from: jwzthreading.py [Copyright (c) 2003-2010, A.M. Kuchling.]
which implements an algorithm for threading mail messages, as described 
at http://www.jwz.org/doc/threading.html.

This code is under a BSD-style license;

"""

import re
from email.utils import parsedate_tz, mktime_tz
from collections import deque

__all__ = ['Message', 'thread']

def uniq(alist):
    set = {}
    return [set.setdefault(e,e) for e in alist if e not in set.keys()]

sender_addr_regexp = re.compile('([^\(\)]+ at [^\(\)]+)\s*')
sender_name_regexp = re.compile('\((.*)\)')
msgid_regexp = re.compile('<([^>]+)>')
restrip_regexp = re.compile("""(
  (Re(\[\d+\])?:) | (\[ [^]]+ \])
\s*)+
""", re.I | re.VERBOSE)

class Container:
    """Contains a tree of messages.

    Instance attributes:
      .message : Message
        Message corresponding to this tree node.  This can be None,
        if a Message-Id is referenced but no message with the ID is
        included.

      .children : [Container]
        Possibly-empty list of child containers.

      .parent : Container
        Parent container; may be None.
    """

    #__slots__ = ['message', 'parent', 'children', 'id']
    def __init__ (self):
        self.message = self.parent = None
        self.children = []

    def __repr__ (self):
        return '<%s %x: %r>' % (self.__class__.__name__, id(self),
                                self.message)

    def is_dummy (self):
        return self.message is None

    def add_child (self, child):
        if child.parent:
            child.parent.remove_child(child)
        self.children.append(child)
        child.parent = self

    def remove_child (self, child):
        self.children.remove(child)
        child.parent = None

    def has_descendant (self, ctr):
        """(Container): bool

        Returns true if 'ctr' is a descendant of this Container.
        """
        # To avoid recursing indefinitely, we'll do a depth-first search;
        # 'seen' tracks the containers we've already seen, and 'stack'
        # is a deque containing containers that we need to look at.
        stack = deque()
        stack.append(self)
        seen = set()
        while stack:
            node = stack.pop()
            if node is ctr:
                return True
            seen.add(node)
            for child in node.children:
                if child not in seen:
                    stack.append(child)
        return False
    
class Message (object):
    """Represents a message to be threaded.

    Instance attributes:
    .sender_address : str
      The email address of the sender
    .sender_name: str
      The name of the sender
    .created: int
      The UTC timestamp (epoch) for the message
    .subject : str
      Subject line of the message.
    .message_id : str
      Message ID as retrieved from the Message-ID header.
    .references : [str]
      List of message IDs from the In-Reply-To and References headers.

    """
    __slots__ = ['sender_address', 'sender_name', 'created', 'subject', 'message_id', 'references']

    def __init__(self, msg=None):
        self.message_id = None
        self.references = []
        self.subject = None
        self.sender_address = None
        self.sender_name = None
        self.created = None
        
        # read the sender data
        m = sender_addr_regexp.search(msg.get('From'))
        if m:
            self.sender_address = m.group(1).strip().lower()
        else:
            self.sender_address = msg.get('From').lower()

        m = sender_name_regexp.search(msg.get('From'))
        if m:
            self.sender_name = m.group(1).strip()
        
        # read the message timestamp
        self.created = int(mktime_tz(parsedate_tz(msg.get('Date'))))
        
        # Set the message id
        m = msgid_regexp.search(msg.get("Message-ID", ""))
        if m is None:
            raise ValueError("Message does not contain a Message-ID: header")

        self.message_id = m.group(1)

        # Get list of unique message IDs from the References: header
        refs = msg.get("References", "")
        self.references = msgid_regexp.findall(refs)
        self.references = uniq(self.references)
        self.subject = msg.get('Subject', "No subject")

        # Get In-Reply-To: header and add it to references
        in_reply_to = msg.get("In-Reply-To", "")
        m = msgid_regexp.search(in_reply_to)
        if m:
            msg_id = m.group(1)
            if msg_id not in self.references:
                self.references.append(msg_id)

    def __repr__ (self):
        return '<%s: %r>' % (self.__class__.__name__, self.message_id)

def prune_container (container):
    """(container:Container) : [Container]
    Recursively prune a tree of containers, as described in step 4
    of the algorithm.  Returns a list of the children that should replace
    this container.
    """

    # Prune children, assembling a new list of children
    new_children = []
    for ctr in container.children[:]:
        L = prune_container(ctr)
        new_children.extend(L)
        container.remove_child(ctr)

    for c in new_children:
        container.add_child(c)

    if (container.message is None and
        len(container.children) == 0):
        # 4.A: nuke empty containers
        return []
    elif (container.message is None and
          (len(container.children)==1 or
           container.parent is not None)):
        # 4.B: promote children
        L = container.children[:]
        for c in L:
            container.remove_child(c)
        return L
    else:
        # Leave this node in place
        return [container]


def thread (msglist):
    """([Message]) : {string:Container}

    The main threading function.  This takes a list of Message
    objects, and returns a dictionary mapping subjects to Containers.
    Containers are trees, with the .children attribute containing a
    list of subtrees, so callers can then sort children by date or
    poster or whatever.
    """

    id_table = {}
    for msg in msglist:
        # 1A
        this_container = id_table.get(msg.message_id, None)
        if this_container is not None:
            this_container.message = msg
        else:
            this_container = Container()
            this_container.message = msg
            id_table[msg.message_id] = this_container

        # 1B
        prev = None
        for ref in msg.references:
            container = id_table.get(ref, None)
            if container is None:
                container = Container()
                container.message_id = ref
                id_table[ref] = container

            if prev is not None:
                #If they are already linked, don't change the existing links.
                if container.parent!=None:
                    pass
                # Don't add link if it would create a loop
                elif container is this_container or container.has_descendant(prev) or prev.has_descendant(container):
                    pass
                else:
                    prev.add_child(container)

            prev = container

        #1C
        if prev is not None:
            prev.add_child(this_container)
        else:
            if(this_container.parent):
                this_container.parent.remove_child(this_container)

    # 2. Find root set
    root_set = [container for container in id_table.values()
                if container.parent is None]

    # 3. Delete id_table
    del id_table

    # 4. Prune empty containers
    for container in root_set:
        assert container.parent == None

    new_root_set = []
    for container in root_set:
        L = prune_container(container)
        new_root_set.extend(L)

    root_set = new_root_set

    # 5. Group root set by subject
    subject_table = {}
    for container in root_set:
        if container.message:
            subj = container.message.subject
        else:
            c = container.children[0]
            subj = container.children[0].message.subject

        subj = restrip_regexp.sub('', subj)
        if subj == "":
            continue

        existing = subject_table.get(subj, None)
        if (existing is None or
            (existing.message is not None and
             container.message is None) or
            (existing.message is not None and
             container.message is not None and
             len(existing.message.subject) > len(container.message.subject))):
            subject_table[subj] = container

    # 5C
    for container in root_set:
        if container.message:
            subj = container.message.subject
        else:
            subj = container.children[0].message.subject

        subj = restrip_regexp.sub('', subj)
        ctr = subject_table.get(subj)
        if ctr is None or ctr is container:
            continue
        if ctr.is_dummy() and container.is_dummy():
            for c in ctr.children:
                container.add_child(c)
        elif ctr.is_dummy() or container.is_dummy():
            if ctr.is_dummy():
                ctr.add_child(container)
            else:
                container.add_child(ctr)
        elif len(ctr.message.subject) < len(container.message.subject):
            # ctr has fewer levels of 're:' headers
            ctr.add_child(container)
        elif len(ctr.message.subject) > len(container.message.subject):
            # container has fewer levels of 're:' headers
            container.add_child(ctr)
        else:
            new = Container()
            new.add_child(ctr)
            new.add_child(container)
            subject_table[subj] = new

    return subject_table
