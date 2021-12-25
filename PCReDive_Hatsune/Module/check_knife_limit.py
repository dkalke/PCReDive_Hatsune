import datetime
import Module.get_closest_end_time
import Module.define_value
async def check_knife_limit(connection, message, server_id, member_id): # main_week, week
  # 取得當前日期區間
  now_time = datetime.datetime.now()
  end_time = Module.get_closest_end_time.get_closest_end_time(now_time)
  start_time = end_time - datetime.timedelta(days=1)

  # 計算已結算正刀數量
  cursor = connection.cursor(prepared = True)
  sql = "\
    SELECT COUNT(*) FROM princess_connect_hatsune.knifes \
    WHERE server_id = ? \
    AND member_id = ? \
    AND type = ? \
    AND update_time > ? \
    AND update_time < ? \
  "
  data = (server_id, member_id, Module.define_value.Knife_Type.NORMAL.value, start_time, end_time)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close()
  if row:
    today_knife = int(row[0])

    # 找出該位一天可以出幾刀
    cursor = connection.cursor(prepared = True)
    sql = "\
      SELECT knife_limit FROM princess_connect_hatsune.members \
      WHERE server_id = ? \
      AND member_id = ? \
    "
    data = (server_id, member_id)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    cursor.close()
    if row:
      knife_limit = int(row[0])
      if today_knife < knife_limit:
        return True
      else:
        return False
    else:
      await message.channel.send('您不是戰隊成員喔')
  else:
    await message.channel.send('您不是戰隊成員喔')
    