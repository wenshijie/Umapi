# -*- coding: utf-8 -*-
# !/usr/bin/env python3

"""
Created on Thu Aug 16 10:32:30 2018

@author: HN00242
"""
'''获得版本和渠道,获取app名字和appkey'''
import Umapi
import pandas as pd
#请求得到手机appname与appkey返回字典如{'手机惠农-安卓':'52254b8a56240be8db048933','手机惠农-ios':'55b9851be0f55a59cb0052fc'}
def getappkeyANDappname():
	try:
		totalpage,page,data=Umapi.API().UmengUappGetAppListRequest()
	except :
		try:
			time.sleep(70)
			totalpage,page,data=Umapi.API().UmengUappGetAppListRequest()
		except:
			print('请求APP失败')
	data_appname_appkey=pd.DataFrame()
	for i in range(1,totalpage+1):
		try:
			totalpage,page,data=Umapi.API().UmengUappGetAppListRequest(opi_parameter={'page':str(i)})
		except:
			try:
				time.sleep(70)
				totalpage,page,data=Umapi.API().UmengUappGetAppListRequest(opi_parameter={'page':str(i)})
			except:
				print('请求APP失败')
		data_appname_appkey=data_appname_appkey.append(data)
	dict_appname_appkey=data_appname_appkey.set_index('name').T.to_dict('records')[0]
	return dict_appname_appkey

#利用appkey获得某天的各版本和app渠道，返回版本列表与渠道列表，如channels=['应用市场-vivo','应用市场-小米','应用市场-应用宝CPD']
def getchannelsANDversions(appkey=None,date=None):
	try:

		versions_data=Umapi.API().UmengUappGetVersionDataRequest(opi_parameter={'appkey':appkey, 'date':date})
	except:
		try:
			time.sleep(70)
			versions_data=Umapi.API().UmengUappGetVersionDataRequest(opi_parameter={'appkey':appkey, 'date':date})
		except:
			print('请求版本数据失败')
	versions=list(versions_data['version'])
	#获取渠道
	try:
		totalpage,page,data=Umapi.API().UmengUappGetChannelDataRequest(opi_parameter={'appkey':appkey, 'date':date})
	except :
		try:
			time.sleep(70)
			totalpage,page,data=Umapi.API().UmengUappGetChannelDataRequest(opi_parameter={'appkey':appkey, 'date':date})
		except:
			print('请求渠道数据页码失败')
	channels_data=pd.Series()
	for i in range(1,totalpage+1):
		try:
			totalpage,page,data=Umapi.API().UmengUappGetChannelDataRequest(opi_parameter={'appkey':appkey, 'date':date,'page':str(i)})
		except:
			try:
				time.sleep(70)
				totalpage,page,data=Umapi.API().UmengUappGetChannelDataRequest(opi_parameter={'appkey':appkey, 'date':date,'page':str(i)})
			except:
				print('{}第{}页的10个渠道数据请求失败'.format(opi_parameter['date'],opi_parameter['page']))
		channels_data=channels_data.append(data['channel'])
	channels=list(channels_data)
	return channels,versions