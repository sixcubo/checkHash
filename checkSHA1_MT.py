import argparse
import hashlib
import json
import os
import os.path
import threading
import time
import deepdiff


UNSCAN = 'UNSCAN'
SCANNING = 'SCANNING'
SCANNED = 'SCANNED'


class RecordElem:
    def __init__(self, fileName, fileSHA1='', fileLock=UNSCAN):
        self.fileName = fileName
        self.fileSHA1 = fileSHA1
        self.fileLock = fileLock
        # self.fileState = fileState


class Record:
    def __init__(self):
        self.baseDir = ''
        self.data = {}

    @classmethod
    def byFiles(cls, baseDir):
        inst = cls()
        inst.baseDir = baseDir
        inst.data = inst.pruneDir(baseDir)
        return inst

    # 对目录树进行剪枝
    def pruneDir(self, baseDir):
        tree = {}
        IGNORE_TYPE = ['jpeg', 'jpg', 'png', 'mp3', 'flac', 'json', 'py']

        for dirpath, dirnames, filenames in os.walk(baseDir):
            if '#ignore' in filenames:
                # 忽略此文件夹及子文件夹
                dirnames[:] = []
            else:
                tree[dirpath] = []
                for filename in filenames:
                    if filename.split('.')[-1].lower() not in IGNORE_TYPE:
                        tree[dirpath].append(RecordElem(filename))
        return tree

    def getAllPath(self):
        return self.data.keys()

    def getElems(self, dirpath):
        return self.data[dirpath]

    # 将Record类转换为能存储在Json中的对象
    def convert2json(self):
        jsonData = {}
        for dirpath in self.getAllPath():
            jsonData[dirpath] = []
            elems = self.getElems(dirpath)
            for elem in elems:
                try:
                    elem.__dict__.pop('fileLock')
                except KeyError:
                    pass
                jsonData[dirpath].append(elem.__dict__)
        return jsonData


class Scanner(threading.Thread):
    def __init__(self, sharedRecord):
        threading.Thread.__init__(self)
        self.sharedRec = sharedRecord

    def run(self):
        for dirpath in self.sharedRec.getAllPath():
            elems = self.sharedRec.getElems(dirpath)
            for elem in elems:
                lock.acquire()
                if elem.fileLock == UNSCAN:
                    elem.fileLock = SCANNING
                    lock.release()
                    print(self.name + '\t' + dirpath + '\\' + elem.fileName)

                    fileSHA1 = self.getFileSHA1(dirpath + '\\' + elem.fileName)
                    elem.fileSHA1 = fileSHA1
                    elem.fileLock = SCANNED
                else:
                    lock.release()

    # 获取文件的SHA1值
    def getFileSHA1(self, filePath):
        with open(filePath, "rb") as fp:
            SHA1Obj = hashlib.sha1()
            SHA1Obj.update(fp.read())
            fileSHA1 = SHA1Obj.hexdigest()
            return fileSHA1


class Checker:
    def __init__(self, sharedRecord):
        self.sharedRecord = sharedRecord

    def createNewJson(self):
        newJsonPath = self.sharedRecord.baseDir + \
            '\\' + self.nameWithTime('#sha1_.json')
        with open(newJsonPath, 'w') as f:
            json.dump(self.sharedRecord.convert2json(), f, ensure_ascii=False,
                      sort_keys=True, indent=4, separators=(',', ':'))

    def compare(self):
        cnt = self.sharedRecord.convert2json()
        past = self.getPastJsonData()

        diff = deepdiff.DeepDiff(cnt, past)
        if diff == {} or past == {}:
            print('无差异')
        else:
            newChangePath = self.sharedRecord.baseDir + \
                '\\' + self.nameWithTime('#change_.json')
            with open(newChangePath, 'w') as f:
                json.dump(diff, f, ensure_ascii=False, sort_keys=True,
                          indent=4, separators=(',', ':'))

    def nameWithTime(self, name):
        prefix, suffix = name.split('.')
        return prefix + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + '.' + suffix

    def getPastJsonData(self):
        data = {}

        filenames = os.listdir(self.sharedRecord.baseDir)
        jsons = [filename for filename in filenames if filename.find(
            '#sha1_', 0, 6) == 0]
        if len(jsons) != 0:
            jsons.sort()
            latestJsonPath = self.sharedRecord.baseDir + '\\' + jsons.pop()
            with open(latestJsonPath, 'r') as fp:
                try:
                    data = json.load(fp)
                except json.decoder.JSONDecodeError:
                    print('读取json文件出错, json文件为空')
                except TypeError:
                    print('读取json文件出错, 文件数据缺失')
        elif jsons.count == 0:
            pass

        return data


def process(rootPath, threadNum):
    sharedRec = Record.byFiles(rootPath)

    time_start = time.time()

    scanners = []
    for i in range(0, threadNum):
        scanner = Scanner(sharedRec)
        scanner.start()
        scanners.append(scanner)
    for s in scanners:
        s.join()

    time_end = time.time()
    print('time cost: ', time_end-time_start, 's')

    checker = Checker(sharedRec)
    checker.compare()
    checker.createNewJson()


if "__main__" == __name__:
    lock = threading.Lock()
    threadNum = 2   # 默认双线程

    # 命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', nargs='*', help='assign the paths')
    parser.add_argument('-t', '--thread', help='assign the thread number')
    args = parser.parse_args()

    if args.thread != None:
        threadNum = int(args.thread)

    if args.run != None:
        if args.run == []:
            # 若 -r 后没有指定路径, 使用当前路径
            rootPath = os.getcwd()
            print('\033[31;49m', end='')    # 红色终端文字
            ans = input('\nUse current path: "' + rootPath + '" ?(y/n): ')
            print('\033[0m', end='')
            if ans == 'y' or ans == 'Y':
                process(rootPath, threadNum)
            else:
                print('Skip.')
            print('Finish.')
        else:
            # 依次取出 -r 后的路径
            for rootPath in args.run:
                print('\033[31;49m', end='')    # 红色终端文字
                ans = input('\nUse the path: "' + rootPath + '" ?(y/n): ')
                print('\033[0m', end='')
                if ans == 'y' or ans == 'Y':
                    process(rootPath, threadNum)
                else:
                    print('Skip.')
            print('Finish.')

    if args.run == None and args.thread == None:
        print("""
        A tool to help you quickly check the files hash value.
        You can use the command -r to run.
        """)