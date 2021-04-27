def main():
    fich = "type_ranking_DB.txt"
    #fich = "../Config/ExperienciaPorNivel.csv"
    try:
        f = open(fich, "r")

        for line in f:
            parseLine(line)
            # parseLineEXP(line)
    except Exception as e:
        print(e)


def parseLine(line):
    # #<typerank>
    #     <id>5</id>
    #     <name>breeder</name>
    #     <description>Eggs Hatched</description>
    #     <text>Breeder</text>
    # </typerank>
    value = line.split(",")
    id = value[0]
    name = value[1].strip('"')
    description = value[2].rstrip('\n').strip('"')
    name_txt = ""

    if (len(value[1].split("_")) > 1):
        for word in value[1].split("_"):
            name_txt += word.strip('"').capitalize() + " "
    else:
        name_txt = str(value[1].strip('"')).capitalize()

    # print("name: %s, name_txt: %s" % (name, name_txt))
    print("<typerank>")
    print("    <id>%s</id>" % (id))
    print("    <name>%s</name>" % (name))
    print("    <description>%s</description>" % (description))
    print("    <text>%s</text>" % (str(name_txt)))
    print("</typerank>")
    return None


def parseLineEXP(line):
    # #<row>
    #     <level>5</level>
    #     <exptoup>1234</exptoup>
    #     <totalxp>1235</totalxp>
    # </row>

    value = line.split(",")
    level = value[0]
    exptoup = value[1]
    totalxp = value[2].rstrip('\n')

    # print("name: %s, name_txt: %s" % (name, name_txt))
    print("<row>")
    print("    <level>%s</level>" % level)
    print("    <exptoup>%s</exptoup>" % exptoup)
    print("    <totalxp>%s</totalxp>" % totalxp)
    print("</row>")
    return None


if __name__ == '__main__':
    main()
