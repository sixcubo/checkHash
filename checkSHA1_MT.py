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

# NORMAL = 'NORMAL'
# CHANGED = 'CHANGED'


class RecordElem(dict):
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
                elem.__dict__.pop('fileLock')
                jsonData[dirpath].append(elem.__dict__)
        return jsonData

    @classmethod
    def convert2obj(cls, jsonData):
        objData = {}
        for dirpath in jsonData:
            objData[dirpath] = []
            elems = jsonData[dirpath]
            for elem in elems:
                objData[dirpath].append(RecordElem(
                    elem['fileName'], elem['fileSHA1']))
        return objData


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

                    fileSHA1 = getFileSHA1(dirpath + '\\' + elem.fileName)
                    elem.fileSHA1 = fileSHA1
                    elem.fileLock = SCANNED
                else:
                    lock.release()


class Checker:
    def __init__(self, sharedRecord):
        self.sharedRecord = sharedRecord

    def createNewJson(self):
        newJsonPath = self.sharedRecord.baseDir + '\\' + self.jsonNameWithTime()
        with open(newJsonPath, 'w') as f:
            json.dump(self.sharedRecord.convert2json(), f, ensure_ascii=False,
                      sort_keys=True, indent=4, separators=(',', ':'))

    def compare(self):
        cnt = self.sharedRecord.data
        pre = {}

        latestJsonPath = self.sharedRecord.baseDir + '\\' + self.getLatestJson()
        with open(latestJsonPath, 'r') as fp:
            try:
                jsonData = json.load(fp)
                pre = Record.convert2obj(jsonData)
            except json.decoder.JSONDecodeError:
                print('读取json文件出错, json文件为空')
            except TypeError:
                print('读取json文件出错, 文件数据缺失')

    def jsonNameWithTime(self):
        return '#sha1_' + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + '.json'

    def getLatestJson(self):
        filenames = os.listdir(self.sharedRecord.baseDir)
        jsons = [filename for filename in filenames if filename.find(
            '#sha1_', 0, 6) == 0]
        jsons.sort()
        return jsons.pop()


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
        sharedRec = Record.byFiles(baseDir)
        lock = threading.Lock()

        scanners = []
        threadNum = 2
        for i in range(0, threadNum):
            scanner = Scanner(sharedRec)
            scanner.start()
            scanners.append(scanner)
        for s in scanners:
            s.join()

        checker = Checker(sharedRec)
        checker.createNewJson()
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
