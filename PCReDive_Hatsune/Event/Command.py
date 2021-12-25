import os
import datetime
import csv
import re
import mysql.connector
from mysql.connector import Error

import discord
from discord import Embed
from Discord_client import client
import Module.full_string_to_half_and_lower
import Module.DB_control

import Name_manager
#import Module.Authentication
import Module.Update
import Module.report_update
#import Module.Offset_manager
import Module.check_week
import Module.check_boss
import Module.define_value
import Module.get_closest_end_time
import Module.check_knife_limit


@client.event
async def on_message(message):
  # 防止機器人自問自答
  if message.author == client.user:
    return

  # --------------------------------------------------------------------指令部分------------------------------------------------------------------------------------------------------
  try:
    tokens = message.content.split()
    if len(tokens) > 0: # 邊界檢查
      tokens[0] = Module.full_string_to_half_and_lower.full_string_to_half_and_lower(tokens[0])

      #!init
      if tokens[0] == '!init':

        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          # 尋找戰隊有無存在
          cursor = connection.cursor(prepared=True)
          sql = "select * from princess_connect_hatsune.group where server_id = ?"
          data = (message.guild.id, )
          cursor.execute(sql, data)
          row = cursor.fetchone()
          cursor.close

          # 查無該戰隊資料，新增一筆資料
          if not row: 
            cursor = connection.cursor(prepared=True)
            sql = "INSERT INTO princess_connect_hatsune.group (server_id, now_week) VALUES (?, ?)"
            data = (message.guild.id, 1)
            cursor.execute(sql, data)
            cursor.close
            connection.commit() # 資料庫存檔
            await message.channel.send('註冊完成!')
          else:
            await message.channel.send('已註冊過')
          await Module.DB_control.CloseConnection(connection, message)

      #!action_here
      if tokens[0] == '!action_here':
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          # 尋找戰隊有無存在
          cursor = connection.cursor(prepared=True)
          sql = "select * from princess_connect_hatsune.group where server_id = ?"
          data = (message.guild.id, )
          cursor.execute(sql, data)
          row = cursor.fetchone()
          cursor.close

          # 查無該戰隊資料，新增一筆，預設1週目1王，除當前週目外，可往後預約4週目
          if row: 
            # 產生初始化訊息
            embed_msg = Embed(description="初始化刀表中!",color=0xD98B99)
            action_message = await message.channel.send(embed = embed_msg)
            embed_msg = Embed(description="初始化暫存刀表中!",color=0xD9ACA3)
            reserved_message_message = await message.channel.send(embed = embed_msg)
            embed_msg = Embed(description="初始化報表中!",color=0xF1DEDA)
            report_message_message = await message.channel.send(embed = embed_msg)
            
            
            # 寫入資料庫
            cursor = connection.cursor(prepared=True)
            sql = "UPDATE princess_connect_hatsune.group SET action_channel_id = ? ,action_message_id = ?, reserved_message_id=?, report_message_id=? WHERE server_id = ?"
            data = (message.channel.id, action_message.id, reserved_message_message.id, report_message_message.id, message.guild.id)
            cursor.execute(sql, data)
            cursor.close
            connection.commit()
            await Module.Update.Update(message, message.guild.id)
            await Module.report_update.report_update(message, message.guild.id) 
          else:
            await message.channel.send('尚未註冊')
          await Module.DB_control.CloseConnection(connection, message)

      #!sign_here
      elif tokens[0] == '!sign_here':
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          # 尋找戰隊有無存在
          cursor = connection.cursor(prepared=True)
          sql = "select * from princess_connect_hatsune.group where server_id = ?"
          data = (message.guild.id, )
          cursor.execute(sql, data)
          row = cursor.fetchone()
          cursor.close

          # 查無該戰隊資料，新增一筆，預設1週目1王，除當前週目外，可往後預約4週目
          if row: 
            # 寫入資料庫
            cursor = connection.cursor(prepared=True)
            sql = "UPDATE princess_connect_hatsune.group SET sign_channel_id = ? WHERE server_id = ?"
            data = (message.channel.id, message.guild.id)
            cursor.execute(sql, data)
            cursor.close
            connection.commit()
            await message.channel.send('報刀是吧，了解!')
          else:
            await message.channel.send('尚未註冊')
          await Module.DB_control.CloseConnection(connection, message)

      #!set_week [週目]
      elif tokens[0] == '!set_week':
        if len(tokens) == 2:
          if tokens[1].isdigit():
            week = int(tokens[1])
            connection = await Module.DB_control.OpenConnection(message)
            if connection:
              # 尋找戰隊有無存在
              cursor = connection.cursor(prepared=True)
              sql = "select * from princess_connect_hatsune.group where server_id = ?"
              data = (message.guild.id, )
              cursor.execute(sql, data)
              row = cursor.fetchone()
              cursor.close

              if row: 
                # 寫入資料庫
                cursor = connection.cursor(prepared=True)
                sql = "UPDATE princess_connect_hatsune.group SET now_week = ? WHERE server_id = ?"
                data = (week, message.guild.id)
                cursor.execute(sql, data)
                cursor.close
                connection.commit()
                await message.channel.send('週目已設定至{}週'.format(week))
                await Module.Update.Update(message, message.guild.id) # 更新活動表
              else:
                await message.channel.send('戰隊尚未註冊，請使用!init')
              await Module.DB_control.CloseConnection(connection, message)
          else:
            await message.channel.send('[週目] 僅能使用阿拉伯數字')
        else:
          await message.channel.send('格式錯誤，應為:\n!set_week [週目]')

      #!add_member [成員1] [成員2] ...
      elif tokens[0] == '!add_member':

        if len(tokens) >= 2:
          connection = await Module.DB_control.OpenConnection(message)
          if connection:
            # 檢查成員是否存在
            illegal_members = ''
            member_list = []
            for member in message.mentions:
              cursor = connection.cursor(prepared=True)
              sql = "SELECT * FROM princess_connect_hatsune.members WHERE server_id=? and member_id=? LIMIT 0, 1"
              data = (message.guild.id, member.id)
              cursor.execute(sql, data)
              row = cursor.fetchone()
              cursor.close
              if row:
                illegal_members = illegal_members + member.mention + ' '
              else:
                member_list.append(member)
                    
            # 寫入成員名單
            legal_members = ''
            for member in member_list:
              cursor = connection.cursor(prepared=True)
              sql = "INSERT INTO princess_connect_hatsune.members (server_id, member_id) VALUES (?, ?)"
              data = (message.guild.id, member.id)
              cursor.execute(sql, data)
              cursor.close
              legal_members = legal_members + member.mention + ' '

            connection.commit() # 資料庫存檔
            connection.close


            # 列出成員名單
            if legal_members == '':
              if illegal_members == '':
                pass
              else:
                await message.channel.send('下列人員已存在:\n' + illegal_members )
            else:
              if illegal_members == '':
                await message.channel.send('新增下列人員:\n' + legal_members )
              else:
                await message.channel.send('下列人員已存在:\n' + illegal_members + '\n新增下列人員' + legal_members )
            await Module.report_update.report_update(message, message.guild.id)
            await Module.DB_control.CloseConnection(connection, message)
        else:
          await message.channel.send('!add_member [成員1] [成員2] ... [成員n]')
        connection = await Module.DB_control.OpenConnection(message)

      #!del_member [成員1] [成員2] ...
      elif tokens[0] == '!del_member':

        if len(tokens) >= 2:
          connection = await Module.DB_control.OpenConnection(message)
          if connection:
            # 檢查成員是否存在
            legal_members = ''
            illegal_members = ''
            del_member_list = []
            for member in message.mentions:
              cursor = connection.cursor(prepared=True)
              sql = "SELECT * FROM princess_connect_hatsune.members WHERE server_id=? and member_id=? LIMIT 0, 1"
              data = (message.guild.id, member.id)
              cursor.execute(sql, data)
              row = cursor.fetchone()
              cursor.close
              if row:
                legal_members = legal_members + member.mention + ' '
                del_member_list.append(member)
              else:
                illegal_members = illegal_members + member.mention + ' '
                    
            for member in del_member_list:
              # 刪除報刀資訊
              cursor = connection.cursor(prepared=True)
              sql = "DELETE FROM princess_connect_hatsune.knifes WHERE server_id = ? AND member_id = ?"
              data = (message.guild.id, member.id)
              cursor.execute(sql, data)
              cursor.close

              # 刪除成員資訊
              cursor = connection.cursor(prepared=True)
              sql = "DELETE FROM princess_connect_hatsune.members WHERE server_id = ? AND member_id = ?"
              data = (message.guild.id, member.id)
              cursor.execute(sql, data)
              cursor.close
              
            connection.commit() # 資料庫存檔
            connection.close


            # 列出成員名單
            if illegal_members == '':
              if legal_members == '':
                await message.channel.send('成員無更動')
              else:
                await message.channel.send('下列人員已刪除:\n' + legal_members )
            else:
              if legal_members == '':
                await message.channel.send('下列人員不存在:\n' + illegal_members )
              else:
                await message.channel.send('下列人員已刪除:\n' + legal_members + '\n下列人員不存在:\n' + illegal_members )
            await Module.report_update.report_update(message, message.guild.id)
            await Module.DB_control.CloseConnection(connection, message)
        else:
          await message.channel.send('!del_member [成員1] [成員2] ... [成員n]')
        connection = await Module.DB_control.OpenConnection(message)

      #!set_member [成員] [刀數] ...
      elif tokens[0] == '!set_member':
        if len(tokens) == 3:
          connection = await Module.DB_control.OpenConnection(message)
          if connection:
            if len(message.mentions)==1:
              if tokens[2].isdigit():
                limit_knife_number = int(tokens[2])
                # 檢查成員是否存在
                cursor = connection.cursor(prepared=True)
                sql = "SELECT * FROM princess_connect_hatsune.members WHERE server_id=? and member_id=? LIMIT 0, 1"
                data = (message.guild.id, message.mentions[0].id)
                cursor.execute(sql, data)
                row = cursor.fetchone()
                cursor.close
                if row:
                  # UPDATE
                  cursor = connection.cursor(prepared=True)
                  sql = "UPDATE princess_connect_hatsune.members SET knife_limit = ? WHERE server_id=? and member_id=?"
                  data = (limit_knife_number, message.guild.id, message.mentions[0].id)
                  cursor.execute(sql, data)
                  cursor.close
                  connection.commit() # 資料庫存檔

                  nick_name = await Name_manager.get_nick_name(message, message.mentions[0].id) # 取得DC暱稱
                  await message.channel.send('成員{}可出刀數已更改為{}刀'.format(nick_name, limit_knife_number))
                  await Module.report_update.report_update(message, message.guild.id)
                else:
                  await message.channel.send('該成員不在此戰隊中')
              else:
                await message.channel.send('[刀數] 僅能為阿拉伯數字')
            else:
              await message.channel.send('[成員] 請tag成員')

            await Module.DB_control.CloseConnection(connection, message)

        else:
          await message.channel.send('格式錯誤，應為:\n!set_member [成員] [刀數]')

      #!1 [week] [boss] [method]  0 = normal  1 = addtional
      elif tokens[0] == '!1': # enter
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT now_week FROM princess_connect_hatsune.group WHERE server_id=? AND sign_channel_id=? limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            main_week = int(row[0])
            if len(tokens) == 4:
              if tokens[1].isdigit() and tokens[2].isdigit() and tokens[3].isdigit():
                week = int(tokens[1])
                boss = int(tokens[2])
                type = None
                type_description = ''

                if int(tokens[3])== Module.define_value.Knife_Type.NORMAL_ENTER.value:
                  type = Module.define_value.Knife_Type.NORMAL_ENTER.value
                  type_description = '正刀'
                elif int(tokens[3])== Module.define_value.Knife_Type.RESERVED_ENTER.value:
                  type = Module.define_value.Knife_Type.RESERVED_ENTER.value
                  type_description = '補償刀'
                else:
                  pass
                  
                if not type == None:
                  if Module.check_week.Check_week(main_week, week):
                    if Module.check_boss.Check_boss(connection, message, message.guild.id, week, boss):
                      if type == Module.define_value.Knife_Type.RESERVED_ENTER.value or await Module.check_knife_limit.check_knife_limit(connection, message, message.guild.id, message.author.id):
                        cursor = connection.cursor(prepared=True)
                        sql = "SELECT type FROM princess_connect_hatsune.knifes WHERE server_id=? and member_id=? AND (type = ? or type = ? or type = ? or type = ?) limit 0, 1"
                        data = (message.guild.id, message.author.id, Module.define_value.Knife_Type.NORMAL_ENTER.value, Module.define_value.Knife_Type.RESERVED_ENTER.value, Module.define_value.Knife_Type.NORMAL_WAIT.value, Module.define_value.Knife_Type.RESERVED_WAIT.value)
                        cursor.execute(sql, data) # 檢查是否有進刀
                        row = cursor.fetchone()
                        cursor.close
                        if not row:
                          # 新增刀
                          cursor = connection.cursor(prepared=True)
                          sql = "INSERT INTO princess_connect_hatsune.knifes (server_id, member_id, type, week, boss) VALUES (?, ?, ?, ?, ?)"
                          data = (message.guild.id, message.author.id, type ,week, boss)
                          cursor.execute(sql, data)
                          cursor.close
                          connection.commit()
                          await message.channel.send('第' + str(week) + '週目' + str(boss) + '王，' + type_description + '已進刀!')
                          await Module.Update.Update(message, message.guild.id) # 更新刀表  
                        else:
                          await message.channel.send('已有進刀紀錄，請完成該刀後再次嘗試!')
                      else:
                        await message.channel.send('已達今日出刀上限，感謝您的付出!')
                    else:
                      await message.channel.send('該王不存在喔!')
                  else:
                    await message.channel.send('該週目不存在喔!')
                else:
                  await message.channel.send('類型錯誤，0:正刀、1:補償刀。')
              else:
                await message.channel.send('[週目] [boss] [0.正刀/1.補償刀]請使用阿拉伯數字!')
            else:
              await message.channel.send('格式錯誤，應為:\n!1 [週目] [boss] [0.正刀/1.補償刀]')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)

      #!2 [剩餘秒數] [damage] [comment]
      elif tokens[0] == '!2': # enter
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT sign_channel_id FROM princess_connect_hatsune.group WHERE server_id=? AND sign_channel_id=? limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            if len(tokens) == 4:
              if tokens[1].isdigit() and tokens[2].isdigit():
                reserved_time = int(tokens[1])
                damage = int(tokens[2])
                comment = tokens[3]
                type_description = ''

                cursor = connection.cursor(prepared=True)
                sql = "SELECT type FROM princess_connect_hatsune.knifes WHERE server_id=? and member_id=? AND ( type = ? or type = ? ) limit 0, 1"
                data = (message.guild.id, message.author.id, Module.define_value.Knife_Type.NORMAL_ENTER.value, Module.define_value.Knife_Type.RESERVED_ENTER.value)
                cursor.execute(sql, data) # 檢查是否有進刀
                row = cursor.fetchone()
                cursor.close
                if row:
                  # 更新狀態
                  cursor = connection.cursor(prepared=True)
                  sql = "update princess_connect_hatsune.knifes set type=?, reserved_time=?, damage=?, comment=?  WHERE server_id=? and member_id=? AND ( type = ? or type = ? )"
                  data = ( int(row[0]) + 2, reserved_time, damage, comment, message.guild.id, message.author.id, Module.define_value.Knife_Type.NORMAL_ENTER.value, Module.define_value.Knife_Type.RESERVED_ENTER.value)
                  cursor.execute(sql, data)
                  cursor.close
                  connection.commit() # 資料庫存檔

                  type_description = None
                  if int(row[0])== Module.define_value.Knife_Type.NORMAL_ENTER.value:
                    type_description = '正刀'
                  else:
                    type_description = '補償刀'
                  
                  await message.channel.send('剩餘秒數' + str(reserved_time) + '，目前傷害' + str(damage) + ','+ comment + ',' + type_description + '已卡好!')
                  await Module.Update.Update(message, message.guild.id) # 更新刀表  
                else:
                  await message.channel.send('請先進刀!')
              else:
                await message.channel.send('[剩餘秒數] [damage]只能為阿拉伯數字')
            else:
              await message.channel.send('格式錯誤，應為:\n!2 [剩餘秒數] [damage] [comment]')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)

      #!3 [實際造成傷害]
      elif tokens[0] == '!3': # enter
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT sign_channel_id FROM princess_connect_hatsune.group WHERE server_id=? AND sign_channel_id=? limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            if len(tokens) == 2:
              if tokens[1].isdigit() :
                damage = int(tokens[1])

                type_description = ''
                cursor = connection.cursor(prepared=True)
                sql = "SELECT type, week, boss FROM princess_connect_hatsune.knifes WHERE server_id=? and member_id=? AND ( type = ? or type = ? ) limit 0, 1"
                data = (message.guild.id, message.author.id, Module.define_value.Knife_Type.NORMAL_WAIT.value, Module.define_value.Knife_Type.RESERVED_WAIT.value)
                cursor.execute(sql, data) # 檢查是否有進刀
                row = cursor.fetchone()
                cursor.close
                if row:
                  if Module.check_boss.Check_boss(connection, message, message.guild.id, week, boss):
                    type_description = None
                    type = None
                    insert_reversed_knife = False
                    if int(row[0])== Module.define_value.Knife_Type.NORMAL_WAIT.value:
                      type_description = '正刀'
                      type = Module.define_value.Knife_Type.NORMAL.value
                    else:
                      type_description = '補償刀'
                      type = Module.define_value.Knife_Type.ADDITIONAL.value

                    # 更新狀態
                    cursor = connection.cursor(prepared=True)
                    sql = "update princess_connect_hatsune.knifes set type=?, damage=? WHERE server_id=? and member_id=? AND ( type = ? or type = ? )"
                    data = ( int(row[0]) + 2, damage, message.guild.id, message.author.id, Module.define_value.Knife_Type.NORMAL_WAIT.value, Module.define_value.Knife_Type.RESERVED_WAIT.value)
                    cursor.execute(sql, data)
                    cursor.close
                    connection.commit() # 資料庫存檔
                  
                    await message.channel.send(str(row[1]) + '週' + str(row[2]) + '王，造成傷害' + str(damage) + '，已結算!')
                    await Module.Update.Update(message, message.guild.id) # 更新刀表  
                    await Module.report_update.report_update(message, message.guild.id)
                  else:
                    await message.channel.send('該王已被擊殺，請使用!c退刀')
                else:
                  await message.channel.send('請先卡秒!')
              else:
                await message.channel.send('類型錯誤，0:沒領到補償刀、1:有領到補償刀。')
            else:
              await message.channel.send('格式錯誤，應為:\n!3 [實際造成傷害]')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)

      #!r [秒數] [備註]
      elif tokens[0] == '!r': #
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT sign_channel_id FROM princess_connect_hatsune.group WHERE server_id=? AND sign_channel_id=? limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            if len(tokens) == 3:
              if tokens[1].isdigit():
                reserved_time = int(tokens[1])
                comment = tokens[2]

                # 新增刀
                cursor = connection.cursor(prepared=True)
                sql = "INSERT INTO princess_connect_hatsune.knifes (server_id, member_id, type, comment) VALUES (?, ?, ?, ?)"
                data = (message.guild.id, message.author.id, Module.define_value.Knife_Type.RESERVED.value, comment)
                cursor.execute(sql, data)
                cursor.close
                connection.commit()
                await message.channel.send(str(reserved_time) +'秒補償，' + comment + '，已登記')
                await Module.Update.Update(message, message.guild.id) # 更新刀表  
                await Module.report_update.report_update(message, message.guild.id) # 更新報表
              else:
                await message.channel.send('[週目] [boss]請使用阿拉伯數字!')
            else:
              await message.channel.send('格式錯誤，應為:\n!r [週目] [boss]')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)

      #!c 取消補償(也就是退刀)
      elif tokens[0] == '!c': # 取消(也就是退刀)
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT sign_channel_id FROM princess_connect_hatsune.group WHERE server_id=? AND sign_channel_id=? limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            if len(tokens) == 1: 
              cursor = connection.cursor(prepared=True)
              sql = "SELECT type, week, boss FROM princess_connect_hatsune.knifes WHERE server_id=? and member_id=? AND (type = ? or type = ? or type = ? or type = ?) limit 0, 1"
              data = (message.guild.id, message.author.id, Module.define_value.Knife_Type.NORMAL_ENTER.value, Module.define_value.Knife_Type.RESERVED_ENTER.value, Module.define_value.Knife_Type.NORMAL_WAIT.value, Module.define_value.Knife_Type.RESERVED_WAIT.value)
              cursor.execute(sql, data) # 檢查是否有進刀
              row = cursor.fetchone()
              cursor.close
              if row:
                # 刪除
                cursor = connection.cursor(prepared=True)
                sql = "DELETE FROM princess_connect_hatsune.knifes WHERE server_id=? and member_id=? AND (type = ? or type = ? or type = ? or type = ?)"
                cursor.execute(sql, data) # DATA同上
                cursor.close
                connection.commit()
                await message.channel.send('第' + str(row[1]) + '週目' + str(row[2]) + '王，已退刀!')
                await Module.Update.Update(message, message.guild.id) # 更新刀表  
              else:
                await message.channel.send('查無正在進行的紀錄')
            else:
              await message.channel.send('格式錯誤，應為:\n!c')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)

      #!cc 取消補償 [序號]
      elif tokens[0] == '!cc': 
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT sign_channel_id FROM princess_connect_hatsune.group WHERE server_id=? AND sign_channel_id=? limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            if len(tokens) == 2: 
              if tokens[1].isdigit():
                index = int(tokens[1]) - 1 # SQL由0開始
                # 檢查該刀有無在表中
                cursor = connection.cursor(prepared=True)
                sql = "SELECT serial_number, member_id FROM princess_connect_hatsune.knifes WHERE server_id=? AND type = ? order by serial_number LIMIT ?, 1"
                data = (message.guild.id, Module.define_value.Knife_Type.RESERVED.value, index)
                cursor.execute(sql, data)
                row = cursor.fetchone()
                cursor.close
                if row:
                  if row[1] == message.author.id:
                    # 刪除
                    cursor = connection.cursor(prepared=True)
                    sql = "DELETE FROM princess_connect_hatsune.knifes WHERE serial_number=?"
                    data = (row[0],)
                    cursor.execute(sql, data)
                    cursor.close
                    connection.commit()
                    await message.channel.send('序號{}，補償刀紀錄已移除!'.format(index + 1)) # 給使用者看要加回來
                    await Module.Update.Update(message, message.guild.id) # 更新刀表  
                    await Module.report_update.report_update(message, message.guild.id)
                  else:
                    await message.channel.send('您非該刀主人喔')
                else:
                  await message.channel.send('查無該序號紀錄')
              else:
                await message.channel.send('[序號] 僅能使用阿拉伯數字')
            else:
              await message.channel.send('格式錯誤，應為:\n!cc [序號]')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)

      #!sl
      elif tokens[0] == '!sl':
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT sign_channel_id FROM princess_connect_hatsune.group WHERE server_id=? AND sign_channel_id=? limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            cursor = connection.cursor(prepared=True)
            sql = "SELECT sl_time FROM princess_connect_hatsune.members WHERE server_id=? AND member_id=? limit 0, 1"
            data = (message.guild.id, message.author.id)
            cursor.execute(sql, data) # 認證身分
            row = cursor.fetchone()
            if row:
              # 修改SL時間
              closest_end_time = Module.get_closest_end_time.get_closest_end_time(datetime.datetime.now())
              if row[0] < closest_end_time:
                cursor = connection.cursor(prepared=True)
                sql = "update princess_connect_hatsune.members SET sl_time=? WHERE server_id = ? and member_id = ?"
                data = (closest_end_time, message.guild.id, message.author.id)
                cursor.execute(sql, data)
                connection.commit()
                await message.channel.send('紀錄完成!')
                await Module.report_update.report_update(message, message.guild.id)
              else:
                await message.channel.send('注意，今日已使用過SL，請勿退出遊戲!')
            else:
              await message.channel.send('你不在該戰隊中')
          else:
            pass # await message.channel.send('這裡不是報刀頻道喔，請在所屬戰隊報刀頻道使用!')
          await Module.DB_control.CloseConnection(connection, message)

  except Error as e:
    print("資料庫錯誤 ",e)
  except Exception as e:
    print("error ",e)

