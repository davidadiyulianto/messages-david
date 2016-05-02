import psycopg2 as ps
import getpass as gp
import numpy as np
import pandas as pd
import datetime
import time
import csv
import sys
import getpass
TKPD_DB_CORE = {"name":"tokopedia-db","ip":"192.168.1.206"}
TKPD_DB_ORDER = {"name":"tokopedia-order","ip":"192.168.17.22"}
TKPD_DB_BACKEND ={"name":"tokopedia-backend","ip":"192.168.1.99"}
TKPD_DB_USER = {"name":"tokopedia-user","ip":"192.168.17.25"}
KAI_PRODUCTION = {"name":"kai","ip":"52.74.38.109"}
TKPD_DB_MESSAGE = {"name":"tokopedia-message", "ip":"192.168.1.81"}

DBUSER = raw_input("db username: ")
PASSWORD = getpass.getpass("db password: ")
master_DB = TKPD_DB_CORE

def get_whole_data(query="",DB=master_DB,convert_dict=True,user=DBUSER,dbpass=PASSWORD, port_used=5432):
    conn = ps.connect("dbname=%s host=%s user=%s password=%s port=%i" % (DB["name"], DB["ip"], user, dbpass, port_used))
    dbCursor = conn.cursor()
    result=[]
    
    dbCursor = conn.cursor()
    try:
        dbCursor.execute(query)
    except ps.Error, e:
        print(e.pgerror)
        pass
    struct = dbCursor.description
    result = dbCursor.fetchall()
    
    
    
    if(convert_dict):
        result = pd.DataFrame(result)
        col_names = []
        for col in xrange(len(struct)):
            col_names.append(struct[col].name)

        result.columns = col_names
    
    return result

def get_data(query="",DB=master_DB,many=0,batch=100,max_failed=5,convert_dict=False,start=0,log = False):
    conn = ps.connect("dbname ='%s' host='%s' user='%s' password='%s'" % (DB["name"], DB["ip"], DBUSER, PASSWORD))
    dbCursor = conn.cursor()
    dbCursor.execute(query+' limit 1')
    struct = dbCursor.description
    start_point = start
    end_point = start_point+batch
    still_trying = True
    result=[]
    how_many_failed = 0
    max_offset = many+start_point
    data_amount=0
    while still_trying:
        try :
            dbCursor = conn.cursor()
            dbCursor.execute(query+' limit '+(str(batch) if many==0 else (str(many%batch if many%batch!=0 else batch) if ((data_amount+batch)>=many) else str(batch)))+' offset '+str(start_point))
            temp_result = dbCursor.fetchall()
            if log==True:
                print "get_data batch ke-"+str(data_amount/batch)+" selesai"
            data_amount += len(temp_result)
            result = result+temp_result
            start_point += batch
            end_point += batch
            if many==0:
                if len(temp_result)<batch:
                    still_trying = False
            else :
                if many <= data_amount:
                    still_trying = False

        except :
            print "masuk except get"
            conn = ps.connect("dbname ='%s' host='%s' user='%s' password='%s'" % (DB["name"], DB["ip"], DBUSER, PASSWORD))
            start_point += batch
            end_point += batch
            dbCursor = conn.cursor()
            how_many_failed+=1
            if how_many_failed>max_failed:
                still_trying=False
    if(convert_dict==True):
        for hit in range(0,len(result)):
            temp = result[hit]
            tempresult = {}
            for hit1 in range(0,len(temp)):
                tempresult.update({struct[hit1].name:temp[hit1]}) 
                result[hit]=tempresult 
    return result

def head_table(table="",DB=master_DB):
    return pd.DataFrame(get_data(query="select * from "+table,DB=DB,many=5,batch=100,max_failed=5,convert_dict=True))

def get_struct_table(table="",DB=master_DB, port_used=5432):
    conn = ps.connect("dbname=%s host=%s user=%s password=%s port=%i" % (DB["name"], DB["ip"], user, dbpass, port_used))
    dbCursor = conn.cursor()
    dbCursor.execute("select * from "+table+' limit 1')
    struct = dbCursor.description
    return [data.name for data in struct]

def get_all_tables(DB=master_DB, user=DBUSER, dbpass=PASSWORD, port_used=5432):
    conn = ps.connect("dbname=%s host=%s user=%s password=%s port=%i" % (DB["name"], DB["ip"], user, dbpass, port_used))
    dbCursor = conn.cursor()
    dbCursor.execute("select * from information_schema.tables")
    get_data = dbCursor.fetchall()
    return [data[2] for data in get_data if data[1]=='public']

def print_data(query="",DB=master_DB,many=0,batch=10000,micro_batch = 100,max_failed=5,path='path',extension='.csv',log=True,micro_log=True):
    start_point = 0
    end_point = start_point+batch
    still_trying = True
    result=[]
    how_many_failed = 0
    many_data=0
    while still_trying:
        try :
            how_many = (batch if many==0 else (batch if start_point+batch<many else (many%batch if many%batch!=0 else batch)))
            temp_result = get_data(query=query,DB=DB,many=how_many,batch=micro_batch,start=start_point,convert_dict=True)
            if log ==True:
                print "print_data batch ke-"+str(many_data)+" selesai"
            pd.DataFrame(temp_result).to_csv(path+"_"+str(many_data)+extension)
            start_point += batch
            end_point += batch
            many_data+=1
            if many==0:
                if len(temp_result)<batch:
                    still_trying = False
            else :
                if many <= start_point:
                    still_trying = False
        except :
            start_point += batch
            end_point += batch
            print "masuk except print"
            how_many_failed+=1
            if how_many_failed>max_failed:
                still_trying=False