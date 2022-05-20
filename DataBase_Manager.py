from ast import Str
import sqlite3

class UserData(object):
    db = sqlite3
    conn = sqlite3.Connection
    def OpenDataFile(self,ls):
        self.conn = self.db.connect(ls,check_same_thread=False)
    
    def Initialization(self): #打开数据库后再用
        db_cmd = '''CREATE TABLE IF NOT EXISTS "User_Info" (
                    "User_ID" INTEGER NOT NULL PRIMARY KEY,
                    "User_Name" TEXT,
                    "Last_Node_ID" INTEGER,
                    "Last_Message_Time" BIGINT
                    );

                    CREATE UNIQUE INDEX IF NOT EXISTS "User_ID"
                    ON "User_Info" (
                    "User_ID" ASC
                    );

                    CREATE TABLE IF NOT EXISTS "Message_Queue" (
                    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "User_ID" INTEGER NOT NULL,
                    "Send_Content" TEXT,
                    "Options_A" TEXT,
                    "Options_B" TEXT,
                    "Send_Time" BIGINT NOT NULL
                    );

                    CREATE UNIQUE INDEX IF NOT EXISTS "ID"
                    ON "Message_Queue" (
                    "User_ID" ASC,
                    "ID" ASC
                    );
                    '''
        self.conn.executescript(db_cmd)
        self.conn.commit()

    def Commit_Transaction(self):
        self.conn.commit()

    def Close(self):
        self.conn.close()
    #///////////////////////////////////////////////

    def Queue_QueryByTime(self,time):
        db_cmd = 'SELECT * FROM Message_Queue where Send_Time<'+ str(time) +' ORDER BY Send_Time ASC' #Send_Time 按ASC算法排列导出
        return(self.conn.execute(db_cmd))
        # for row in cur:
        #     print(row[0])
    
    def Queue_DeleteByTime(self,time):
        #注意：判定必须小于当前时间（与Queue_QueryByTime同步），防止误删除
        db_cmd = 'DELETE FROM Message_Queue where Send_Time<'+ str(time)
        self.conn.execute(db_cmd)

    def Queue_DeleteByUserID(self,User_ID):
        #注意：判定必须小于当前时间（与Queue_QueryByTime同步），防止误删除
        db_cmd = 'DELETE FROM Message_Queue where User_ID<'+ str(User_ID)
        self.conn.execute(db_cmd)

    def Queue_Add(self,User_ID,Send_Content,Options_A,Options_B,Send_Time):
        value = (User_ID,Send_Content,Options_A,Options_B,Send_Time)
        db_cmd = "INSERT INTO Message_Queue (User_ID,Send_Content,Options_A,Options_B,Send_Time) VALUES (?,?,?,?,?)"
        self.conn.execute(db_cmd,value)

    def Queue_WaitTime_Sub(self,User_ID,Sub_Time):
        db_cmd = "UPDATE Message_Queue SET Send_Time = CASE WHEN Send_Time < 1 THEN 0 ELSE Send_Time - " + str(Sub_Time) + " END WHERE User_ID = " + str(User_ID)
        self.conn.execute(db_cmd)

    def Queue_QueryWaitTimeByUserID(self,User_ID):
        db_cmd = 'SELECT * FROM Message_Queue where User_ID='+ str(User_ID) +' ORDER BY Send_Time ASC' #Send_Time 按ASC算法排列导出
        row = self.conn.execute(db_cmd).fetchone()
        if(row == None):
            return(0)
        else:
             return(row[5])
        # for row in cur:
        #     print(row[0])
    #///////////////////////////////////////////////

    def Info_AC(self,User_ID,User_Name,Last_Node_ID,Last_Message_Time):
        #无则增，有则改 需要ID字段的话用 insert into ... on conflict do update set ...
        #反正我是懒得改回来了
        value = (User_ID,User_Name,Last_Node_ID,Last_Message_Time)
        db_cmd = "REPLACE INTO User_Info (User_ID,User_Name,Last_Node_ID,Last_Message_Time) VALUES (?,?,?,?)"
        self.conn.execute(db_cmd,value)

    def Info_QueryLNDByUserID(self,User_ID):
        db_cmd = 'SELECT Last_Node_ID FROM User_Info where User_ID='+ str(User_ID)
        row = self.conn.execute(db_cmd).fetchone()
        if(row == None):
            return(0)
        else:
            return(row[0])

    def Info_GetInt(self):
        db_cmd = 'SELECT COUNT(*) FROM User_Info'
        return(self.conn.execute(db_cmd).fetchone()[0])
    


class Story(object):
    db = sqlite3
    conn = sqlite3.Connection
    def OpenDataFile(self,ls):
        self.conn = self.db.connect(ls,check_same_thread=False)
        # 注意：WaitTime字段是本行文字所需等待时间
        # Story表：
        # CREATE TABLE "Story" (
        # "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        # "Node_ID" INTEGER NOT NULL,
        # "Node_Content" TEXT NOT NULL,
        # "Options_A" TEXT,
        # "Options_B" TEXT,
        # "Options_A_Jump_ID" INTEGER,
        # "Options_B_Jump_ID" INTEGER,
        # "WaitTime" DATETIME
        # );

        # CREATE UNIQUE INDEX "Node_ID"
        # ON "Story" (
        # "Node_ID" ASC
        # );

    def Close(self):
        self.conn.close()

    def QueryStoryByNodeID(self,Node_ID):
        db_cmd = 'SELECT Node_Content,Options_A,Options_B,Options_A_Jump_ID,Options_B_Jump_ID,WaitTime FROM Story where Node_ID='+ str(Node_ID)
        return(self.conn.execute(db_cmd).fetchone()) #row

    def QueryNodeIDByContent(self,Node_Content):
        db_cmd = "SELECT Node_ID FROM Story where Node_Content=?;"
        row = self.conn.execute(db_cmd,([Node_Content])).fetchone()
        if(row == None):
            return('0')
        else:return(row[0]) 
#///////////////////////////////////////////////

# if __name__ == '__main__':
#     ud = UserData()
#     ud.OpenDataFile(ls='/home/bxv/Desktop/Userdata.db')
#     ud.Initialization()
#     ud.Info_QueryNodeIDByUserID(1)