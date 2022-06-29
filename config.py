from configparser import ConfigParser

def config(filename = r"D:\amritanshu\OneDrive - Infosys Limited\VB code\Python Code\connect.ini", section = 'postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db ={}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception("Section {} not found in file {}".format(section, filename))
    return db