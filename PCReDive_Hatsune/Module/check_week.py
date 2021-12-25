def Check_week(main_week, week): # main_week, week
  if main_week <= week and week < main_week + 2:
    return True
  else:
    return False