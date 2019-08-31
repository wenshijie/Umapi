# -*- coding: UTF-8 -*-
# !/usr/bin/env python3

"""
Spyder Editor

This is a temporary script file.
"""

import Hnbi
import datetime

def list_diff_day(time1=None,time2=None):
	'''两个datetime.datetime的日期差'''
	if time1>time2:
		diff_day=(time1-time2).days
	else:
		diff_day=(time2-time1).days
	list_diff_day=list(range(diff_day))
	list_diff_day.sort(reverse=True)#倒序排列为了从相差最远的一天开始补数据
	return list_diff_day

def read_last_line(path='log/umeng_basic_log.txt'):
	'''读取日志文件的最后一行，用于得到最后一次写入数据成功的日期，得到字符串xxxx-xx-xx类型日期'''
	fr=open(path,'r')
	lines = fr.readlines() #读取所有行
	try:
		last_line = lines[-1]
	except :
		last_line = ''
	 #取最后一行
	return last_line[0:10]#有一个换行符共11个字符取前十个

def write_log(path='log/umeng_basic_log.txt',string=None):
	'''把写数据成功的日期写入日志'''
	fw = open(path,'a')
	fw.write(string+'\n')
	fw.close()

#当前时间
today=datetime.datetime.now()

########################################写入数据库表umeng_basic的数据并自动检测是否缺少数据然后自动补充##########################################
read_last_time=datetime.datetime.strptime(read_last_line(path='log/umeng_basic_log.txt'),'%Y-%m-%d')#上次成功写入数据的时间
#上次成功写入数据的时间与今天时间的差值列表，一般情况差值为1，列表中只有0，即下面执行今天写数据的操作。如果差值大于1则一天一天的补数据从最远的一天开始
list_diffday=list_diff_day(time1=today,time2=read_last_time)
for day in list_diffday:
#处理数据缺失，取数过程中失败，或者没有某天没有执行程序造成的缺失，情况特别少。正常情况只有day=0即只写入今天的数据，day=1写入昨天应该写入的数据，
#依次类推。如果前一天写入不成功优先写入昨天的数据（不会造成死循环如果前一天没有一条有效数据但会有一行至少add_time有值得数据写入，也会有日志）
#处理数据在写入过程中写入了一部分然后突然中止造成的数据缺失，情况极少。
#会自动删除重复的也就是删除未完成全部写入的，部分写入的数据。判断依据是mysql表中有上一次写入的数据成功日志
	result_umeng_basic=Hnbi.HNBI().getumeng_basic(day=day)#重写前一天的数据
	if result_umeng_basic==0:
		#写入成功日志即写数据成功的日期
		print('umeng_basic write success')
		add_time=(datetime.datetime.now()+datetime.timedelta(days=-day)).strftime("%Y-%m-%d")#写数据的日期mysql表里有小时分钟秒
		write_log(path='log/umeng_basic_log.txt',string=add_time)
	else:
		print('umeng_basic write error，可能是MySQL连接出错')
##############################################写入数据库表umeng_basic_acc的数据并自动处理缺失数据#########################################
read_last_time=datetime.datetime.strptime(read_last_line(path='log/umeng_basic_acc_log.txt'),'%Y-%m-%d')#上次写入数据的时间
list_diffday=list_diff_day(time1=today,time2=read_last_time)
for day in list_diffday:
	result_umeng_basic_acc=Hnbi.HNBI().getumeng_basic_acc(day=day)#默认值day=0
	if result_umeng_basic_acc==0:
		print('umeng_basic_acc write success')
		addtime=(datetime.datetime.now()+datetime.timedelta(days=-day)).strftime("%Y-%m-%d")#写数据的日期mysql表里有小时分钟秒
		write_log(path='log/umeng_basic_acc_log.txt',string=addtime)
	else:
		print('umeng_basic_acc write error，可能是MySQL连接出错')
######################################入数据库表umeng_retention数据并自动处理缺失数据####################################################
read_last_time=datetime.datetime.strptime(read_last_line(path='log/umeng_retention_log.txt'),'%Y-%m-%d')#上次写入数据的时间
list_diffday=list_diff_day(time1=today,time2=read_last_time)
for day in list_diffday:
	result_umeng_retention=Hnbi.HNBI().getumeng_retention(day=day)#默认值day=0
	if result_umeng_retention==0:
		print('umeng_retention write success')
		add_time=(datetime.datetime.now()+datetime.timedelta(days=-day)).strftime("%Y-%m-%d")#写数据的日期mysql表里有小时分钟秒
		write_log(path='log/umeng_retention_log.txt',string=add_time)
	else:
		print('umeng_retention  write error，可能是MySQL连接出错')