from src.utils import MLPD


if __name__ == '__main__':
    output_path = "/home/pasha/dump.mlpd"
    mprof_path = "/opt/apprecovery/mono/bin/mprof-report"

    # If you don't have cache file (the third parameter) just leave empty,
    # it's will be saved in current directory in the src.txt file
    mlpd = MLPD(output_path, mprof_path)
    mlpd.parse_mlpd()
