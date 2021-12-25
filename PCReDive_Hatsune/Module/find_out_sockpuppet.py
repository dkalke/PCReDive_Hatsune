async def find_out_sockpuppet(connection, message):
  cursor = connection.cursor(prepared=True)
  sql = "SELECT sockpuppet FROM princess_connect_hatsune.members WHERE server_id=? and member_id=? AND now_using = '1' limit 0, 1"
  data = (message.guild.id, message.author.id)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  if row:
    return int(row[0])
  else:
    await message.channel.send('您不在該戰隊喔!')
    return None