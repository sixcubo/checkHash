import hashlib
import sys
import os.path

recordsName = r"SHA1.records"

def getFileMD5(filePath):
    with open(filePath, "rb") as fp:
        md5obj = hashlib.md5()
        md5obj.update(fp.read())
        fileMD5 = md5obj.hexdigest()
        return fileMD5


# 获取文件的SHA1值
def getFileSHA1(filePath):
    with open(filePath, "rb") as fp:
        SHA1Obj = hashlib.sha1()
        SHA1Obj.update(fp.read())
        fileSHA1 = SHA1Obj.hexdigest()
        return fileSHA1


def isIgnore(filePath):
    fileType = ['records', 'jpeg', 'png' ,'jpg' ]
    if filePath.split('.')[-1] in fileType:
        print('IGNORE\t\t' + filePath)
        return True

    return False


# 检查目录树下文件的SHA1值
def checkRecords(basepath):
    # 遍历目录树
    for dirpath, dirnames, filenames in os.walk(basepath):
        # 打开records
        with open(dirpath + '\\' + recordsName, "r+") as fp:
            # 读取records中的文件名和SHA1值
            records = fp.readlines()
            flienNameOfRecord = []
            flienSHA1OfRecord = []
            for i in range(len(records)):
                records[i] = records[i].split('\t')
                flienNameOfRecord.insert(i, records[i][0])
                flienSHA1OfRecord.insert(i, records[i][1])

            # 遍历当前目录
            for filename in filenames:
                if not isIgnore(dirpath + "\\" + filename):
                    fileSHA1 = getFileSHA1(dirpath + "\\" + filename)
                    # 若文件已存在于records，检查与记录是否相同
                    if filename in flienNameOfRecord:
                        idx = flienNameOfRecord.index(filename)
                        if fileSHA1 == flienSHA1OfRecord[idx]:
                            print('SHA1 EQULE\t' + dirpath + '\\' + filename)
                        else:
                            print('SHA1 NOT EQULE\t' + dirpath + '\\' + filename)
                            flienSHA1OfRecord[idx] = fileSHA1
                    # 若文件不存在于records，插入记录
                    else:
                        print('SHA1 not exist\t' + dirpath + '\\' + filename)
                        flienNameOfRecord.insert(len(flienNameOfRecord), filename)
                        flienSHA1OfRecord.insert(len(flienSHA1OfRecord), fileSHA1)

            # 写入记录
            fp.seek(0)
            for i in range(len(flienNameOfRecord)):
                fp.write(flienNameOfRecord[i] + '\t' + flienSHA1OfRecord[i] + "\t\n")


# 遍历目录树，在每个目录下生成records
def createRecords(basepath):
    for dirpath, dirnames, filenames in os.walk(basepath):
        try:
            fp = open(dirpath + '\\' + recordsName, "x")
        except FileExistsError:
            print("RECORDS EXIST\t" + dirpath + '\\' + recordsName)
        else:
            fp.close()


if "__main__" == __name__:
    # basepath = sys.argv[1]
    # basepath = input('Input basepath: ')
    basepath = 'D:/testhash'
    createRecords(basepath)
    checkRecords(basepath)
