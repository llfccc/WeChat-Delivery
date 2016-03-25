# -*- coding:utf8 -*-
import time
import MySQLdb
from flask import Flask, g, request, make_response,render_template
import hashlib
import xml.etree.ElementTree as ET
app=Flask(__name__)  
app.debug=True

import sae.const
MYSQL_DB = sae.const.MYSQL_DB 
MYSQL_USER = sae.const.MYSQL_USER 
MYSQL_PASS = sae.const.MYSQL_PASS 
MYSQL_HOST_M = sae.const.MYSQL_HOST 
MYSQL_HOST_S = sae.const.MYSQL_HOST_S 
MYSQL_PORT = int(sae.const.MYSQL_PORT)

def insertMysql(data):
    conn = MySQLdb.Connection(host=MYSQL_HOST_M,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASS,db='app_datagarden')
    cur=conn.cursor()
    conn.set_character_set('utf8')
    sql="insert into kuaidi values('%s','%s','%s')" %data
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

def insertUsers(data):
    conn = MySQLdb.Connection(host=MYSQL_HOST_M,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASS,db='app_datagarden')
    conn.set_character_set('utf8')
    cur=conn.cursor()

    sql="replace into users values('%s','%s','%s','%s')" %data
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

def insertKuaidiInfo(data):
    conn = MySQLdb.Connection(host=MYSQL_HOST_M,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASS,db='app_datagarden')
    cur=conn.cursor()
    conn.set_character_set('utf8')
    sql="insert into kuaidiInfo values('%d','%s','%s',0)" %data
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    
def searchID(field,content):

    conn = MySQLdb.Connection(host=MYSQL_HOST_M,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASS,db='app_datagarden')
    cur=conn.cursor()
    conn.set_character_set('utf8')
    sql="SELECT  time,CASE WHEN users.realName is not  null THEN users.realName else kuaidi.wechatName end,department,position   FROM kuaidi LEFT JOIN users ON kuaidi.wechatName=users.wechatName  where  %s='%s' order by time desc" %(field,content)
    cur.execute(sql)
    sqlResult=cur.fetchall()
    
    sql="select * from kuaidiInfo where randomNumber=%d limit 1" %(int(content))
    cur.execute(sql)
    kuaidiInfo=cur.fetchall()
    if len(kuaidiInfo)>0:
       result="编号为%s的快件内容为'%s',打包方式为'%s',进度:\n\n" %(content,kuaidiInfo[0][1],kuaidiInfo[0][2])
    else:
       return "查询出错"
    #kuaidiInfo=((sdf,sdf))
    cur.close()
    conn.close()

    temp=''
    if sqlResult:
       for k,v in enumerate(sqlResult):
           tempTime= time.localtime(int(v[0]))
           tempTime=time.strftime('%Y-%m-%d %H:%M:%S',tempTime)
           temp="%d.登记人员为'%s',时间为%s;部门为'%s',职位为'%s'\n" %(k+1,v[1],tempTime,v[2],v[3])
           result+=temp
       return result
    else:
       return "未找到该编号的快件"

def changeFinished(content):
    conn = MySQLdb.Connection(host=MYSQL_HOST_M,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASS,db='app_datagarden')
    cur=conn.cursor()
    conn.set_character_set('utf8')
    sql=" update kuaidiInfo set finished=1 where randomNumber=%d " %(content)
    cur.execute(sql)
    cur.close()
    conn.close()    

def searchUser(field,content):
    conn = MySQLdb.Connection(host=MYSQL_HOST_M,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASS,db='app_datagarden')
    cur=conn.cursor()
    conn.set_character_set('utf8')
    sql="select time,CASE WHEN users.realName is not  null THEN users.realName else k.wechatName end,content,department,position  from (select * from (select * from ( select * from  kuaidi where content in (SELECT content  FROM kuaidi WHERE %s='%s'   GROUP BY content) ) b order by time desc) as a group by a.content order by time desc ) k  LEFT JOIN users ON k.wechatName=users.wechatName group by content  order by time  " %(field,content)
    cur.execute(sql)
    sqlResult=cur.fetchall()

    
    result="以下显示您所有未结束的登记快件的最新情况：\n\n"
    temp=''
    num=1
    if sqlResult:
        for k,v in enumerate(sqlResult):
            temp=''
            tempTime= time.localtime(int(v[0]))
            tempTime=time.strftime('%Y-%m-%d %H:%M:%S',tempTime)
            
            sql="select * from kuaidiInfo where randomNumber=%d and finished=0 limit 1" %(int(v[2]))
            cur.execute(sql)

            kuaidiInfo=cur.fetchall()

            if len(kuaidiInfo)>0:
               
               temp+="%d. 编号为%s的快件内容为 '%s' ,打包方式为 '%s' ,进度:\n\n" %(num,v[2],kuaidiInfo[0][1],kuaidiInfo[0][2])
               temp+="登记人为'%s',职位为'%s',登记时间为 %s\n\n" %(str(v[1]),v[4],tempTime)
               num+=1
            else:
                temp=''
               	#return "查询出错"
            
            
            result+=temp
        return result
    else:
        return "您还未登记过任何快件"
    cur.close()
    conn.close()

def applyID():
    conn = MySQLdb.Connection(host=MYSQL_HOST_M,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASS,db='app_datagarden')
    cur=conn.cursor()
    conn.set_character_set('utf8')
    sql=" select randomNumber from randomTable where used = 0 limit 1   "  
    cur.execute(sql)
    number=int(cur.fetchall()[0][0])
    sql=" update randomTable SET used = 1 WHERE randomNumber = %d   " %(number)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    return number 

def checkID(digitID): #检查是否已经申请过编号
    conn = MySQLdb.Connection(host=MYSQL_HOST_M,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASS,db='app_datagarden')
    cur=conn.cursor()
    conn.set_character_set('utf8')
    sql=" select randomNumber from kuaidiInfo where randomNumber= %d limit 1   "   %digitID
    cur.execute(sql)
    num=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    if len(num)>0:  #如果没查到编号，就返回0
        return num[0][0]
    else:
        return 0

@app.route('/', methods = ['GET', 'POST'] )
def wechat_auth():
    if request.method == 'GET':
        token = 'nibuzhidaowoshilelinfengba'# your token
        query = request.args  # GET 方法附上的参数
        signature = query.get('signature', '')
        timestamp = query.get('timestamp', '')
        nonce = query.get('nonce', '')
        echostr = query.get('echostr', '')
        s = [timestamp, nonce, token]
        s.sort()
        s = ''.join(s)
        if ( hashlib.sha1(s).hexdigest() == signature ):
          return make_response(echostr)
    else:
        rec = request.stream.read()
        xml_rec = ET.fromstring(rec)
        timestamp = xml_rec.find('CreateTime').text
        tou = xml_rec.find('ToUserName').text
        fromu = xml_rec.find('FromUserName').text
        content = xml_rec.find('Content').text
        if content.isdigit() and len(content)>5:
            if checkID(int(content))==int(content):
                insertMysql((int(timestamp),fromu,content)) 
                content="已登记编号为"+content+"的快递件"
            else:
                content="该编号还未被申请过,请进行新编号申请"
                
        elif content[0:1]=='c' and content[1:].isdigit():
            content=content[1:]
            content=searchID('content',content)
        elif content[0:2]=='cx':
            try:
                content=searchUser('wechatName',fromu)
            except: 	
                content="未找到任何信息"
        elif content[0:2]=='sq':
            try:
                number=applyID()   #申请一个编号，并从randomTable中标记为1，保证不给重复的数字
                filename=content.split()[1]
                packaging=content.split()[2]
                
                insertMysql((int(timestamp),fromu,number))                 
                insertKuaidiInfo((number,filename,packaging))
                
                content=u"已申请快件编号为:%d,文件内容为:%s打包方式为:%s"   %( number,filename,packaging)
            except: 	
                content="申请编号失败"
                
        elif content[0:2]=='js' and content[2:].isdigit():
            try:
                content=int(content[2:])
                if checkID(content)==content:
                    changeFinished(content)
                    content="成功结束%d号快件，以后不会出现在cx指令中" %content

            except:
                content="标记结束任务失败"
        elif content[0:2]=='dj':
            try:
                realName=content.split()[1]
                department=content.split()[2]
                position=content.split()[3]
                userData=(fromu,position,department,realName)
                insertUsers(userData)

                content=u"已登记名字:%s的部门为:%s职位为:%s" %(realName,department,position)                
            except:
                content="登记失败"
           
        else:
            content="一.警告：输入错误，快递编号位数大与等于6；\n\n二.使用距离：\n1.文件发起人输入“sq 文件内容及分数 打包方式”（例如  sq 设备审批2份 信封 ，以空格来分隔）来登记文件，其他人输入快件编号来登记。\n2.输入“c123456”来查找快递编号为123456的快件情况\n3.输入“cx”来查找你自己投递的快件.\n4.第一次使用需输入dj 名字 部门 职位 来登记信息。\n\n##如有疑问咨询 物资部-乐林峰##"

        xml_rep = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"
        response = make_response(xml_rep % (fromu,tou,str(int(time.time())), content))
        response.content_type='application/xml'
        return response
    
@app.route('/test')
def test():
    content="o8NpYxO3QTITVs8F2kWa2Ijm_nQM"
    timestamp=11111111
    fromu='sdfsdfds'
    tou='s'
    field = 'wechatName'

    conn = MySQLdb.Connection(host=MYSQL_HOST_M,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASS,db='app_datagarden')
    cur=conn.cursor()
    conn.set_character_set('utf8')
    sql="select time,CASE WHEN users.realName is not  null THEN users.realName else k.wechatName end,content,department,position  from (select * from (select * from ( select * from  kuaidi where content in (SELECT content  FROM kuaidi WHERE %s='%s'  GROUP BY content) ) b order by time desc) as a group by a.content order by time desc ) k  LEFT JOIN users ON k.wechatName=users.wechatName group by content  order by time  " %(field,content)
    cur.execute(sql)
    sqlResult=cur.fetchall()

    
    result="您登记的快件最新情况为：\n\n"
    temp=''
    if sqlResult:
        for k,v in enumerate(sqlResult):
            tempTime= time.localtime(int(v[0]))
            tempTime=time.strftime('%Y-%m-%d %H:%M:%S',tempTime)
            
            sql="select * from kuaidiInfo where randomNumber=%d limit 1" %(int(v[2]))
            cur.execute(sql)

            kuaidiInfo=cur.fetchall()

            if len(kuaidiInfo)>0:
               temp+="%d,编号为%s的快件内容为 '%s' ,打包方式为 '%s' ,进度:\n\n" %(k+1,v[2],kuaidiInfo[0][1],kuaidiInfo[0][2])
            else:
               return "查询出错"
            
            temp+="登记人为'%s',职位为'%s',登记时间为 %s\n" %(str(v[1]),v[4],tempTime)
            result+=temp
        return result
    else:
        return "您还未登记过任何快件"
    cur.close()
    conn.close()
 
    
  
    
    
