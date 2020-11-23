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
