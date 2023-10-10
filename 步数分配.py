import pandas as pd
from collections import Counter
import math
import operator

# 设置参数
run_limit = 3 # 需要调整几轮
path = r'C:\Users\ZY001\Desktop\步数分配\\' # 修改成自己的

# 打开文件
file_1 = open(path + '单关调整表.csv', 'r', encoding='gbk')
file_2 = open(path + '关卡段调整表.csv', 'r', encoding='gbk')
df_1 = pd.read_csv(file_1)[['关卡数','关卡分段','调前难度','目标难度','调前步数','关卡距离目标难度差值(%)','分段步数调整幅度','置信度']]
df_2 = pd.read_csv(file_2)
df_2['需要调整的步数'] = round(df_2['预计调整步数 '],0)
df_2_reindex = df_2.set_index(['关卡分段'])
df_step_num = df_1.groupby(['关卡分段']).sum(['调前步数'])['调前步数']
df_2 = pd.concat([df_2_reindex,df_step_num], axis =1)

# 排序
section_list = list(Counter(list(df_1['关卡分段'])).keys()) # 关卡段
df_sorted = pd.DataFrame(columns=list(df_1.columns))
for i in range(len(section_list)):
    df_1_section = df_1[df_1['关卡分段']==section_list[i]]
    df_1_section = df_1_section[df_1_section['关卡距离目标难度差值(%)']*df_1_section['分段步数调整幅度']<0]
    z_list = list(df_1_section['置信度'])
    z_mean = sum(z_list)/len(z_list)
    for i in range(len(z_list)):
        if z_list[i]>1.3*z_mean:
            z_list[i] =1.3*z_mean
    df_1_section['调整置信度'] = z_list
    df_1_section['调整排序'] =df_1_section['调前步数']*abs(df_1_section['关卡距离目标难度差值(%)'])*df_1_section['调整置信度']
    df_1_section['调整排名'] =df_1_section['调整排序'].rank(ascending=False)
    df_1_section = df_1_section.sort_values('调整排序',inplace=False,ascending=False)
    df_sorted = pd.concat([df_sorted,df_1_section])

level_adjust_num = dict(Counter(list(df_sorted['关卡分段'])))
level_adjust_need = df_2['需要调整的步数']*(-1)
level_adjust_need =level_adjust_need.to_dict()
print('同方向关卡数：',level_adjust_num)
print('需要调整的关卡数',level_adjust_need)

out_of_distribution=[]
for x in section_list:
    if level_adjust_num[x]*run_limit>abs(level_adjust_need[x]):
        pass
    else:
        out_of_distribution.append(x)
print('不能在{}次完成分配的关卡段有：'.format(run_limit),out_of_distribution)

last_adjust_steps={}
for x in section_list:
    if x in out_of_distribution:
        last_adjust_steps[x] = level_adjust_num[x]
    else:
        if abs(level_adjust_need[x])%level_adjust_num[x]==0:
            last_adjust_steps[x] =level_adjust_num[x]
        else:
            last_adjust_steps[x] =level_adjust_need[x]%level_adjust_num[x]
print('最后一轮需要调整的步数：',last_adjust_steps)

# 分配步数
times_distribution={}
times_distribution_list =[]
for x in section_list:
    times_result = max(min([math.ceil(level_adjust_need[x]/level_adjust_num[x]),run_limit]),-1*run_limit)
    times_distribution[x] = times_result
    times_distribution_list.append(times_result)

distribution_times_dict = {}
distribution_times = list(set(times_distribution_list))
for num in distribution_times:
    for x in section_list:
        if times_distribution[x] ==num:
            distribution_times_dict.setdefault(num,[]).append(x)
print('调整次数对应的关卡段：',distribution_times_dict)

level_adjust_need_result=df_2['需要调整的步数'].to_dict()
result_dict ={}
for num in distribution_times:
    adjust_level = distribution_times_dict[num]
    for x in adjust_level:
        df_sorted_ = df_sorted
        df_sorted_ = df_sorted_[df_sorted_['关卡分段'] == x].reset_index()
        last_adjust_level = list(df_sorted_[df_sorted_['关卡分段'] == x].reset_index()[:abs(int(last_adjust_steps[x]))]['关卡数'])
        base_adjust_level = list(df_sorted_['关卡数'])
        base_before_level =[x for x in base_adjust_level if x not in last_adjust_level]
        all_level = list(df_1[df_1['关卡分段'] == x]['关卡数'])
        for item_ in all_level:
            if level_adjust_need_result[x]!=0:
                if item_ in base_before_level:
                    result_dict[item_]=(abs(num)-1)*level_adjust_need_result[x]/abs(level_adjust_need_result[x])
                elif item_ in last_adjust_level:
                    result_dict[item_] =abs(num)*level_adjust_need_result[x]/abs(level_adjust_need_result[x])
                else:
                    result_dict[item_] = 0
            else:
                result_dict[item_]=0
sort_result_dic = dict(sorted(result_dict.items(), key=operator.itemgetter(0)))
print('分配结果',sort_result_dic)

# 输出结果
df_result_dict = pd.DataFrame.from_dict(sort_result_dic, orient='index')
df_result_dict.columns=['调整步数']
df_result_dict.to_excel(path + '步数分配结果.xlsx', index=True)
