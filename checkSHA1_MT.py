
import argparse
import hashlib
import json
import os
import os.path
import threading
import time
import enum


UNSCAN = 'UNSCAN'
SCANNING = 'SCANNING'
SCANNED = 'SCANNED'
CHANGED = 'CHANGED'


class RecordElem:
    def __init__(self, fileName):
        self.fileName = fileName
        self.fileSHA1 = ''
        self.fileState = UNSCAN


class Record:
    def __init__(self, baseDir):
        self.baseDir = baseDir
        self.data = self.pruneDir(baseDir)

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

    def trans2json(self):
        data4json = {}
        for dirpath in self.getAllPath():
            data4json[dirpath] = []
            elems = self.getElems(dirpath)
            for elem in elems:
                data4json[dirpath].append(
                    {'name': elem.fileName, 'sha1': elem.fileSHA1, 'state': elem.fileState})
        return data4json

    def getAllPath(self):
        return self.data.keys()

    def getElems(self, dirpath):
        return self.data[dirpath]


class Scanner(threading.Thread):
    def __init__(self, sharedRecord):
        threading.Thread.__init__(self)
        self.sharedRec = sharedRecord

    def run(self):
        for dirpath in self.sharedRec.getAllPath():
            elems = self.sharedRec.getElems(dirpath)
            for elem in elems:
                if elem.fileState == UNSCAN:
                    elem.fileState = SCANNING
                    fileSHA1 = getFileSHA1(dirpath + '\\' + elem.fileName)
                    elem.fileSHA1 = fileSHA1
                    elem.fileState = SCANNED


class Checker:
    def __init__(self, sharedRecord):
        self.sharedRecord = sharedRecord

    def compare(self):
        jsonPath = self.sharedRecord.baseDir + '\\' + self.jsonNameWithTime()
        with open(jsonPath, 'w') as f:
            json.dump(self.sharedRecord.trans2json(), f, ensure_ascii=False,
                      sort_keys=True, indent=4, separators=(',', ':'), )

    def load(self):
        pass

    def dump(self):
        pass

    def jsonNameWithTime(self):
        return '#sha1_' + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + '.json'


# 获取文件的SHA1值
def getFileSHA1(filePath):
    with open(filePath, "rb") as fp:
        SHA1Obj = hashlib.sha1()
        SHA1Obj.update(fp.read())
        fileSHA1 = SHA1Obj.hexdigest()
        return fileSHA1


def parseCL():
    return 'D:\\testhash'


if "__main__" == __name__:
    baseDir = parseCL()

    if baseDir != None:
        sharedRec = Record(baseDir)

        # lock = threading.Lock()
        scanners = []
        threadNum = 2
        for i in range(0, threadNum):
            scanner = Scanner(sharedRec)
            scanner.start()
            scanners.append(scanner)
        for s in scanners:
            s.join()

        checker = Checker(sharedRec)
        checker.compare()

    else:
        # 未指定参数
        print('Please assign parameter.')

    # def readOldTree(self):
    #     print('============ Create JSON files ============')
    #     try:
    #         fp = open(jsonPath, "x")
    #         print("CREATE FILE:\t" + jsonPath)
    #     except FileExistsError:
    #         print("FILE EXISTED:\t" + jsonPath)
    #     else:
    #         fp.close()

    # def compare(self):
    #     jsonPath = self.sharedRec.baseDir + '\\' + SHA1_JSON

    #     print('============ Compare files SHA1 ============')
    #     fp = open(jsonPath, 'r+')
    #     try:
    #         old_tree = json.load(fp)
    #     except json.decoder.JSONDecodeError:
    #         old_tree = {}
    #     new_tree = self.sharedRec.tree

    #     # 比较两棵树
    #     for dirpath in new_tree:
    #         new_files = new_tree[dirpath]
    #         old_files = old_tree[dirpath]

    #     fp.close()
