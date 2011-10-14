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

def iqIncoming(con,iq): #iq запросы которые получаем
    global iqInbox
    global botRun
    iqInbox = iq

    IqToNode = iqInbox.getTo().getNode()
    if IqToNode == 'xmppsms0':
        btId = 0
    elif IqToNode == 'xmppsms1':
        btId = 1
    else:
        print 'hm...is a bug'
        sys.exit()

    if iqInbox.getCDATA()[:3] == 'SMS':
        botRun[btId].send(xmpp.Message(messageClientFromSms,iqInbox.getCDATA(), 'chat'))

    print '\nIq = ',iqInbox.getCDATA(), ':', IqToNode #выводит возможный текст из iq запросов

def messageIncoming(con, msg): #сообщения, передаются данные сообщения, содержат все, отправлять лучше в транслите, огромное количество символов 120работает
    global botRun

    messageFrom = msg.getFrom()
    messageToNode = msg.getTo().getNode()
    messageBody = msg.getBody()

    print 'Message =', messageFrom, ':', messageBody

    if messageToNode == 'xmppsms0': #кому пришло, из ботов клиентов запущенных
        btId = 0
    elif messageToNode == 'xmppsms1':
        btId = 1
    else:
        print 'hm...it is a bug'
        sys.exit()

    stFnd = str(msg.getFrom()).find('/') #-1 - знач не нашла
    if str(msg.getFrom())[:stFnd] == configLoad(1,0)[0]: #функция проверки от кого сообщение, именно жид без ресурса
        requestMessage(btId,messageBody,messageFrom)

    #if messageFrom == 'mrim.jabber.ru': #ответы все к клиенту, которые придут от этого адреса, в такой конфигурации не работает
    #    botRun[btId].send(xmpp.Message(messageClientFromSms,messageBody, 'chat'))

def requestMessage(numClient,mesBody,mesFrom): #все все что идет из сообщений отсеянных, сюда на обработку, и отвечает есессно обратно, либо работает с смс
    global botRun #запущенные боты, номер передан при входе в функцию

    #print '0', mesBody, '1', mesFrom
    if mesBody == '_off': #все нормально, посылает чатики
        botRun[btId].send(xmpp.Message(msg.getFrom(),'гудбай америка оооуууооо', 'chat'))
        botRun[0].online = 0
        botRun[1].online = 0
        print 'disconnect'
    elif mesBody == '_sms': #шлем смс с тестом
        smsSend(config['numberMobile'],'testing',1) #120символов, транслит - ok
        botRun[numClient].send(xmpp.Message(mesFrom,'посмотрим, не обещаю', 'chat'))
    elif mesBody == '_weather': #шлем смс с погодой уже
        smsSend(config['numberMobile'],weather(0),0)
        botRun[numClient].send(xmpp.Message(mesFrom,'состояние погоды отправлено - 0', 'chat'))
    else:
        botRun[numClient].send(xmpp.Message(mesFrom,'command unknow', 'chat'))

def checkSending(): #проверяет дошло ли смс, по ответному iq, которое уповестит что не дошло
    #либо сделать функцию как обработчик сообщений iq c mrim.mail.ru
    #так же можно и с сообщениями, сделать отдельный обработчик который будет работать только с запросами mrim.mail.ru
    #судьба функции не известна...
    #ее можно встроить в функцию работы с mrim.mail.ru
    pass

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
    botRun[0].send(smsRequest) #отправляем смску

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

    nodesPath = [    '/MMWEATHER/REPORT/TOWN/FORECAST/TEMPERATURE', #температура
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

def configLoad(whatPars,numAccount): #загружаются параметры из конфига, передается номер аккаунта, который парсить, что парсить 0 - акки, 1 - админские акки
    #объединим с админскими, меньше перегружать память
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read('config')
    if whatPars == 0:
        login = config.get('account' + str(numAccount), 'login')
        password = config.get('account' + str(numAccount), 'password')
        resource = config.get('account' + str(numAccount), 'resource')
        number = config.get('mobile', 'number')
        return {'login':login,'password':password, 'resource':resource, 'numberMobile':number}
    elif whatPars == 1:
        account = []
        i=0
        #while i<=0: #нужно както сделать на неопределнное количество акккаунтов
        account.append(config.get('admin', 'user' + str(i)))
        return (account)

####основная функция логина аккаунтов
numacc = 0
botRun = []

while numacc <= 1: #цикл логина двух аккаунтов
    config = configLoad(0,numacc)
    jid = xmpp.JID(config['login'])
    bot = xmpp.Client(jid.getDomain(), debug=[])

    con=bot.connect()
    if not con:
        print 'no connect!'
        sys.exit()
    print 'connected with',con
    auth=bot.auth(jid.getNode(),config['password'],config['resource'])
    if not auth:
        print 'no authenticate!'
        sys.exit()
    print 'authenticated using',auth
    bot.sendInitPresence()
    bot.RegisterHandler('message', messageIncoming)
    bot.RegisterHandler('iq', iqIncoming)
    bot.online = 1 #та строка в конце, которая определяла работу цикла до отключения бота
    botRun.append(bot)
    numacc+=1

while botRun[0].online or botRun[1].online:
    botRun[0].Process(1)
    botRun[1].Process(1)
botRun[0].disconnect()
botRun[1].disconnect()
