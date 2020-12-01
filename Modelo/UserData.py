class UserData:
    nick = None
    jogger = None
    collector = None
    backpaker = None
    totalxp = None

    def __str__(self):
        txt = "{"
        txt += "Nick " + str(self.nick)
        txt += ", Jogger " + str(self.jogger)
        txt += ", Collector " + str(self.collector)
        txt += ", Backpaker " + str(self.backpaker)
        txt += ", TotalXP " + str(self.totalxp)
        txt += " }"

        return txt

    def getDict(self):
        dict = {}
        dict["nick"] = self.nick
        dict["jogger"] = self.jogger
        dict["collector"] = self.collector
        dict["backpaker"] = self.backpaker
        dict["totalxp"] = self.totalxp

        """
        Para eliminar valores nulos
        filtered = {k: v for k, v in dict.items() if v is not None}
        dict.clear()
        dict.update(filtered)"""

        return dict