content = open('backend/routers/calendar.py').read()
old = '    elif week_start.weekday() != 0:\n        raise HTTPException(status_code=400, detail="week_start must be a Monday")'
new = '    elif week_start.weekday() != 0:\n        week_start = week_start - timedelta(days=week_start.weekday())'
if old in content:
    content = content.replace(old, new)
    open('backend/routers/calendar.py', 'w').write(content)
    print('Done')
else:
    print('ERROR: not found')
