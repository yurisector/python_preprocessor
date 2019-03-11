import csv
import os

def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


# 폴더 없으면 폴더만들기
def make_folder(folder_name):
    #각각의 폴더로 나눠줌
    folder_list = folder_name.split('/')
    #각각의 폴더의 경로를 지정해줌
    for i in range(len(folder_list)):
        if i==0: continue
        folder_list[i]=folder_list[i-1]+'/'+folder_list[i]
    #각각의 폴더가 있는지 확인하고 없다면 만들어줌
    for folder in folder_list:
        if not os.path.isdir(folder):
            os.mkdir(folder)

def find_file(cur_dir, file_name):
    for file in os.listdir(cur_dir):
        if file == file_name:
            return 1
    return 0

def tomorrow(date):
    year = int(date / 10000)
    month = int(date / 100) % 100
    day = date % 100
    day_list = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if day == 28 and month == 2 and year % 4 == 0:
        return str(year*10000 + 2*100 + 29)
    elif day == 31 and month == 12:
        return str((year + 1)*10000 + 1*100 + 1)
    elif day >= day_list[month-1]:
        return str(year*10000 + (month+1)*100 + 1)
    else:
        return str(year*10000 + month*100 + day+1)


target_list = ['LinkList_강남순환_1', 'LinkList_강남순환_2', 'LinkList_경부고속_1', 'LinkList_내부순환_1', 'LinkList_내부순환_2',
               'LinkList_내부순환_3', 'LinkList_동부간선_4', 'LinkList_서부간선_1', 'LinkList_서부간선_2']
acc_list = [['사고속보',1], ['공사정보',2]]

AccDataFile = open('AccData.csv', encoding='korean')
Acc = csv.reader(AccDataFile)

stepAcc = -1
for Accline in Acc:
    stepAcc += 1
    if stepAcc == 0: continue
    label = 0
    for accdata in acc_list:
        if accdata[0] == Accline[2]:
            label = accdata[1]
            break
    if label == 0:
        continue

    lon = float(Accline[3])
    lat = float(Accline[4])
    st_time = Accline[12]
    ed_time = Accline[13]
    min_dis = 9999.9999
    LinkID_list = []

    LinkDataFile = open('LinkData.csv', 'r')
    Link = csv.reader(LinkDataFile)
    stepLink = -1
    for Linkline in Link:
        stepLink += 1
        if stepLink == 0: continue
        if Linkline[0] in (None,""):
            break
        cur_dis = distance(float(lon), float(lat), float(Linkline[2]), float(Linkline[3]))

        # 최소거리의 LinkID찾음 이때 여러 linkID에 겹친 점도 찾음
        if cur_dis < min_dis:
            min_dis = cur_dis
            LinkID_list.clear()
            LinkID_list.append(Linkline[0])
        elif min_dis == cur_dis:
            LinkID_list.append(Linkline[0])
    LinkDataFile.close()

    for LinkID in LinkID_list:
        other = 1
        targetNum = 0

        for target in target_list:
            TargetData = open(target + '.csv', 'r')
            Tar = csv.reader(TargetData)

            stepTar = -1
            for Tarline in Tar:
                stepTar += 1
                if stepTar == 0: continue
                if int(LinkID) == int(float(Tarline[0])):
                    other = 0
                    break

            TargetData.close()
            if other == 0: break
            targetNum += 1

            tar = 1
        # 디렉토리를 만들어준다.
        dir_path = ''
        if other == 1:
            dir_path = '5min/others'
        else:
            dir_path = '5min/' + target_list[targetNum]

        make_folder(dir_path)

        fname = ''
        stime_list = []
        etime_list = []

        st = str(st_time)
        ed = str(ed_time)

        while st[0:8] != ed[0:8]:
            stime_list.append(st)
            etime_list.append(st[0:8] + '2355')
            st = tomorrow(int(st[0:8])) + '0000'
        stime_list.append(st)
        etime_list.append(ed)

        for idx in range(len(stime_list)):
            fname = stime_list[idx][0:8]+'_'+LinkID+'_5min.csv'
            t_list = [0] * 288
            if find_file(dir_path,fname):
                outputfile2=open(dir_path+'/'+fname, 'r')
                output2=csv.reader(outputfile2)
                i=-2
                for output2line in output2:
                    i+=1
                    if i == -1: continue
                    t_list[i] = output2line[3]
                outputfile2.close()

            shour = int(stime_list[idx][8:10])
            ehour = int(etime_list[idx][8:10])
            smin = int((int(stime_list[idx][10:12])+4)/5)
            emin = int((int(etime_list[idx][10:12])+4)/5)
            for time in range(shour*12+smin, ehour*12+emin+1):
                if int(t_list[time]) != label:
                    if int(t_list[time])< 3:
                        t_list[time] = str(int(t_list[time]) + label)
                elif int(t_list[time]) == label:
                    continue

            outputfile = open(dir_path+'/'+fname, 'w')
            output = csv.writer(outputfile)
            output.writerow(['date', 'time', 'linkID', 'label'])
            for time in range(len(t_list)):
                a,b = divmod(time, 12)
                output.writerow([stime_list[idx][0:8],str(10000 + a * 100 + b*5)[1:5], LinkID, t_list[time]])
            outputfile.close()
AccDataFile.close()