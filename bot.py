# -*- coding: utf-8 -*-

#####################################
# Name:         xmppsms             #
# Author:       free_kode           #
# Created:      22.07.2011          #
# Copyright:    (c) free_kode 2011  #
# Licence:      GNU GPL v2          #
#####################################

#!/usr/bin/env python
import xmpp,sys

iqInbox = ''
messageClientFromSms = ''

def iqIncoming(con,iq): #iq запросы которые получаем
	global iqInbox
	iqInbox = iq
	print '\nIq = ',iqInbox.getCDATA() #выводит возможный текст из iq запросов
	
def messageIncoming(con, msg): #сообщения, передаются данные сообщения, содержат все
	global botClient
	global messageClientFromSms
	global config

	messageFrom = msg.getFrom()
	messageBody = msg.getBody()
	print 'Message =',messageFrom, ':', messageBody
	
	if messageBody == '_off': #проблема в том что присылает сообщения, а не чатики, хз
		botClient.send(xmpp.Message(msg.getFrom(),'гудбай америка оооуууооо'))
		botClient.online = 0
		print 'disconnect'
	if messageBody == '_sms': #шлем смс с тестом
		messageClientFromSms = messageFrom
		smsSend(config['numberMobile'],'testing',0)
		botClient.send(xmpp.Message(messageFrom,'посмотрим, не обещаю'))
	if messageBody == '_weather': #шлем смс с погодой уже
		messageClientFromSms = messageFrom
		smsSend(config['numberMobile'],weather(0),0)
		botClient.send(xmpp.Message(messageFrom,'состояние погоды отправлено - 0'))
	if messageFrom == 'mrim.jabber.ru': #ответы все к клиенту, которые придут от этого адреса
		botClient.send(xmpp.Message(messageClientFromSms,messageBody))

def smsSend(number,smsText,translit): #функция отсыла смс, передается номер, текст, транслит
	global iqInbox

	level1 = []
	level2 = []
	level3 = []

	ses = '0'
	field0_attrs = {'type':'text-single', #формирование запроса самой смс
					'var':'number'}
	field1_attrs = {'type':'text-multi', #уровень1.1
					'var':'text'}
	field2_attrs = {'type':'boolean', #уровень1.2
					'var':'translit'}
	field_attrs_all = (field0_attrs,field1_attrs,field2_attrs)
	dataTag = (number,smsText,translit)

	i=0
	while i<=2:
		field = xmpp.Node('field',attrs=field_attrs_all[i]) #уровень1.0
		field.setTagData('value',dataTag[i]) #уровень0
		level1.append(field)
		i+=1

	nodeX_attrs = {'type':'submit'}
	nodeX = xmpp.Node('x',attrs=nodeX_attrs)
	nodeX.setNamespace(xmpp.NS_DATA)
	nodeX.setPayload(level1) #не трогать!!! работает через жопу, не знаю как
	level2.append(nodeX)

	nodeCommand_attrs = {'node':'sms',
						 'sessionid': ses}
	nodeCommand = xmpp.Node('command',attrs=nodeCommand_attrs)
	nodeCommand.setNamespace(xmpp.NS_COMMANDS)
	nodeCommand.setPayload(level2)
	level3.append(nodeCommand)  #nodeCommand последний узел 
	#перед отправкой, теперь надо сформировать запрос, а лан потом расскажу,
	#вобщем вверху поставил что массивы равны
	#так они и дальше оказались равны лол

	smsRequest = xmpp.Iq(typ='set',  to='mrim.jabber.ru')
	smsRequest.setPayload(level3)
	botClient.send(smsRequest) #отправляем смску

def weather(tod): #парсер погоды, передается время суток 0-3
	import urllib
	from lxml import etree

	weatherList = []
	weatherNames = ['','|осад=','|t=','|вл=']
	
	xmlWeather = urllib.urlopen('http://informer.gismeteo.ru/xml/99624_1.xml').read()
	tree = etree.XML(xmlWeather) # Парсинг строки
		
	nodes = tree.xpath('/MMWEATHER/REPORT/TOWN/FORECAST') #время суток
	midValue = []
	for node in nodes:
		midValue.append(int(node.values()[4]))
	weatherList.append(midValue)
		
	nodes = tree.xpath('/MMWEATHER/REPORT/TOWN/FORECAST/PHENOMENA') #осадки
	midValue = []
	for node in nodes:
		midValue.append(int(node.values()[1]))
	weatherList.append(midValue)
	
	nodesPath = [	'/MMWEATHER/REPORT/TOWN/FORECAST/TEMPERATURE', #температура
					'/MMWEATHER/REPORT/TOWN/FORECAST/RELWET',] #влажность
	i=0
	while i <= 1:
		nodes = tree.xpath(nodesPath[i])
		midValue = []
		for node in nodes:
			midValue.append((int(node.values()[0]) + int(node.values()[1]))/2)
		weatherList.append(midValue) #конечный кортеж, с 4мя параметрами, на 4время суток
		i+=1
		
	days = ['ночь','утро','день','вечер']
	j=0
	i=0
	while i<=3: #меняем цифры на название время суток
		while j<=3:
			if weatherList[0][i] == j:
				weatherList[0][i] = days[j]
				break
			j+=1
		i+=1
		
	rain = {4:'дождь',5:'ливень',6:'снег',7:'снег',8:'гроза',9:'n/a',10:'нет'}
	i=0
	j=4
	while i<=3:
		while j<=10:
			if weatherList[1][i] == j:
				weatherList[1][i] = rain[j]
				break
			j+=1
		i+=1
	
	i=0
	weatherAll = ''
	while i<=3:
		midlweath = weatherNames[i] + str(weatherList[i][tod])
		weatherAll = weatherAll + midlweath
		i+=1
	print 'weather = ', weatherAll
	return weatherAll
	
def configLoad(): #загружаются параметры из конфига
	import ConfigParser
	config = ConfigParser.ConfigParser()
	config.read('config')

	login = config.get('account0', 'login')
	password = config.get('account0', 'password')
	resource = config.get('account0', 'resource')
	number = config.get('mobile', 'number')

	return {'login':login,'password':password, 'resource':resource, 'numberMobile':number}

####основная функция логина аккаунта, в будущем должна логинить два аккаунта и более
config = configLoad()

jid = xmpp.JID(config['login'])
botClient = xmpp.Client(jid.getDomain(),debug=[])

con=botClient.connect()
if not con:
	print 'no connect!'
	sys.exit()
print 'connected with',con
auth=botClient.auth(jid.getNode(),config['password'],config['resource'])
if not auth:
	print 'no authenticate!'
	sys.exit()
print 'authenticated using',auth

botClient.sendInitPresence()
botClient.RegisterHandler('message', messageIncoming)
botClient.RegisterHandler('iq', iqIncoming)

botClient.online = 1 #0-выключение, в сообщениях указываеться как _off
while botClient.online:
	botClient.Process(1)
botClient.disconnect()
