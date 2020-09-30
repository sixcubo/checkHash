import argparse
import hashlib
import os.path
import os
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
            # 若文件已记录于#sha1.txt，检查与记录是否相同
            if records.__contains__(filename):
                # 若文件SHA1值与记录不相同，由用户决定下一步动作
                if fileSHA1 != records[filename]:
                    print('\033[31;49m', end='')    # 终端红色文字
                    print('SHA1 NOT EQULE\t' +
                          '\033[4m' + dirpath + '\\' + filename + '\033[24m')   # 终端文字下划线
                    ans = input('├─Do you konw this error?(y/n): ')
                    while ans not in ['y', 'Y', 'n', 'N']:
                        ans = input(
                            '├─invalid input. Do you konw this error?(y/n): ')
                    else:
                        if ans == 'y' or ans == 'Y':
                            records[filename] = fileSHA1
                            print('└─MODIFY #sha1.txt')
                        elif ans == 'n' or ans == 'N':
                            changes[filename] = fileSHA1
                            print('└─ADD TO #error.txt')
                    print('\033[0m', end='')
                # 若文件SHA1值与记录相同
                else:
                    print('SHA1 EQULE\t' + dirpath + '\\' + filename)
            # 若文件未记录于#sha1.txt，插入新记录
            else:
                print('ADD TO RECORDS\t' + dirpath + '\\' + filename)
                records[filename] = fileSHA1


# 扫描basedir
def scanBaseDir(basedir):
    # 遍历目录树
    for dirpath, _, filenames in os.walk(basedir):
        print('\n' + dirpath)
        sha1Rec = {}    # 存储#sha1.txt的记录
        errorRec = {}   # 存储SHA1值有变化的记录

        # 打开#sha1.txt，读取记录
        recordsFO = open(dirpath + '\\#sha1.txt', "r+")
        linesOfRecords = recordsFO.readlines()
        for line in linesOfRecords:
            line = line.split()
            sha1Rec[line[0]] = line[1]

        # 检查SHA1值
        checkSHA1(sha1Rec, errorRec, dirpath, filenames)

        # 将records写入#sha1.txt
        recordsFO.seek(0)
        for record in sha1Rec.items():
            recordsFO.write(record[0] + '\t' + record[1] + "\n")
        recordsFO.close()

        # 若存在文件SHA1值改变，将变化写入#error.txt
        if errorRec.__len__() != 0:
            changesFO = open(dirpath + '\\#error.txt', "a")
            changesFO.write(time.strftime(
                "%Y-%m-%d %H:%M:%S %a", time.localtime()) + '\n')
            for record in errorRec.items():
                changesFO.write(record[0] + '\t' + record[1] + "\n")
            changesFO.write('\n')
            changesFO.close()


# 遍历目录树，在每个目录下生成sha1.txt
def createRecords(basedir):
    for dirpath, _, __ in os.walk(basedir):
        try:
            fo = open(dirpath + '\\#sha1.txt', "x")
            print("CREATE RECORDS\t" + dirpath)
        except FileExistsError:
            print("RECORDS EXIST\t" + dirpath)
        else:
            fo.close()


def param_run(basedir):
    if not os.path.exists(basedir):
        print('Can not find this dir.')
    else:
        ans = input('Are you sure you want use dir: "' +
                    basedir + '" ?(y/n): ')
        while ans not in ['y', 'Y', 'n', 'N']:
            ans = input('├─invalid input. Use dir: "' + basedir + '" ?(y/n): ')
        else:
            if ans == 'y' or ans == 'Y':
                createRecords(basedir)
                scanBaseDir(basedir)
            elif ans == 'n' or ans == 'N':
                print('└─Quit')


def cleanLogs(cleandir):
    for dirpath, _, filenames in os.walk(cleandir):
        if '#sha1.txt' in filenames:
            filepath = dirpath + '\\#sha1.txt'
            print('delete\t' + filepath)
            os.remove(filepath)
        if '#error.txt' in filenames:
            filepath = dirpath + '\\#error.txt'
            print('delete\t' + filepath)
            os.remove(filepath)
    print('Clean "' + cleandir + '" completed')


def param_clean(cleandir):
    if not os.path.exists(cleandir):
        print('Can not find this dir.')
    else:
        ans = input('Are you sure you want use dir: "' +
                    cleandir + '" ?(y/n): ')
        while ans not in ['y', 'Y', 'n', 'N']:
            ans = input('├─invalid input. Use dir: "' +
                        cleandir + '" ?(y/n): ')
        else:
            if ans == 'y' or ans == 'Y':
                cleanLogs(cleandir)
            elif ans == 'n' or ans == 'N':
                print('└─Quit')


if "__main__" == __name__:
    # 命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', nargs='*', help='assign base paths')
    parser.add_argument('-c', '--clean', nargs='*',
                        help='rm record files in assigned dirs')
    args = parser.parse_args()

    # 若指定参数[run]
    if args.run != None:
        if args.run == []:
            basedir = os.getcwd()
            print('\nUse current dir: ' + basedir)
            param_run(basedir)
        else:
            for basedir in args.run:
                print('\nUse the dir: ' + basedir)
                param_run(basedir)
        exit()

    # 若指定参数[clean]
    if args.clean != None:
        if args.clean == []:
            cleandir = os.getcwd()
            print('\nUse current dir: ' + cleandir)
            param_clean(cleandir)
        else:
            for cleandir in args.clean:
                print('\nUse the dir: ' + cleandir)
                param_clean(cleandir)
        exit()

    # 未指定参数
    print('Please assign parameter.')
