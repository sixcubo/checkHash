import hashlib
import os.path
import sys
import time

recordsName = 'SHA1.records'
changeRecordsName = 'SHA1_change.records'


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
    ignoreType = ['records', 'jpeg', 'jpg', 'png', 'mp3', 'flac', 'py']
    if filePath.split('.')[-1].lower() in ignoreType:
        print('IGNORE\t\t' + filePath)
        return True

    return False


# 检查目录树下文件的SHA1值
def checkRecords(basepath):
    # 遍历目录树
    for dirpath, dirnames, filenames in os.walk(basepath):
        print('\n' + dirpath)

        changeRecords = {}  # 记录SHA1值有变化的文件

        # 打开 .records，读取记录
        records = {}
        recordsFile = open(dirpath + '\\' + recordsName, "r+")
        linesOfRecords = recordsFile.readlines()
        for line in linesOfRecords:
            line = line.split()
            records[line[0]] = line[1]

        # 检查当前目录下文件的SHA1值
        for filename in filenames:
            if not isIgnore(dirpath + '\\' + filename):
                fileSHA1 = getFileSHA1(dirpath + '\\' + filename)
                # 若文件已记录于 .records，检查与记录是否相同
                if records.__contains__(filename):
                    # 若文件SHA1值与记录不相同，由用户决定下一步动作
                    if fileSHA1 != records[filename]:
                        print('*SHA1 NOT EQULE\t' + dirpath + '\\' + filename)
                        ans = input(' ├──Do you konw this change?(y/n): ')
                        while ans not in ['y', 'Y', 'n', 'N']:
                            ans = input(' ├──invalid input. Do you konw this change?(y/n): ')
                        else:
                            if ans == 'y' or ans == 'Y':
                                records[filename] = fileSHA1
                                print(' └──MODIFY SHA1.records')
                            elif ans == 'n' or ans == 'N':
                                changeRecords[filename] = fileSHA1
                                print(' └──ADD TO SHA1_change.records')
                    # 若文件SHA1值与记录相同
                    else:
                        print('SHA1 EQULE\t' + dirpath + '\\' + filename)
                # 若文件未记录于 .records，插入记录
                else:
                    print('ADD TO RECORDS\t' + dirpath + '\\' + filename)
                    records[filename] = fileSHA1

        # 写入 SHA1.records
        recordsFile.seek(0)
        for record in records.items():
            recordsFile.write(record[0] + '\t' + record[1] + "\n")
        recordsFile.close()

        # 若存在文件SHA1值改变，写入 SHA1_change.records
        if changeRecords.__len__() != 0:
            changeRecordsFile = open(dirpath + '\\' + changeRecordsName, "a")
            changeRecordsFile.write(time.strftime("%Y-%m-%d %H:%M:%S %a", time.localtime()) + '\n')
            for record in changeRecords.items():
                changeRecordsFile.write(record[0] + '\t' + record[1] + "\t\n")
            changeRecordsFile.write('\n')
            changeRecordsFile.close()


# 遍历目录树，在每个目录下生成 .records
def createRecords(basepath):
    for dirpath, dirnames, filenames in os.walk(basepath):
        try:
            fp = open(dirpath + '\\' + recordsName, "x")
            print("RECORDS CREATE\t" + dirpath + '\\' + recordsName)
        except FileExistsError:
            print("RECORDS EXIST\t" + dirpath + '\\' + recordsName)
        else:
            fp.close()


if "__main__" == __name__:
    # basepath = sys.argv[1]
    # basepath = input('Input basepath: ')
    basepath = 'D:\\testhash'
    createRecords(basepath)
    checkRecords(basepath)
