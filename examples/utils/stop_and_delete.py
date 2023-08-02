import os

# try:
#     os.system('redis-cli flushall')    
# except:
#     pass

try:
    os.system("pkill -9 -f 'celerytasks'")     
except:
    pass