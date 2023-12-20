from datetime import datetime, timedelta
from dateutil import relativedelta
str = '20231219'
dte = datetime.strptime(str, '%Y%m%d')
print(dte+relativedelta(months=1))