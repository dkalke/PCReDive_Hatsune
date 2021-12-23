import os
import datetime
import mysql.connector
from discord import Embed
import Discord_client
import Name_manager
import Module.DB_control
import Module.define_value
import Module.week_stage
import Module.get_closest_end_time

async def Update(message ,server_id):
  connection = await Module.DB_control.OpenConnection(message)
  if connection.is_connected():
    await UpdateEmbed(connection, message, server_id)
    await Module.DB_control.CloseConnection(connection, message)
  
async def UpdateEmbed(connection, message, server_id): # 更新刀表
  # 查詢當前周目、王、刀表訊息、保留刀訊息
  cursor = connection.cursor(prepared=True)
  sql = "SELECT now_week ,action_channel_id, action_message_id, reserved_message_id FROM princess_connect_hatsune.group WHERE server_id = ? LIMIT 0, 1"
  data = (server_id, )
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  if row:
    now_week = row[0]
    action_channel_id = row[1]
    action_message_id = row[2]
    reserved_message_id = row[3]
    date_now = datetime.datetime.now()
    closest_end_time = Module.get_closest_end_time.get_closest_day_end(date_now) # 取得當日結束時間 29點00分

    if action_channel_id:
      embed_msg = Embed(title='當前狀態', color=0xD98B99)
      # 當前狀態，印出now_week與now_week+1
      for i in range(now_week, now_week + 2):
        need_update_now_week = True # 如果五隻王都死，now_week += 1
        week_stage = Module.week_stage.week_stage(i)
        week_msg = ''
        for j in range(1,6):  
          kinfe_msg = ''
          # 計算該王受到的傷害，只抓正刀與尾刀
          cursor = connection.cursor(prepared=True)
          sql = \
            "SELECT server_id, boss, week, SUM(damage), \
            (SELECT SUM(damage) FROM princess_connect_hatsune.knifes \
            WHERE server_id = ? and week = ? and boss = ? and type >= ? and type <= ? \
            group BY server_id, week, boss) as temp_damage FROM princess_connect_hatsune.knifes\
            WHERE server_id = ? and week = ? and boss = ? and type >= ? and type <= ? \
            group BY server_id, week, boss"
          data = (server_id, i ,j, Module.define_value.Knife_Type.NORMAL_ENTER.value, Module.define_value.Knife_Type.ADDITIONAL.value, \
            server_id, i ,j, Module.define_value.Knife_Type.NORMAL.value, Module.define_value.Knife_Type.ADDITIONAL.value)
          cursor.execute(sql, data)
          row = cursor.fetchone()

          if not row: # 乏人問津
            need_update_now_week = False
            title_msg = '**' + str(j) + '**王(**' + str(Module.define_value.BOSS_HP[week_stage][j-1]) + '**/**' + str(Module.define_value.BOSS_HP[week_stage][j-1]) +'**)\n'
            kinfe_msg = '　(乏人問津)\n'
          else:
            temp_damage = 0
            if row[3]:
              temp_damage = int(row[3])
            real_damage = 0
            if row[4]:
              real_damage = int(row[4])

            if real_damage > Module.define_value.BOSS_HP[week_stage][j-1]: # 王死
              title_msg = '**' + str(j) + '**王(**0**/**' + str(Module.define_value.BOSS_HP[week_stage][j-1]) +'**)\n'
              kinfe_msg = '　(已討伐)\n'
            else:
              need_update_now_week = False
              title_msg = '**' + str(j) + '**王(**'+ str(Module.define_value.BOSS_HP[week_stage][j-1] - temp_damage) + '**/**' + str(Module.define_value.BOSS_HP[week_stage][j-1]) +'**)\n'
              # 刀表SQL
              cursor = connection.cursor(prepared=True)
              sql = "SELECT a.member_id, type, reserved_time, damage, comment, sl_time FROM princess_connect_hatsune.knifes a left join princess_connect_hatsune.members b ON a.member_id=b.member_id WHERE a.server_id = ? and week = ? and boss = ? order by a.serial_number"
              data = (server_id, i ,j)
              cursor.execute(sql, data)
              row = cursor.fetchone()
              index = 1
              kinfe_msg = '' # 該週目該王報刀資訊
              while row:
                # 出刀狀況
                nick_name = await Name_manager.get_nick_name(message, row[0]) # 取得DC暱稱
                type = row[1]
                reserved_time = row[2]
                damage = row[3]
                comment = row[4]
                sl_time = row[5]

                if sl_time >= closest_end_time:
                  sl_time = '[無閃] '
                else:
                  sl_time = '[有閃] '

                # 依照刀的狀態決定輸出樣式
                if type == Module.define_value.Knife_Type.NORMAL_ENTER.value or type == Module.define_value.Knife_Type.RESERVED_ENTER.value:
                  kinfe_msg = kinfe_msg + '　{' +str(index) + '} [進行中]' + sl_time + nick_name + '\n'
                elif type == Module.define_value.Knife_Type.NORMAL_WAIT.value or type == Module.define_value.Knife_Type.RESERVED_WAIT.value:
                  kinfe_msg = kinfe_msg + '　{' +str(index) + '} [等待中]' + sl_time + nick_name + '\n　　' + '傷害' + str(damage) + '，剩餘秒數' + str(reserved_time) + '，' + comment + '\n'
                elif type == Module.define_value.Knife_Type.NORMAL.value or type == Module.define_value.Knife_Type.ADDITIONAL.value:
                  kinfe_msg = kinfe_msg + '　{' +str(index) + '} [已結算]' + sl_time + nick_name + '\n　　' + '傷害' + str(damage) + '\n'
                elif type == Module.define_value.Knife_Type.RESERVED.value:
                  pass

                index = index +1
                row = cursor.fetchone()
              cursor.close()
          week_msg = week_msg + title_msg + kinfe_msg
        index_boss = 1
        embed_msg.add_field(name='\u200b', value='-   -   -   -   -   -   -   -   ', inline=False)
        embed_msg.add_field(name='第' + str(i) + '週目', value=week_msg , inline=False)
            
  
      if need_update_now_week: #更新now_week 重跑一次
        cursor = connection.cursor(prepared=True)
        sql = "UPDATE princess_connect_hatsune.group SET now_week = ? WHERE server_id = ?"
        data = (now_week + 1, message.guild.id)
        cursor.execute(sql, data)
        cursor.close
        connection.commit()
        await UpdateEmbed(connection, message, server_id); # 重跑一次
      else: #印出更新後的訊息，並繼續跑保留區
        try:
          guild = Discord_client.client.get_guild(server_id)
          channel = guild.get_channel(action_channel_id)
          message_obj = await channel.fetch_message(action_message_id)
          await message_obj.edit(embed=embed_msg)
        except:
          await message.channel.send(content='活動訊息已被移除，請重新設定活動頻道!')


        # 保留刀部分
        # 刀表SQL
        cursor = connection.cursor(prepared=True)
        sql = "SELECT member_id, comment FROM princess_connect_hatsune.knifes WHERE server_id = ? and type = ? order by serial_number"
        data = (server_id, Module.define_value.Knife_Type.RESERVED.value)
        cursor.execute(sql, data)
        msg = ''
        index = 1
        row = cursor.fetchone()
        while row:  
          # {index} nickname\tcomment\n
          name = await Name_manager.get_nick_name(message, row[0])
          msg = msg + '{' +str(index) + '} ' + name + '\n　' + row[1] + '\n'
          index = index + 1
          row = cursor.fetchone()
        cursor.close
  
        # 修改保留刀表
        if msg == '':
          msg = '保留區尚無相關資訊!'
        else:
          pass
        embed_msg = Embed(title='保留區', color=0xD9ACA3)
        embed_msg.add_field(name='\u200b', value=msg , inline=False)
            

        # 取得訊息物件
        try:
          guild = Discord_client.client.get_guild(server_id)
          channel = guild.get_channel(action_channel_id)
          message_obj = await channel.fetch_message(reserved_message_id)
          await message_obj.edit(embed=embed_msg)
        except:
          await message.channel.send(content='保留區訊息已被移除，請重新設定刀表頻道!')

    else:
      await message.channel.send(content='請戰隊隊長設定活動頻道!')
  else:
    await message.channel.send(content='查無戰隊資料!')
