from src.utils import MLPDParser
import configparser


def get_config():
    global cache_file, output_path, mprof_path

    cp = configparser.ConfigParser()
    cp.read_file(open('parser.conf'))
    config = dict(cp.items("main"))
    cache_file = config.get('cache_file')
    output_path = config.get('output_path')
    mprof_path = config.get('mprof_path')


if __name__ == '__main__':
    get_config()
    # If you don't have cache file (the third parameter) just leave empty,
    # it's will be saved in current directory in the src.txt file
    mlpd = MLPDParser(output_path, mprof_path, cache_file)
    mlpd.parse_mlpd()
