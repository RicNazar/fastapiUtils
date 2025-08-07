#from fastapi import Depends
from app.api.excel.classes.db import Db
from app.api.excel.classes.excel import Excel

#(db: Db = Depends(get_db)):
def get_db():
    return Db()

#(excel: Excel = Depends(get_excel)):
def get_excel():
    return Excel()