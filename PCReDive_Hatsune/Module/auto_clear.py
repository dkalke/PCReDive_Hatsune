import Discord_client
import Module.DB_control
import Module.Update
import Module.report_update


async def auto_clear():
  connection = await Module.DB_control.OpenConnection(None)
  if connection:
    cursor = connection.cursor(prepared=True)

    # 刪除刀表
    sql = "DELETE FROM princess_connect_hatsune.knifes"
    cursor.execute(sql)

    # 重設week到第一週
    sql = "UPDATE princess_connect_hatsune.group SET now_week='1'"
    cursor.execute(sql)

    # 更新所有戰隊刀表
    sql = "SELECT server_id, sign_channel_id, action_channel_id, action_message_id, reserved_message_id, report_message_id FROM princess_connect_hatsune.group"
    cursor.execute(sql)
    rows = cursor.fetchall()  
    for row in rows:
      server_id = row[0]
      sign_channel_id = row[1]
      action_channel_id = row[2]
      action_message_id = row[3]
      reserved_message_id = row[4]
      report_message_id = row[5]

      
      guild = Discord_client.client.get_guild(server_id)
      if not guild == None:
        # 取得報刀頻道
        message_obj = None
        try:
          channel = guild.get_channel(sign_channel_id)
          message_obj = await channel.send(content='正在執行戰前重置流程!')

          # 取得活動頻道
          try:
            channel = guild.get_channel(action_channel_id)
            await Module.Update.Update(message_obj, server_id) # 更新刀表  
            await Module.report_update.report_update(message_obj, server_id)
            await message_obj.edit(content = '已完成戰前重置流程!')
          except:
            print('伺服器:' + str(server_id) + ', 編號' + '頻道:' + str(action_channel_id) + '活動頻道不存在!')
        except:
          print('伺服器:' + str(server_id) + ', 編號' + '頻道:' + str(sign_channel_id) + '報刀頻道不存在!')
      else: # 清除不存在的戰隊資料
        sql = "DELETE FROM princess_connect_hatsune.group where server_id = ?"
        data = (server_id, )
        cursor.execute(sql, data)

        sql = "DELETE FROM princess_connect_hatsune.knifes where server_id = ?"
        data = (server_id, )
        cursor.execute(sql, data)

        sql = "DELETE FROM princess_connect_hatsune.members where server_id = ?"
        data = (server_id, )
        cursor.execute(sql, data)

        print('伺服器:' + str(server_id) + ', 編號' '頻道:' + str(action_channel_id) + '已從資料庫移除')

    connection.commit()
    cursor.close
    await Module.DB_control.CloseConnection(connection, None)
    print('已經清除所有刀表')