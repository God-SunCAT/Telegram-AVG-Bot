from pickle import FALSE
import time
import sys
import threading
from wsgiref.util import request_uri
import DataBase_Manager
from telegram import Bot,ReplyKeyboardMarkup,Update
from telegram.ext import Updater,CommandHandler,MessageHandler,Filters

Token = ''
Message_Send_Bool = True
Message_Deal_Bool = True
Administration_ID = 0 #管理员ID

def Message_deal(update, context):
    # now = time.time()
    global Message_Deal_Bool,Administration_ID
    if(Message_Deal_Bool == False and update.message.from_user.id != Administration_ID):return()
    AC_Bool = False
    #if(update.message.from_user.id != Administration_ID):return()#测试专用
    match update.message.text:
        case '/start':
            row = ['','','','']
            i = 0
            ud.Queue_DeleteByUserID(update.message.from_user.id)
            STime = update.message.date.timestamp()
            while(row[1] == '' or row[1] == None): #row[1]:Options_A
                if(row[3] != '' and row[3] != None):i = row[3]
                else:i = i + 1
                row = story.QueryStoryByNodeID(i)
                if(row[0] != ''):
                    STime = STime + row[5]
                    ud.Queue_Add(update.message.from_user.id,row[0],row[1],row[2],STime)
                else:
                    break
            ud.Info_AC(update.message.from_user.id,update.message.from_user.username,i,int(update.message.date.timestamp()))
        case '/deal_start':
            if(update.message.from_user.id == Administration_ID):
                Message_Deal_Bool = True
                update.message.reply_text(text='Message deal state:True',protect_content=True,timeout=20)
            else:
                update.message.delete()
        case '/deal_suspend':
            if(update.message.from_user.id == Administration_ID):
                Message_Deal_Bool = False
                update.message.reply_text(text='Message deal state:False',protect_content=True,timeout=20)
                ud.Commit_Transaction()
            else:
                update.message.delete()
        case '/stop_service':
            if(update.message.from_user.id == Administration_ID):
                update.message.reply_text(text='Has stoped..',protect_content=True,timeout=20)
                Message_Send_Bool = False #可以先关闭接收...
                Message_Deal_Bool = False
                ud.Commit_Transaction()
                sys.exit(0)
            else:
                update.message.delete()
        case '/save_data':
            if(update.message.from_user.id == Administration_ID):
                update.message.reply_text(text='Has saved..',protect_content=True,timeout=20)
                ud.Commit_Transaction()
            else:
                update.message.delete()
        case '/jump_wait':
            # if(update.message.from_user.id == Administration_ID):
                update.message.delete()
                ud.Queue_WaitTime_Sub(update.message.from_user.id,ud.Queue_QueryWaitTimeByUserID(update.message.from_user.id))
            # else:
                # update.message.delete()
        case '/get_user_int':
            if(update.message.from_user.id == Administration_ID):
                update.message.reply_text(text='Current number of users:' + str(ud.Info_GetInt()),protect_content=True,timeout=20)
            else:
                update.message.delete()
        case _:
            if(update.message.text[:13] == '/backtracking'):#回溯
                row = ['','','','']
                STime = update.message.date.timestamp()
                i = int(story.QueryNodeIDByContent(update.message.text[14:]))# /backtracking 剧本
                if(i==0):
                    ud.Queue_Add(update.message.from_user.id,"次元引擎回溯失败:未知..","None","None",STime)
                    return()
                LND = ud.Info_QueryLNDByUserID(update.message.from_user.id)
                if(LND >= 1 and LND<1164):#S2
                    mi = i-0
                    LND = LND-0
                if(LND >= 1164 and LND<1342):#E2
                    mi = i-1163
                    LND = LND-1163
                if(LND >= 1342):#S3
                    mi = i-1341
                    LND = LND-1341
                if(mi >= LND):
                    ud.Queue_Add(update.message.from_user.id,"次元引擎回溯失败..","None","None",STime)
                else:
                    i=i-1
                    while(row[1] == '' or row[1] == None): #row[1]:Options_A
                        if(row[3] != '' and row[3] != None):i = row[3]
                        else:i = i + 1
                        row = story.QueryStoryByNodeID(i)
                        if(row[0] != ''):
                            STime = STime + row[5]
                            ud.Queue_Add(update.message.from_user.id,row[0],row[1],row[2],STime)
                        else:
                            break
                    ud.Info_AC(update.message.from_user.id,update.message.from_user.username,i,int(update.message.date.timestamp()))
            elif(update.message.text[:10] == '/set_story'):
                row = ['','','','']
                match update.message.text[11:]:
                    case 'S2':
                        i = 1-1
                    case 'E2':
                        i = 1164-1
                    case 'S3':
                        i = 1342-1
                STime = update.message.date.timestamp()
                while(row[1] == '' or row[1] == None): #row[1]:Options_A
                    if(row[3] != '' and row[3] != None):i = row[3]
                    else:i = i + 1
                    row = story.QueryStoryByNodeID(i)
                    if(row[0] != ''):
                        STime = STime + row[5]
                        ud.Queue_Add(update.message.from_user.id,row[0],row[1],row[2],STime)
                    else:
                        break
                ud.Info_AC(update.message.from_user.id,update.message.from_user.username,i,int(update.message.date.timestamp()))
            else:
                LND = ud.Info_QueryLNDByUserID(update.message.from_user.id)
                STime = update.message.date.timestamp()
                if(LND != 0):
                    row = story.QueryStoryByNodeID(LND)
                    if(update.message.text == row[1]):#row[3]:Options_A_Jump_ID
                        i = row[3]
                        row = ['','','','']
                        while(row[1] == '' or row[1] == None): #row[1]:Options_A
                            row = story.QueryStoryByNodeID(i)
                            if(row[0] != ''):
                                STime = STime + row[5]
                                ud.Queue_Add(update.message.from_user.id,row[0],row[1],row[2],STime)
                                if((row[1] == '' or row[1] == None) and (row[3] != '' and row[3] != None)):i = row[3] #这个判断是给选项为空,无条件跳转用的
                                else:i = i + 1
                            else:
                                AC_Bool = True
                                break
                        if(AC_Bool==False):ud.Info_AC(update.message.from_user.id,update.message.from_user.username,i-1,int(update.message.date.timestamp()))
                    elif(update.message.text == row[2]):#row[4]:Options_B_Jump_ID
                        i = row[4]
                        row = ['','','','']
                        while(row[1] == '' or row[1] == None): #row[1]:Options_A
                            row = story.QueryStoryByNodeID(i)
                            if(row[0] != ''):
                                STime = STime + row[5]
                                ud.Queue_Add(update.message.from_user.id,row[0],row[1],row[2],STime) #这个判断是给选项为空,无条件跳转用的
                                if((row[1] == '' or row[1] == None) and (row[3] != '' and row[3] != None)):i = row[3]
                                else:i = i + 1
                            else:
                                AC_Bool = True
                                break
                        if(AC_Bool==False):ud.Info_AC(update.message.from_user.id,update.message.from_user.username,i-1,int(update.message.date.timestamp()))
                    else:
                        update.message.delete()

    
class Message_Send(threading.Thread):
    def run(self):
        MSBI = 0
        print("-->MSGD Threading Runing...")
        while(Message_Send_Bool):
            now = time.time()
            cur = ud.Queue_QueryByTime(now)
            for row in cur:
                try:
                    if(row[3] == '' or row[3] == None or row[3] == 'None'):#none字符串是写入的锅(就这样)
                        bot.send_message(chat_id=int(row[1]),text=row[2],protect_content=True,timeout=20)
                    else:
                        bot.send_message(chat_id=int(row[1]),text=row[2],reply_markup = ReplyKeyboardMarkup([[str(row[3])],[str(row[4])]],resize_keyboard=True,one_time_keyboard=True),protect_content=True,timeout=20)
                except:
                    ud.Queue_Add(row[1],row[2],row[3],row[4],int(row[5])+1) #防止timeout错误
            ud.Queue_DeleteByTime(now)
            time.sleep(1)
            MSBI = MSBI +1
            if(MSBI > 600):
                ud.Commit_Transaction()#定时保存 5分钟一次
        print("-->MSGD Threading Stop...")





if __name__ == '__main__':
    #///////////////////////////////////////////////
    Token = 'TgBot的token'
    Self_Base_url = '基于CF的反向代理地址,如果不是部署于国内可以无视'
    #///////////////////////////////////////////////
    patch_ = './Userdata.db'
    ud = DataBase_Manager.UserData()
    story = DataBase_Manager.Story()
    story.OpenDataFile(ls=patch_)
    ud.OpenDataFile(ls=patch_)
    print("-->"+patch_)
    ud.Initialization()
    #///////////////////////////////////////////////
    bot = Bot(token=Token,base_url=Self_Base_url)
    updater = Updater(token=Token,base_url=Self_Base_url)
    dispatcher = updater.dispatcher
    #///////////////////////////////////////////////
    # dispatcher.add_handler(CommandHandler('start',Command_Start),1)
    dispatcher.add_handler(MessageHandler(Filters.text,Message_deal),2)
    Message_Send().start()
    updater.start_polling()
    print("-->Starting....")
    while(True):
        data = input()
        match data:
            case "save":
                ud.Commit_Transaction()
                print("-->Has Saved..")
            case "stop":
                Message_Send_Bool = False
                updater.idle()
                updater.stop()
                ud.Commit_Transaction()
                print("-->Has stoped")
                sys.exit(0)
    #updater.idle()
    #updater.stop()


#CF worker:Self_Base_url
# const whitelist = [""];
# const tg_host = "api.telegram.org";
 
# addEventListener('fetch', event => {
#     event.respondWith(handleRequest(event.request))
# })
 
# function validate(path) {
#     for (var i = 0; i < whitelist.length; i++) {
#         if (path.startsWith(whitelist[i]))
#             return true;
#     }
#     return false;
# }
 
# async function handleRequest(request) {
#     var u = new URL(request.url);
#     u.host = tg_host;
#     if (!validate(u.pathname))
#         return new Response('Unauthorized', {
#             status: 403
#         });
#     var req = new Request(u, {
#         method: request.method,
#         headers: request.headers,
#         body: request.body
#     });
#     const result = await fetch(req);
#     return result;
# }



    
