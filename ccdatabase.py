import sqlite3
from pathlib import Path
from entities import BugData

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

    def executeAndFetchAll(self, query, params = None):
        cursor = self.connection.cursor()
        if params == None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        return cursor.fetchall()

    def getAllBugs(self):
        return self.executeAndFetchAll("SELECT r.id, r.detection_status, r.bug_id FROM reports r LEFT JOIN review_statuses rs ON r.bug_id = rs.bug_hash WHERE r.detection_status IN ('new', 'unresolved', 'reopened') AND rs.status IN (NULL, 'confirmed')")
    
    def getAllReports(self):
        return self.executeAndFetchAll("SELECT id FROM reports")
    
    def getBugData(self, bugId):
        params = (bugId,)
        bugData = self.executeAndFetchOne("SELECT bpe.line_begin, bpe.col_begin, bpe.line_end, bpe.col_end, f.filepath FROM bug_path_events bpe JOIN files f ON bpe.file_id=f.id WHERE bpe.report_id=? ORDER BY bpe.`order` DESC LIMIT 1", params)
        checkerData = self.executeAndFetchOne("SELECT checker_id, detection_status, checker_message, line, bug_id FROM reports WHERE id=? LIMIT 1", params)
        params2 = (checkerData[4],)
        reviewData = self.executeAndFetchOne("SELECT status FROM review_statuses WHERE bug_hash=? LIMIT 1", params2)
        allBugData = BugData(bugData[0], bugData[2], bugData[4], checkerData[0], checkerData[1], checkerData[2], checkerData[3], reviewData)
        return allBugData
    
    def getNotResolvedBugData(self, bugId):
        bugData = self.getBugData(bugId)
        if bugData is not None and bugData.getStatus() not in ['new', 'unresolved', 'reopened']:
            return None
        if bugData is not None and bugData.getReviewStatus() not in ['unreviewed', 'confirmed']:
            return None
        return bugData

    def getAllBugsForChecker(self, checker):
        params = (checker,)
        return self.executeAndFetchAll("SELECT r.id, r.detection_status, r.file_id FROM reports r LEFT JOIN review_statuses rs ON r.bug_id = rs.bug_hash WHERE r.checker_id=? AND r.detection_status IN ('new', 'unresolved', 'reopened') AND rs.status IN (NULL, 'confirmed')", params)
    
    def getFileData(self, filename):
        params = (filename,)
        return self.executeAndFetchAll("SELECT id, filepath, filename FROM files WHERE filename=?", params)
