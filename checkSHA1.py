import argparse
import hashlib
import os.path
import sys
import time


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
    ignoreType = ['txt', 'jpeg', 'jpg', 'png', 'mp3', 'flac', 'py']
    if filePath.split('.')[-1].lower() in ignoreType:
        print('IGNORE\t\t' + filePath)
        return True

    return False


# 检查目录下文件的SHA1值
def checkSHA1(records, changes, dirpath, filenames):
    # 检查当前目录下文件的SHA1值
    for filename in filenames:
        if not isIgnore(dirpath + '\\' + filename):
            fileSHA1 = getFileSHA1(dirpath + '\\' + filename)
            # 若文件已记录于#records.txt，检查与记录是否相同
            if records.__contains__(filename):
                # 若文件SHA1值与记录不相同，由用户决定下一步动作
                if fileSHA1 != records[filename]:
                    print('\033[31;49m', end='')
                    print('SHA1 NOT EQULE\t' +
                          '\033[4m' + dirpath + '\\' + filename + '\033[24m')
                    ans = input('├─Do you konw this change?(y/n): ')
                    while ans not in ['y', 'Y', 'n', 'N']:
                        ans = input(
                            '├─invalid input. Do you konw this change?(y/n): ')
                    else:
                        if ans == 'y' or ans == 'Y':
                            records[filename] = fileSHA1
                            print('└─MODIFY #records.txt')
                        elif ans == 'n' or ans == 'N':
                            changes[filename] = fileSHA1
                            print('└─ADD TO #changes.txt')
                    print('\033[0m', end='')
                # 若文件SHA1值与记录相同
                else:
                    print('SHA1 EQULE\t' + dirpath + '\\' + filename)
            # 若文件未记录于#records.txt，插入新记录
            else:
                print('ADD TO RECORDS\t' + dirpath + '\\' + filename)
                records[filename] = fileSHA1


# 扫描basedir
def scanBaseDir(basedir):
    # 遍历目录树
    for dirpath, dirnames, filenames in os.walk(basedir):
        print('\n' + dirpath)
        records = {}    # 存储已记录在#records.txt的文件
        changes = {}    # 存储SHA1值有变化的文件

        # 打开#records.txt，读取记录
        recordsFO = open(dirpath + '\\#records.txt', "r+")
        linesOfRecords = recordsFO.readlines()
        for line in linesOfRecords:
            line = line.split()
            records[line[0]] = line[1]

        # 检查SHA1值
        checkSHA1(records, changes, dirpath, filenames)

        # 将records写入#records.txt
        recordsFO.seek(0)
        for record in records.items():
            recordsFO.write(record[0] + '\t' + record[1] + "\n")
        recordsFO.close()

        # 若存在文件SHA1值改变，将changes写入#changes.txt
        if changes.__len__() != 0:
            changesFO = open(dirpath + '\\#changes.txt', "a")
            changesFO.write(time.strftime(
                "%Y-%m-%d %H:%M:%S %a", time.localtime()) + '\n')
            for record in changes.items():
                changesFO.write(record[0] + '\t' + record[1] + "\n")
            changesFO.write('\n')
            changesFO.close()


# 遍历目录树，在每个目录下生成SHA1.records
def createRecords(basedir):
    if not os.path.exists(basedir):
        print('Can not find this dir.')
        exit()
    else:
        for dirpath, dirnames, filenames in os.walk(basedir):
            try:
                fo = open(dirpath + '\\#records.txt', "x")
                print("CREATE RECORDS\t" + dirpath)
            except FileExistsError:
                print("RECORDS EXIST\t" + dirpath)
            else:
                fo.close()


if "__main__" == __name__:
    # 命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--basedir', help='assign base path')
    args = parser.parse_args()

    # 若为指定命令行参数，询问是否使用当前目录
    if args.basedir == None:
        ans = input('Use current dir "' + os.getcwd() + '" ?(y/n): ')
        while ans not in ['y', 'Y', 'n', 'N']:
            ans = input('├─invalid input. Use current dir?(y/n): ')
        else:
            if ans == 'y' or ans == 'Y':
                basedir = os.getcwd()
                print('└─Work in dir: ' + basedir)
            elif ans == 'n' or ans == 'N':
                print('└─Quit')
                exit()
    # 接收命令行参数
    elif args.basedir != None:
        basedir = args.basedir

    createRecords(basedir)
    scanBaseDir(basedir)
