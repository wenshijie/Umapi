# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 10:15:59 2018

@author: HN00242
"""

import Umapi
import pandas as pd
import getbasicinformation
import time
import datetime
from sqlalchemy import create_engine

class HNBI():
	"""docstring for HNBI 写入数据库hn_bi,参数为app名字以及与其对应的appkey的字典，所要写入的数据库连接"""
	#app名字和appkey 现在获取不到如下dict_app
	dict_app=getbasicinformation.getappkeyANDappname()
	def __init__(self, dict_app=dict_app,
		engine=create_engine('mysql+pymysql://*************************/emp?charset=utf8', echo=False)):
		self.dict_app = dict_app
		self.engine=engine
######################################表umeng_basic的清洗和写入自动删除重复数据（重新写入时）。更新时自动删除老数据。############
	def getumeng_basic(self,day=0):
		###获得前一天各版本各渠道的新增、活跃、启动次数
		#day=0，默认当前读取时间 day=1 重新执行昨天的任务
		add_time=(datetime.datetime.now()+datetime.timedelta(days=-day)).strftime("%Y-%m-%d %H:%M:%S")#写数据的日期 
		#请求前一天的的数据，前一天的日期
		yesterday=(datetime.datetime.now()+datetime.timedelta(days=-1-day)).strftime("%Y-%m-%d")
		#得到安卓或ios各渠道各版本新增、活跃以及启动次数
		data_umeng_basic=pd.DataFrame()
		for key,value in self.dict_app.items():
			#获取版本和渠道
			channels,versions=getbasicinformation.getchannelsANDversions(appkey=value,date=yesterday)
			versions=[None]
			data_app =pd.DataFrame()
			for channel in channels:
				for version in versions:
					data=pd.DataFrame()
					opi_parameter={'appkey':value,'startDate':yesterday,
									'endDate':yesterday,'periodType':'daily',
									'channels':channel,'versions':version}#函数参数信息
					try:#尝试请求某渠道某版本的新增、活跃、以及启动次数
						data_ActiveUsers=Umapi.API().UmengUappGetActiveUsersByChannelOrVersionRequest(opi_parameter)
						data['act_users']=data_ActiveUsers['value']
					except:#如果上面请求出错
						try:#休眠60秒，再次请求
							time.sleep(30)
							data_ActiveUsers=Umapi.API().UmengUappGetActiveUsersByChannelOrVersionRequest(opi_parameter)
							data['act_users']=data_ActiveUsers['value']
						except:#如果再次请求出错，该次请求结果为Nan
							print('UmengUappGetActiveUsersByChannelOrVersionRequest error',channel)
							data['act_users']=0
					data['daydate']=yesterday
					data['int_date']=list(map(lambda a:str(time.mktime(time.strptime(str(a), "%Y-%m-%d"))),data_ActiveUsers['date']))
					data['channel']=channel
					data['version']=version
					try:#新增
						data_NewUsers=Umapi.API().UmengUappGetNewUsersByChannelOrVersionRequest(opi_parameter)
						data['new_users']=data_NewUsers['value']
					except :
						try:
							time.sleep(30)
							data_NewUsers=Umapi.API().UmengUappGetNewUsersByChannelOrVersionRequest(opi_parameter)
							data['new_users']=data_NewUsers['value']
						except:
							print('UmengUappGetNewUsersByChannelOrVersionRequest error',channel)
							data['new_users']=0
					try:#启动次数
						data_launch=Umapi.API().UmengUappGetLaunchesByChannelOrVersionRequest(opi_parameter)
						data['launch']=data_launch['value']
					except:
						try:
							time.sleep(30)
							data_launch=Umapi.API().UmengUappGetLaunchesByChannelOrVersionRequest(opi_parameter)
							data['launch']=data_launch['value']
						except :
							print('UmengUappGetLaunchesByChannelOrVersionRequest error',channel)
							data['launch']=0
					data['app_name']=key
					data['add_time']=add_time
					data_app=data_app.append(data)
					data_app=data_app[(data_app['act_users']>0)|(data_app['new_users']>0)|(data_app['launch']>0)]
			data_umeng_basic=data_umeng_basic.append(data_app)
		data_umeng_basic=data_umeng_basic[['add_time','daydate','int_date','app_name','channel','version',
							'new_users','act_users','launch']]
		sql="DELETE FROM umeng_basic WHERE daydate='"+yesterday+"'"#如果重新写入昨天的数据，自动删除昨天的数据
		self.engine.execute(sql)
		data_umeng_basic.to_sql('umeng_basic',self.engine,if_exists='append',index=False)
		return 0
######################################表umeng_basic_acc的清洗和写入自动删除重复数据（重新写入时）。更新时自动删除老数据。############
	def getumeng_basic_acc(self,day=0):
		#day=0，默认当前读取时间 day=1 重新执行昨天的任务
		add_time=(datetime.datetime.now()+datetime.timedelta(days=-day)).strftime("%Y-%m-%d %H:%M:%S")
		list_day=[]#昨天到前15天的时间列表（日期要大于14 才会有14天的留存率更新出来）
		for i in range(2,16):
			day_i=(datetime.datetime.now()+datetime.timedelta(days=-i-day)).strftime("%Y-%m-%d")
			list_day.append(day_i)
		endDate=list_day[0]
		startDate=list_day[-1]#八天前时间
		#得到前一天安卓新增、活跃以及启动次数
		data_all=pd.DataFrame()
		for key,value in self.dict_app.items():
			data=pd.DataFrame()
			opi_parameter={'appkey':value,'startDate':startDate,
					'endDate':endDate,'periodType':'daily'}#函数参数信息
			try:#活跃用户（返回data=pd.DataFrame(message['activeUserInfo'])）
				data_ActiveUsers=Umapi.API().UmengUappGetActiveUsersRequest(opi_parameter)
			except :
				try:
					time.sleep(30)
					data_ActiveUsers=Umapi.API().UmengUappGetActiveUsersRequest(opi_parameter)
				except :
					print(key,'UmengUappGetActiveUsersRequest error',startDate,endDate)
					data_ActiveUsers=pd.DataFrame(data=list_day,columns=['date'])
					data_ActiveUsers['value']=None
			data['daydate']=data_ActiveUsers['date']
			data['active_users']=data_ActiveUsers['value']
			data['app_name']=key
			try:#新用户（返回data=pd.DataFrame(message['newUserInfo'])）
				data_NewUsers=Umapi.API().UmengUappGetNewUsersRequest(opi_parameter)
			except :
				try:
					time.sleep(30)
					data_NewUsers=Umapi.API().UmengUappGetNewUsersRequest(opi_parameter)
				except:
					print(key,'UmengUappGetNewUsersRequest error',startDate,endDate)
					data_NewUsers=pd.DataFrame()
					data_NewUsers['value']=None
			data['new_users']=data_NewUsers['value']
			try:#启动次数（返回data=pd.DataFrame(message['launchInfo'])）
				data_launch=Umapi.API().UmengUappGetLaunchesRequest(opi_parameter)
			except :
				try:
					time.sleep(30)
					data_launch=Umapi.API().UmengUappGetLaunchesRequest(opi_parameter)
				except :
					print(key,'UmengUappGetLaunchesRequest error')
					data_launch=pd.DataFrame()
					data_launch['value']=None
			data['launches']=data_launch['value']
		#得到app用户的停留时间，不区分安卓的渠道和版本
			data_Durations=pd.DataFrame()
			for date in list_day:
				data_Duration=pd.DataFrame()
				try:
					data_Duration_day=Umapi.API().UmengUappGetDurationsRequest(opi_parameter={'appkey':value,
								'date':date,'statType':'daily','channel':None,'version':None})
					data_Duration['duration_average']=data_Duration_day['average']
					data_Duration['durations']=data_Duration_day['durationInfos']
				except:
					try:
						time.sleep(30)
						data_Duration_day=Umapi.API().UmengUappGetDurationsRequest(opi_parameter={'appkey':value,
								'date':date,'statType':'daily','channel':None,'version':None})
						data_Duration['duration_average']=data_Duration_day['average']
						data_Duration['durations']=data_Duration_day['durationInfos']
					except: 
						print(key,'UmengUappGetDurationsRequest  error',date)
						data_Duration_day=pd.DataFrame([{'average':None,'durationInfos':None,'date':date}])
						data_Duration['duration_average']=data_Duration_day['average']
						data_Duration['durations']=data_Duration_day['durationInfos']
				data_Duration['date']=date
				data_Durations=data_Durations.append(data_Duration)
			data=pd.merge(data,data_Durations,how='inner',left_on='daydate',right_on='date')
			del data['date']
		#每次启动的停留时间
			time.sleep(30)#强制停止
			data_launch_Durations=pd.DataFrame()
			for date in list_day:
				data_launch_Duration=pd.DataFrame()
				try:
					data_launch_Duration_day=Umapi.API().UmengUappGetDurationsRequest(opi_parameter={'appkey':value,
								'date':date,'statType':'daily_per_launch','channel':None,'version':None})
					data_launch_Duration['durations_per_launch']=data_launch_Duration_day['durationInfos']
					data_launch_Duration['durations_per_launch_average']=data_launch_Duration_day['average']
				except:
					try:
						time.sleep(30)
						data_launch_Duration_day=Umapi.API().UmengUappGetDurationsRequest(opi_parameter={'appkey':value,
								'date':date,'statType':'daily_per_launch','channel':None,'version':None})
						data_launch_Duration['durations_per_launch']=data_launch_Duration_day['durationInfos']
						data_launch_Duration['durations_per_launch_average']=data_launch_Duration_day['average']
					except: 
						print(key,'launch_Durations UmengUappGetDurationsRequest  error',date)
						data_launch_Duration_day=pd.DataFrame([{'durationInfos':None,'average':None}])
						data_launch_Duration['durations_per_launch']=data_launch_Duration_day['durationInfos']
						data_launch_Duration['durations_per_launch_average']=data_launch_Duration_day['average']
				data_launch_Duration['date']=date
				data_launch_Durations=data_launch_Durations.append(data_launch_Duration)
			data=pd.merge(data,data_launch_Durations,how='inner',left_on='daydate',right_on='date')
			del data['date']
			try:
				data_Retentions=Umapi.API().UmengUappGetRetentionsRequest(opi_parameter={'appkey':value,'startDate':startDate,
							'endDate':endDate,'periodType':'daily','channel':None,'version':None})
				data_Retentions=data_Retentions.rename(columns={'totalInstallUser':'retention_install','retentionRate':'retention'})
				data=pd.merge(data,data_Retentions,how='left',left_on='daydate',right_on='date')
				del data['date']
			except :
				try:
					time.sleep(30)
					data_Retentions=Umapi.API().UmengUappGetRetentionsRequest(opi_parameter={'appkey':value,'startDate':startDate,
							'endDate':endDate,'periodType':'daily','channel':None,'version':None})
					data_Retentions=data_Retentions.rename(columns={'totalInstallUser':'retention_install','retentionRate':'retention'})
					data=pd.merge(data,data_Retentions,how='left',left_on='daydate',right_on='date')
					del data['date']
				except:
					print('UmengUappGetRetentionsRequest error',startDate,endDate)
					data['retention']=None
					data['retention_install']=None
			data_all=data_all.append(data)
		data_all['addtime']=add_time
		data_all['date_seg']='daily'
		data_umeng_basic_acc=data_all[['addtime','daydate','app_name','date_seg','new_users',
				'active_users','launches','durations','duration_average','durations_per_launch',
				'durations_per_launch_average','retention','retention_install']]
		data_umeng_basic_acc['durations']=data_umeng_basic_acc['durations'].astype(str)
		data_umeng_basic_acc['durations_per_launch']=data_umeng_basic_acc['durations_per_launch'].astype(str)
		data_umeng_basic_acc['retention']=data_umeng_basic_acc['retention'].astype(str)
		sql="DELETE FROM umeng_basic_acc WHERE daydate>='"+list_day[-1]+"'"
		self.engine.execute(sql)
		data_umeng_basic_acc.to_sql('umeng_basic_acc',self.engine,if_exists='append',index=False)
		return 0
#######################################表umeng_retention的清洗和写入自动删除重复数据（重新写入时）。更新时自动删除老数据。############
	def getumeng_retention(self,day=0):
		#day=0，默认当前读取时间 day=1 重新执行昨天的任务
		add_time=(datetime.datetime.now()+datetime.timedelta(days=-day)).strftime("%Y-%m-%d %H:%M:%S")#显示本地时间
		list_day=[]#昨天到前15天的时间列表（日期要大于15 才会有14天的留存率更新出来）
		for i in range(2,16):
			day_i=(datetime.datetime.now()+datetime.timedelta(days=-i-day)).strftime("%Y-%m-%d")
			list_day.append(day_i)
		endDate=list_day[0]
		startDate=list_day[-1]
		data_app_day=pd.DataFrame()
		for key,value in self.dict_app.items():
			#获得渠道与版本数
			channels,versions=getbasicinformation.getchannelsANDversions(appkey=value,date=endDate)
			versions=[None]
			for channel in channels:
				for version in versions:
					opi_parameter1={'appkey':value,'startDate':startDate,
								'endDate':endDate,'periodType':'daily',
								'channels':channel,'versions':version}#函数参数信息
					try:#各版本渠道的新增用户
						data_NewUsers=Umapi.API().UmengUappGetNewUsersByChannelOrVersionRequest(opi_parameter1)
						data_NewUsers['versions']=version
					except:
						try:
							time.sleep(30)
							data_NewUsers=Umapi.API().UmengUappGetNewUsersByChannelOrVersionRequest(opi_parameter1)
							data_NewUsers['versions']=version
						except:
							print(startDate,'-',endDate,key,channel,version,'新增获取失败')
							data_NewUsers=pd.DataFrame(data=list_day,columns=['date'])
							data_NewUsers['value']=1
							data_NewUsers['channels']=channel
							data_NewUsers['versions']=version
					opi_parameter2={'appkey':value,'startDate':startDate,
								'endDate':endDate,'periodType':'daily',
								'channel':channel,'version':version}#函数参数信息（注意坑这里参数名channel不带s，version也不带s）
					try:
						data_Retentions=Umapi.API().UmengUappGetRetentionsRequest(opi_parameter2)
						data_Retentions['versions']=version
					except :
						try:
							time.sleep(30)
							data_Retentions=Umapi.API().UmengUappGetRetentionsRequest(opi_parameter2)
							data_Retentions['versions']=version
						except :
							print(key,'UmengUappGetRetentionsRequest 留存  error',channel,version)
							data_Retentions=pd.DataFrame(data=list_day,columns=['date'])
							data_Retentions['retentionRate']=None
							data_Retentions['channels']=channel
							data_Retentions['versions']=version
							data_Retentions['totalInstallUser']=1#如果没请求到数据为1 可能被以后覆盖掉
					data=pd.merge(data_NewUsers[data_NewUsers['value']>0],data_Retentions[data_Retentions['totalInstallUser']>0]
								,how='inner',on=['date','channels','versions'])#新增大于零且下载（新设备）大于零
					data['app_name']=key
					data['add_time']=add_time
					data=data.rename(columns={'date':'daydate','channels':'channel','versions':'version',
						'value':'new_users','retentionRate':'retention_per_list'})
					data['int_date']=list(map(lambda a:str(time.mktime(time.strptime(str(a), "%Y-%m-%d"))),data['daydate']))
					data_app_day=data_app_day.append(data)
		data_umeng_retention=data_app_day[['add_time','daydate','int_date','app_name','channel','version','new_users','retention_per_list']]
		data_umeng_retention['retention_per_list']=data_umeng_retention['retention_per_list'].astype(str)
		sql="DELETE FROM umeng_retention WHERE daydate>='"+list_day[-1]+"'"
		self.engine.execute(sql)
		data_umeng_retention.to_sql('umeng_retention',self.engine,if_exists='append',index=False)
		return 0

if __name__== '__main__':
	a=HNBI().getumeng_basic()
'''
	date_start=datetime.datetime.now()
	a=HNBI().getumeng_retention()
	date_end=datetime.datetime.now()
	difftime=date_end-date_start
'''