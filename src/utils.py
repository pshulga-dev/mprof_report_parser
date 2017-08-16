from subprocess import Popen, PIPE
import re
import csv
import os


class Executer(object):
    def __init__(self, cmd):
        self.cmd = cmd

    def __enter__(self):
        p = Popen(self.cmd, shell=False, stderr=PIPE, stdin=PIPE, stdout=PIPE)
        yield from p.communicate()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is IOError:
            print(exc_val)
            return True


class MLPD(object):

    def __init__(self, output_path, mprof_path, cache_file=None):
        self.cache_file = cache_file
        self.output_path = output_path
        self.mprof_path = mprof_path

    @staticmethod
    def create_full_list(custom_list=[], l=0):
        try:
            custom_list[l]
        except IndexError:
            for _ in range(len(custom_list), l+1):
                custom_list.append('')
        return custom_list

    def get_data(self):
        if self.cache_file is None:
            cmd = [self.mprof_path, self.output_path]
            text = ''
            with open("src.txt", "w") as src_file:
                with Executer(cmd) as ex:
                    for i in ex:
                        text += i.strip().decode()
                        src_file.write(text)
        else:
            text = open(self.cache_file).read()
        return text

    def parse_mlpd(self):
        data_list = []
        res_list_size = []
        res_list_count = []
        shot_number = 0
        unique_class_obj = set()
        data = self.get_data()
        heap_shot_list = re.split(r"Heap shot", data)
        del heap_shot_list[0:2]
        for heap_shot_item in heap_shot_list:
            try:
                shot_number = re.findall("\d+", heap_shot_item)[0]
                heap_dict = {'heap': shot_number}
            except IndexError:
                continue
            for c, line in enumerate(re.split(r"\n", heap_shot_item)[2:]):
                try:
                    line = re.split(" +", line)
                    if "Counters:" in line:
                        break
                    unique_class_obj.add(line[4])
                    heap_dict.update({'data': (line[1], line[2], line[4])})
                    data_list.append(heap_dict.copy())
                except IndexError:
                    continue

        with open('tmp.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['heap'])
            writer.writerow(['objects'])
            for obj in unique_class_obj:
                writer.writerow([obj])

        with open('tmp.csv') as csvout:
            read_file = csv.reader(csvout, delimiter=',')
            for count, row_main in enumerate(read_file):
                row_fork = row_main.copy()
                if count == 0:
                    [row_main.append(i) for i in range(int(shot_number)+1)]
                    [row_fork.append(i) for i in range(int(shot_number)+1)]
                elif count == 1:
                    [row_main.append('size Mb') for _ in range(int(shot_number)+1)]
                    [row_fork.append('count') for _ in range(int(shot_number) + 1)]
                else:
                    row_main = self.create_full_list(row_main, int(shot_number)+1)
                    row_fork = self.create_full_list(row_fork, int(shot_number)+1)
                    for iter_data in data_list:
                        if iter_data['data'][2] in row_main:
                            row_main.pop(int(iter_data['heap'])+1)
                            row_fork.pop(int(iter_data['heap'])+1)

                            row_main.insert(int(iter_data['heap'])+1, int(iter_data['data'][0])/1024/1024)
                            row_fork.insert(int(iter_data['heap']) + 1, iter_data['data'][1])
                res_list_size.append(row_main)
                res_list_count.append(row_fork)

        with open('size.csv', 'w') as csv_size:
            write_file = csv.writer(csv_size, delimiter=',', lineterminator='\n')
            for line in res_list_size:
                write_file.writerow(line)

        with open('count.csv', 'w') as csv_count:
            write_file = csv.writer(csv_count, delimiter=',', lineterminator='\n')
            for line in res_list_count:
                write_file.writerow(line)
        os.remove("tmp.csv")