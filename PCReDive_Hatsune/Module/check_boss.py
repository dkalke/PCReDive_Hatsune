import datetime
import Module.get_closest_end_time
import Module.define_value
import Module.week_stage

def Check_boss(connection, message, server_id, week, boss):
  # 範圍檢測
  if boss > 0 and boss < 6 :  
    # 血量檢測
    # 取得當前日期區間
    now_time = datetime.datetime.now()
    end_time = Module.get_closest_end_time.get_closest_end_time(now_time)
    start_time = end_time - datetime.timedelta(days=1)

    # 計算已結算正刀數量
    cursor = connection.cursor(prepared = True)
    sql = "\
      SELECT SUM(damage) FROM princess_connect_hatsune.knifes \
      WHERE server_id = ? \
      AND type = ? \
      AND type = ? \
      AND week = ? \
      AND boss = ? \
      AND update_time >= ? \
      AND update_time < ? \
    "
    data = (server_id, Module.define_value.Knife_Type.NORMAL.value, Module.define_value.Knife_Type.ADDITIONAL.value, week, boss, start_time, end_time)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    cursor.close()
    if row[0]:
      if int(row[0]) < Module.define_value.BOSS_HP[Module.week_stage.week_stage(week)][boss-1]:
        return True
      else:
        return False
    else:
      return True # 沒這隻王的紀錄，肯定Pass
      