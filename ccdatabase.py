import sqlite3
from pathlib import Path

class CCDatabase():
    connection = None
    
    def __init__(self, path):
        self.connection = self.connect(path)
    
    def connect(self, db):
        dbFile = Path(db)
        if not dbFile.is_file():
            raise FileNotFoundError
        conn = sqlite3.connect(db)
        return conn
    
    def __del__(self):
        if self.connection != None:
            self.connection.close()

    def executeAndFetchOne(self, query, params):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def executeAndFetchAll(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def getAllBugs(self):
        #TODO: Include current version of file as filter
        #TODO: Ignore bugs marked as false-positive or intentional
        return self.executeAndFetchAll("SELECT id,detection_status FROM reports WHERE detection_status IN ('new', 'unresolved', 'reopened')")
    
    def getAllReports(self):
        return self.executeAndFetchAll("SELECT id FROM reports")

    def getBugData(self, bugId):
        params = (bugId,)
        bugData = self.executeAndFetch("SELECT bpe.line_begin, bpe.col_begin, bpe.line_end, bpe.col_end, f.filepath FROM bug_path_events bpe JOIN files f ON bpe.file_id=f.id WHERE bpe.report_id=? ORDER BY bpe.`order` DESC LIMIT 1", params)
        versionData = self.executeAndFetch("SELECT rh.version_tag FROM reports rp JOIN runs rn ON rp.run_id=rn.id JOIN run_histories rh ON rn.id=rh.run_id WHERE rp.id=? ORDER BY rh.time DESC LIMIT 1", params)
        allBugData = [bugData[0], bugData[1], bugData[2], bugData[3], bugData[4], versionData[0]]
        #TODO: Make bugData a class
        return allBugData
