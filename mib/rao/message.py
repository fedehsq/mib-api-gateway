
class Message():
    """
    It is not a model, it is only a lightweight class used
    to represents a message.
    """

    # All fields of message
    id = None
    sender = None
    receiver = None
    body = None
    photo = None
    timestamp = None
    draft = None
    scheduled = None
    sent = 0
    read = 0
    bold = None
    italic = None
    underline = None

    SERIALIZE_LIST = ['id', 'sender', 'receiver', 'body', 'photo', 'timestamp',\
             'draft', 'scheduled', 'sent', 'read', 'bold', 'italic',\
             'underline']

    @staticmethod
    def build_from_json(json: dict):
        kw = {key: json[key] for key in ['id', 'sender', 'receiver', 'body', 'photo', 'timestamp',\
             'draft', 'scheduled', 'sent', 'read', 'bold', 'italic',\
             'underline']}
        return Message(**kw)

    def serialize(self):
            return dict([(k, self.__getattribute__(k)) for k in self.SERIALIZE_LIST])        

    def __init__(self, **kw):
        if kw == {}:
            return
        self.id = kw["id"]
        self.sender = kw["sender"]
        self.receiver = kw["receiver"]
        self.body = kw["body"]
        self.photo = kw["photo"]
        self.timestamp = kw["timestamp"]
        self.draft = kw["draft"]
        self.scheduled = kw["scheduled"]
        self.sent = kw["sent"]
        self.read = kw["read"]
        self.bold = kw["bold"]
        self.italic = kw["italic"]
        self.underline = kw["underline"]

    def get_id(self):
        return self.id

    def __getattr__(self, item):
        if item in self.__dict__:
            return self[item]
        else:
            raise AttributeError('Attribute %s does not exist' % item)

    def __str__(self):
        s = 'Message Object\n'
        for (key, value) in self.__dict__.items():
            s += "%s=%s\n" % (key, value)
        return s