# Check Hash

批量检查文件 hash 值的小工具, 运行程序可以快速找出 hash 值发生变化的文件.  

*checkSHA1.py* 为单线程版, 已弃用.   
*checkSHA1_MT.py* 为修改后的多线程版, 对代码进行重构, 运行速度更快:  
* 使用多线程编写, 可以同时处理多个文件, 通过加锁实现线程隔离，避免读取到错误的状态;
* oop, 对代码进行封装, 逻辑明确;
* 使用 Json 存储数据, 方便查看.


## 使用说明
运行需要 Python3 以上, 运行前需安装 deepdiff,  
`$ pip install deepdiff`

* 运行程序需要使用参数 `-r` 或 `--run` 指定目录路径, 可以一次性指定任意数量的目录, 比如   
`$ python checkSHA1_MT.py -r D:\\test1 D:\\test2`  
若不指定路径则使用当前路径, 比如  
`$ python checkSHA1_MT.py -r`  
> 如果路径中含有反斜杠 `\` , 注意避免产生转义字符.

* 可以使用参数 `-t` 或 `-thread` 指定线程数, 默认为 2. 

* 如果要忽略某个文件夹及其所有子文件夹, 在此文件夹下新建一个名为 *#ignore* 的文件, 程序会自动忽略.  

* 程序产生的数据文件命名为 *#sha1_<date_time>.json* 和 *#change_<date_time>.json* , 存储于指定的目录下.

## 程序逻辑
程序运行后, 根据指定的目录路径计算出目录下文件的 hash 值, 然后读取上次的计算结果进行比较:  
* 若无差异直接存储本次结果, 命名为 *#sha1_<date_time>.json* ;  
* 若有差异, 存储本次结果和差异, 分别命名为 *#sha1_<date_time>.json* 和 *#change_<date_time>.json* .