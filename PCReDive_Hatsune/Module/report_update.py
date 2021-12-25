import datetime
from enum import Enum
from discord import Embed
import Discord_client
import Name_manager
import Module.DB_control
import Module.define_value
import Module.get_closest_end_time

async def report_update(message ,server_id):
  # 取得資訊訊息物件
  connection = await Module.DB_control.OpenConnection(message)
  if connection.is_connected():
    cursor = connection.cursor(prepared=True)
    sql = "SELECT action_channel_id, report_message_id FROM princess_connect_hatsune.group WHERE server_id = ? LIMIT 0, 1"
    data = (server_id, )
    cursor.execute(sql, data)
    row = cursor.fetchone()
    cursor.close
    if row: # 戰隊存在
      action_channel_id = row[0]
      report_message_id = row[1]

      if report_message_id :
        # 取得戰隊戰日期
        date_now = datetime.datetime.now()
        day_name = ''

        if date_now < Module.define_value.BATTLE_DAY[0]:
          day_name = '(尚未開戰)'
        elif date_now < Module.define_value.BATTLE_DAY[1]:
          day_name = '戰隊戰第1天'
        elif date_now < Module.define_value.BATTLE_DAY[2]:
          day_name = '戰隊戰第2天'
        elif date_now < Module.define_value.BATTLE_DAY[3]:
          day_name = '戰隊戰第3天'
        elif date_now < Module.define_value.BATTLE_DAY[4]:
          day_name = '戰隊戰第4天'
        elif date_now < Module.define_value.BATTLE_DAY[4]:
          day_name = '戰隊戰第5天'
        else:
          day_name = '(等待下月戰隊戰日期公佈中)'

        end_time = Module.get_closest_end_time.get_closest_end_time(date_now) # 取得當日結束時間 29點00分
        start_time = end_time - datetime.timedelta(days=1)
        embed_msg = Embed(title='戰隊報表', description=day_name ,color=0xF1DEDA)

        # 列出序號、成員名稱、剩餘正刀刀數、剩餘補償刀數
        cursor = connection.cursor(prepared=True)
        # 抓出正刀
        sql = "\
          SELECT member_id, sl_time , \
          (SELECT COUNT(*) FROM princess_connect_hatsune.knifes k WHERE k.member_id = m.member_id AND k.`type` = ? AND k.update_time > ? AND k.update_time < ? ) AS normal_times, \
          (SELECT COUNT(*) FROM princess_connect_hatsune.knifes k WHERE k.member_id = m.member_id AND k.`type` = ? AND k.update_time > ? AND k.update_time < ? ) AS addtional_times, \
          (SELECT COUNT(*) FROM princess_connect_hatsune.knifes k WHERE k.member_id = m.member_id AND k.`type` = ? AND k.update_time > ? AND k.update_time < ? ) AS revered_times \
          FROM princess_connect_hatsune.members m \
          WHERE server_id = ? \
          ORDER BY m.member_id"
        data = (Module.define_value.Knife_Type.NORMAL.value, start_time, end_time, 
                Module.define_value.Knife_Type.ADDITIONAL.value, start_time, end_time, 
                Module.define_value.Knife_Type.RESERVED.value, start_time, end_time, 
                server_id)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        msg = ''
        normal_total = 0
        additional_total = 0
        reversed_total = 0
        count = 1
        while row:
          member_id=row[0]
          sl_time=row[1]
          normal_times = row[2]
          addtional_times = row[3]
          revered_times = row[4]

          # 是否有SL?
          if sl_time >= end_time:
            sl_time = '[閃退已用] '
          else:
            sl_time = '[閃退未用] '

            
          member_name = await Name_manager.get_nick_name(message, member_id)
          msg = msg + '{' + str(count) + '} ' + sl_time + member_name + '\n'
          msg = msg+ '　' + '正刀已出' + str(normal_times) + '刀、補償已出' + str(addtional_times) + '刀、補償還剩' + str(revered_times) + '刀' + '\n'
          normal_total = normal_total + normal_times
          additional_total = additional_total + addtional_times
          reversed_total = reversed_total + revered_times
          count = count + 1
          row = cursor.fetchone()

        cursor.close

        if msg == '':
          msg = '尚無成員資訊!'
        else:
          msg = msg + '{合計}\n'
          msg = msg+ '　' + '正刀已出' + str(normal_total) + '刀、補償已出' + str(additional_total) + '刀、補償還剩' + str(reversed_total) + '刀' + '\n'

        embed_msg.add_field(name='\u200b', value=msg , inline=False)

        # 取得訊息物件
        try:
          guild = Discord_client.client.get_guild(server_id)
          channel = guild.get_channel(action_channel_id)
          message_obj = await channel.fetch_message(report_message_id)
          await message_obj.edit(embed=embed_msg)
        except:
          await message.channel.send(content='報表訊息已被移除，請重新設定報表頻道!')
      else:
        await message.channel.send(content='請戰隊隊長設定報表頻道!')

    else:
      await message.channel.send(content='查無戰隊資料!')

    await Module.DB_control.CloseConnection(connection, message)
