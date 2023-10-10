import pandas as pd
import os
from collections import Counter

group_limit = 3000
version = '1.3.0'

file_list =os.listdir('事件属性/'+version)
# 将多天文件合并成同一文件
file_num = len(file_list)
df_test = pd.read_csv('事件属性/'+version+'/'+file_list[0])
full_file = pd.DataFrame(columns =list(df_test.columns))
full_file_out = pd.DataFrame(columns =list(df_test.columns))
for file in file_list:
    df_import = pd.read_csv('事件属性/'+version+'/'+file)
    full_file = pd.concat([full_file,df_import])
full_file = full_file[full_file['curr_level'] !='(null)']


full_label = []
curr_level =list(Counter(list(full_file['curr_level'])))
for ii in range(len(curr_level)):
    # 按关卡段划分数据
    level_file = full_file[full_file['curr_level'] ==curr_level[ii]]
    df = level_file
    start_times = list(df['stage_start.总次数'].astype(int))
    index=[]
    count= 0
    for i in range(len(start_times)):
        count += start_times[i]
        if count>=group_limit:
            index.append(i)
            count =0
            i = i+1
        else:
            i = i+1
    times_index_2 =[x+1 for x in index]

    label_=[]
    label_+=['0--'+str(ii)]*times_index_2[0]
    for i in range(len(times_index_2)):
         label_+=[str(i)+'--'+str(ii)]*(times_index_2[i]-times_index_2[i-1])
    label_ +=['9999--'+str(ii)]*(len(df)-times_index_2[-1])
    df.loc[:,'label'] =label_
    full_file_out = pd.concat([full_file_out,df])

ad_per_person = round(full_file_out['ads_reward.总次数'].astype(int)/full_file_out['任意事件.触发用户数'].astype(int),2)
time_per_person = round(full_file_out['人均时长'].astype(float)/full_file_out['任意事件.触发用户数'].astype(int),2)
add_step_per_person = round(full_file_out['加步'].astype(int)/full_file_out['任意事件.触发用户数'].astype(int),2)
tool_per_person = round(full_file_out['道具使用'].astype(int)/full_file_out['任意事件.触发用户数'].astype(int),2)
full_file_out['ad_per_person'] = ad_per_person
full_file_out['time_per_person'] = time_per_person
full_file_out['add_step_per_person'] = add_step_per_person
full_file_out['tool_per_person'] = tool_per_person
full_file_out['version'] = [version]*len(full_file_out)
full_file_out['labels'] = list(full_file_out['label'])
full_file_out = full_file_out.drop(['label'], axis=1)
full_file_out.columns=['date','curr_level','duration','stage_start','stage_win','ads_rewards','add_step','tool_use','all_users','ad_per_person','duration_per_person','add_step_per_person','tool_per_person','version','labels']

full_file_out.to_csv('带标签表格.csv')