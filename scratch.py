import csv
import os


# 주의할점
# scv에서 읽은 정보는 str형으로 나온다 1234라도 '1234'로 나옴
# 한글제목의 scv의 경우 1234가 1234.0이라는 str형식으로 나온다.
# 따라서 str->float->int로 바꾸는 작업이 필요하다


# 두점사이의 거리
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

#파일이 해당 디렉토리에 있다면 1 없다면 0
def find_file(cur_dir, file_name):
    for file in os.listdir(cur_dir):
        if file == file_name:
            return 1
    return 0

# 다음날
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
acc_list = [['사고속보',1], ['공사정보',2]] #만약 행사를 넣는다면 4로넣음(이진수)


AccDataFile = open('AccData.csv', encoding='korean')  # 한글이 있어서 파일이 깨짐(맥에서만 그러는지 모르겠음)
Acc = csv.reader(AccDataFile)


stepAcc = -1  # 0번째 설명줄 삭제를 위해 for문에 i를 넣고 작성하면 i의 숫자가 튄다.(csv.reader함수의 작동법인듯)
for Accline in Acc:
    stepAcc += 1
    if stepAcc == 0: continue
    print(Accline)
    #label해줌 처리하지 않을 데이터면 제외시켜줌
    #label = stepAcc%2

    #한글파일 깨짐 문제

    label = 0
    for accdata in acc_list:  #라벨링하는 for문입니다.
        print(accdata)
        if accdata[0] == Accline[2]:
            label = accdata[1]
            print(str(label) + 'here is the label')
            break
    if label == 0:
        continue

    lon = float(Accline[3])
    lat = float(Accline[4])
    st_time = Accline[12]
    ed_time = Accline[13]

    min_dis = 9999.9999  # double 최대값
    LinkID_list = []

    #LinkDataFile은 포문 안에서 읽어야합니다. 여기도 밑에까지 함수로 빼내세요
    LinkDataFile = open('LinkData.csv', 'r')
    Link = csv.reader(LinkDataFile)
    stepLink = -1
    for Linkline in Link:
        print(Linkline)
        stepLink += 1
        if stepLink == 0: continue
        if Linkline[0] in (None,""):
            break
        cur_dis = distance(float(lon), float(lat), float(Linkline[2]), float(Linkline[3]))
        print(str(cur_dis) + 'here is the cur_dis')
        # 최소거리의 LinkID찾음 이때 여러 linkID에 겹친 점도 찾음
        if cur_dis < min_dis:
            min_dis = cur_dis
            LinkID_list.clear()
            LinkID_list.append(Linkline[0]) #linkline 1 이 아니고 0 입니다. 1은 gps
            print(str(Linkline[0]) + 'here is the linkline being searched')
        elif min_dis == cur_dis:
            LinkID_list.append(Linkline[0]) #오잉 같은 거리의 링크 (gps기준 겹쳐짐)을 찾았어요!
            print(str(Linkline[0]) +'here is the linkline double searched')
    LinkDataFile.close()
    #여기까지 LinkDataFile 읽는 부분 함수로 빼내기

    # 찾은 최소거리의 LinkID가 속한 target file찾음. 그리고 파일을 만들어줌
    for LinkID in LinkID_list: #이거 두번 이상 돌아가면 사고가 하필 링크의 접점에서 일어나서 링크 두 개가 해당 한다는 내용입니다.
        other = 1
        targetNum = 0
        print(str(LinkID) +'here is the linkID')
        for target in target_list:
            TargetData = open(target + '.csv', 'r')
            Tar = csv.reader(TargetData)

            stepTar = -1
            for Tarline in Tar:
                stepTar += 1
                if stepTar == 0: continue
                if int(LinkID) == int(float(Tarline[0])):  # target파일이 한글파일이라 숫자가 깨져서 나온다 그래서 str->float->int형으로 바꿔줌
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

        # 두개의 사고가 동일한 날에 같은 링크에 영향을 미치면 만들었던 파일을 수정해야하는 문제가 생긴다.
        # 이미 적어놓은 파일을 읽고 그 내용을 토대로 새로 만들어야한다.
        # 혹은 모든 사고 데이터를 다 저장하여 처리해야하는데 사고 데이터가 너무 많아 불가능하다
        fname = ''
        stime_list = []
        etime_list = []

        st = str(st_time)
        ed = str(ed_time)
        # 여러날에 걸친 사건을 나눠준다.
        while st[0:8] != ed[0:8]:
            stime_list.append(st)
            etime_list.append(st[0:8] + '2355')
            st = tomorrow(int(st[0:8])) + '0000'
        stime_list.append(st)
        etime_list.append(ed)

        # 위에서만든 여러날에 걸친 사건을 파일로 만들어준다.
        for idx in range(len(stime_list)):
            print(str(idx) + 'here is the index')
            fname = stime_list[idx][0:8]+'_'+LinkID+'_5min.csv'
            t_list = [0] * 288
            # 이미 파일이 있는경우 파일을 t_list에 복사해준다.
            if find_file(dir_path,fname):
                outputfile2=open(dir_path+'/'+fname, 'r') #디렉토리 패스를 추가해줘야 잘 오픈할 수 있다.
                output2=csv.reader(outputfile2)
                i=-2
                for output2line in output2: #t_list[time] 이 들어갔다 나온거만 더해지는 이유는 뭘까 한번 int로 캐스트 했으면 계속 바까조야혀
                    i+=1
                    if i == -1: continue
                    t_list[i] = output2line[3]
                outputfile2.close()
            #stime_list와 etime_list값을 t_list와 합해준다.
            #시간과 분 단위를 5분단위의 값 288개로 나눈다.

            shour = int(stime_list[idx][8:10])
            ehour = int(etime_list[idx][8:10])
            smin = int((int(stime_list[idx][10:12])+4)/5)
            emin = int((int(etime_list[idx][10:12])+4)/5)
            for time in range(shour*12+smin, ehour*12+emin+1): #시간 계산 알고리즘
                # 해당 라벨의 값이 0이면 더해준다. 열었던 파일 일 수도 있고 아닐 수도 있겠지만 일단은 0으로 라벨링한다 사고속보와 공사정보는 나뉘어야한다
                if int(t_list[time]) != label:  # 같지않으면 일단 더해도 된다. 중복 검사 알고리즘도 동시에 작동합니다.
                    if int(t_list[time])< 3:  # 이미 더해 줄 대로 더해 줬다
                        t_list[time] = str(int(t_list[time]) + label)  # 캐스팅 지옥인데?
                        print(label)
                        print('here is below label')
                elif int(t_list[time]) == label:  # 같은 유형의 사건사고는 그냥 넘김
                    continue

            #t_list의 정보를 토대로 파일 만듬
            outputfile = open(dir_path+'/'+fname, 'w')
            output = csv.writer(outputfile)
            output.writerow(['date', 'time', 'linkID', 'label'])
            for time in range(len(t_list)):
                #여기서부터
                a,b = divmod(time, 12)
                output.writerow([stime_list[idx][0:8],str(10000 + a * 100 + b*5)[1:5], LinkID, t_list[time]])
                #여기까지 함수로 빼내기 time_stamp(time, stime_List, LinkID, t_list)
            outputfile.close()
AccDataFile.close()