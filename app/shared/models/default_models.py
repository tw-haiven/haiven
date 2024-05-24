class DefaultModels:
    def __init__(self, chat, vision, embeddings):
        self.chat = chat
        self.vision = vision
        self.embeddings = embeddings

    @classmethod
    def from_dict(cls, data):
        return cls(data.get("chat"), data.get("vision"), data.get("embeddings"))
