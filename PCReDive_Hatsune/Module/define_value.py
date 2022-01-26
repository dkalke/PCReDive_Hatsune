import datetime
from enum import Enum


MAX_DAMAGE = 1000000000

class Period(Enum):
  UNKNOW = 0 # 未定
  DAY = 1 # 08-16
  NIGHT = 2 # 16-24
  GRAVEYARD = 3 # 00-08
  ALL = 4 # 00-24


class Knife_Type(Enum):
  NORMAL_ENTER = 0 # 正刀進刀
  RESERVED_ENTER = 1 # 補償刀進刀
  NORMAL_WAIT = 2 # 正刀卡秒完成
  RESERVED_WAIT = 3 # 正刀卡秒完成
  NORMAL = 4 # 正刀出刀完成
  ADDITIONAL = 5 # 補償出刀完成
  RESERVED = 6 # 自報補償刀數量  ##與系統脫鉤


class Stage(Enum):
  one = 1
  two = 4
  three = 11
  four = 31
  five = 41

# BOSS[week][boss] 血量  
BOSS_HP=[\
  [600,800,1000,1200,1500],\
  [600,800,1000,1200,1500],\
  [1200,1400,1700,1900,2200],\
  [1900,2000,2300,2500,2700],\
  [8500,9000,9500,10000,11000]]

for i in range(0,5):
  for j in range(0,5):
    BOSS_HP[i][j] = BOSS_HP[i][j]

# 戰隊戰日期
this_year = 2022
this_month = 1
this_day = 27
BATTLE_DAY=[\
  datetime.datetime(year=this_year, month=this_month, day=this_day, hour=5, minute=0, second=0),\
  datetime.datetime(year=this_year, month=this_month, day=this_day, hour=5, minute=0, second=0) + datetime.timedelta(days=1),\
  datetime.datetime(year=this_year, month=this_month, day=this_day, hour=5, minute=0, second=0) + datetime.timedelta(days=2),\
  datetime.datetime(year=this_year, month=this_month, day=this_day, hour=5, minute=0, second=0) + datetime.timedelta(days=3),\
  datetime.datetime(year=this_year, month=this_month, day=this_day, hour=5, minute=0, second=0) + datetime.timedelta(days=4),\
  datetime.datetime(year=this_year, month=this_month, day=this_day, hour=0, minute=0, second=0) + datetime.timedelta(days=5)]

CD_TIME = 10 # !n 的冷卻時間
NCD_TIME = 60 # !cn 的冷卻時間