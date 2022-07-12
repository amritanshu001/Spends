from configparser import ConfigParser
import os

def config(filename = 'connect.ini', section = 'postgresql'):

    cur_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(cur_path)
    
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