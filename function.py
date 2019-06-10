# -*- coding: utf-8 -*-
"""
2019运筹学大作业-工厂选址
@Author：孙潇 1752365
python3.7
需要额外安装的库：requests,json,cv2,numpy 
----------------------------------------------------------
  
"""
import requests
import json
import cv2
import numpy as np
import os

def _one_plan(my_origin,my_destination,strategy_i):
    """
    strategy_i=i 数值
    """
    strategy='&strategy={}'.format(str(strategy_i))
    url0='https://restapi.amap.com/v3/direction/driving?'
    origin='&origin='+my_origin
    destination='&destination='+my_destination
    my_key='88551836b6d0f8bd9f5a97dbb57d5741'
    key='key='+my_key
    ##
    url=url0+key+origin+destination+strategy
    html=requests.get(url)
    data=json.loads(html.text)
    
    all_route=''
    
    """
    #是否获得详细坐标数据
    for polyline in data['route']['paths'][0]['steps']:
        all_route=all_route+polyline['polyline']
    """
    ##
    return(data['route']['paths'][0]['distance'],
           float(data['route']['paths'][0]['tolls'])*5,
           all_route)
    """
        收费问题：
        返回的tolls为小轿车收费
        模型假设：
        全国高速小轿车平均收费大致为0.4元一公里
        载重货车收费2元一公里
        所以所有tolls*5
    """

def plan(origin_city,destination_city,print_it=False,need_route=False):
    """
    ###
    调用高德API获得两经纬度之间的驾车路线规划
    ###
    origin_city：出发地  e.g. 上海
    destination_city：目的地  e.g. 北京
    均为中文，字符串形式
    """
    my_origin=_get_coordinate(origin_city)
    my_destination=_get_coordinate(destination_city)
    """
    my_origin,my_destination为经纬度坐标：
        origin:出发地
        destination:目的地
        字符串形式; 经度在前，纬度在后
        e.g. 121.47370,31.23037
        最多6位小数
    ##详细文档：
    https://lbs.amap.com/api/webservice/guide/api/direction/
    """
    strategy_num={0:'速度优先，不考虑路况',
                  1:'费用优先，不走收费路段，且耗时最少的路线',
                  2:'距离优先，不考虑路况，仅走距离最短的路线'}
    """
    strategy_num:各只返回一条路径
    0，速度优先，不考虑当时路况，此路线不一定距离最短
    1，费用优先，不走收费路段，且耗时最少的路线
    2，距离优先，不考虑路况，仅走距离最短的路线
    """
    if print_it==True:
        print('出发地:{}\t坐标：{}\n目的地:{}\t坐标：{}\n-----'.format(origin_city,my_origin,destination_city,my_destination))
    
    result=[]
    for i in range(3):
        (distance,tolls,route)=_one_plan(my_origin,my_destination,i)
        result.append([i,float(distance)/1000,tolls])
        if print_it==True:
            print('策略{}：{}\n距离：{}km\n费用:{}元\n'.format(i+1,strategy_num[i],float(distance)/1000,tolls))
    #print(route)
    return result

def _transportation_expenses_for_one_truck(city1,city2):
    """
    获得两个城市之间的最优运费
    从高德三个策略中选取
    city1，city2为中文城市名，字符
    只返回最终运费
    """
    oil_price=6.72  #每升柴油价格
    truck_per_km=0.4  #货车每公里消耗柴油
    rent_fee=0  #租车费，，司机费用
    #若买车，买车费和路桥费算在一起
    ##
    price_per_km=truck_per_km*oil_price+rent_fee
    plans=plan(city1,city2)
    costs=[]
    for aplan in plans:
        cost=aplan[1]*price_per_km+float(aplan[2])
        costs.append(cost)
    return min(costs)
    
###########################################################

###########################################################

###########################################################
def _base_map_url():
    url0='https://restapi.amap.com/v3/staticmap?'
    my_key='88551836b6d0f8bd9f5a97dbb57d5741'
    key='key='+my_key
    ####################################################
    #地图大小
    zoom='&zoom=5'#缩放级别[1,17] 1比例尺最大
    size='&size=1024*1024'#1024*1024最大
    my_location=_get_coordinate('合肥')
    scale='&scale=1'
    location='&location='+my_location
    
    the_url=url0+key+zoom+size+location+scale
    return the_url
    
def _cv_map(name):
    """
    name='map.png'
    """
    img=cv2.imread(name)
    cv2.namedWindow("map",0)
    cv2.resizeWindow('map',768,768)
    cv2.moveWindow('map',50,50)
    cv2.imshow("map", img)
    cv2.waitKey()
    cv2.destroyAllWindows()    
    
def show_map(factory_str='',show_it=False):
    """
    ###
    显示工厂和四个城市的位置，并连线 
    (生成文件名：final_factory.png)
    若不填，则只显示四个城市  
    (生成文件名:basemap.png)
    ###
    *factory_str=''
    factory_str为城市名称
    e.g.  factory_str='重庆'
    """
    map_url=_base_map_url()
    ####################################################
    ##四个城市标签：(坐标)
    city=['北京','上海','广州','南京']
    beijing=_get_coordinate('北京')
    shanghai=_get_coordinate('上海')
    guangzhou=_get_coordinate('广州')
    nanjing=_get_coordinate('南京')
    coordinates=[beijing,shanghai,guangzhou,nanjing]
    ######
    my_labels=''
    for i in range(4):
        labelstyle='{},0,0,33,0xFFFFFF,0xFF8000'.format(city[i])
        coordinate=':{}'.format(coordinates[i])
        one_label=labelstyle+coordinate
        my_labels=my_labels+one_label
        if i<3:
            my_labels=my_labels+'|'
    labels='&labels='+my_labels
    ####################################################
    #工厂 
    #标记marker
    if factory_str!='':
        ##可选是否显示工厂
        factory=_get_coordinate(factory_str)
        factory_coordinate=':{}'.format(factory)
        markersytle='large,0xFF0000,F'
        markers='&markers='+markersytle+factory_coordinate
    ####################################################
    #工厂与四个城市连线
    #paths
        my_pathstyle='5,0xFFFF00,0.75,,0'
        all_paths=''
        for i in range(4):
            coordinate=':{};{}'.format(factory,coordinates[i])
            one_path=my_pathstyle+coordinate
            all_paths=all_paths+one_path
            if i<3:
                all_paths=all_paths+'|'
        paths='&paths='+all_paths
    ####################################################
        url=map_url+labels+markers+paths
    else:
        url=map_url+labels
        
    html=requests.get(url)

    if factory_str=='':
        map_name='basemap.png'
    else:
        map_name='final_factory.png'
        
    fp=open(map_name,'wb')
    fp.write(html.content)
    fp.close()
    if show_it==True:
        _cv_map(map_name)
    
def _get_coordinate(city_name,print_it=False):
    """
    city_name为中午 字符串形式
    """
    url0='https://restapi.amap.com/v3/geocode/geo?'
    my_key='88551836b6d0f8bd9f5a97dbb57d5741'
    key='key='+my_key
    address='&address='+city_name
    ##
    url=url0+key+address
    html=requests.get(url)
    data=json.loads(html.text)
    ##
    if print_it==True:
        print('{}的经纬度为：{}'.format(city_name,data['geocodes'][0]['location']))
    return(data['geocodes'][0]['location'])

########################################################

########################################################
def _get_one_city_mark(city_name_str):
    """
    获得地图上只有一个城市的mark  绿色
    保存图片名称  one_city_mark.png
    """
    global mark_size
    my_location=_get_coordinate(city_name_str)
    map_url=_base_map_url()
    factory_coordinate=':{}'.format(my_location)
    markersytle='{},0x00FF00,'.format(mark_size)

    markers='&markers='+markersytle+factory_coordinate
    url=map_url+markers
    html=requests.get(url)
    
    fp=open('one_city_mark.png','wb')
    fp.write(html.content)
    fp.close()
    
    #_cv_map('one_city_mark.jpg') 
    
def _is_right_color(frame,rgb=np.array([7,252,8])):
    """
    frame[241 248 251]
    rgb=[241 248 251],<class 'numpy.ndarray'>
    """
    global mark_size
    if mark_size=='small':
        rgb=np.array([26,252,29])
    elif mark_size=='mid':
        rgb=np.array([14,252,15])
    if (frame==rgb).all():
        return True
    else:
        return False

def _is_right_color_hsv(frame,hsv=np.array([])):
    if abs(frame[0]-120)<=10:
        return True
    else:
        return False
    
def _get_mark_xy():
    img=cv2.imread('one_city_mark.png')
    #img_hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    result=[]
    for x in range(len(img)):
        for y in range(len(img[x])):
            #print(img[x][y])
            if _is_right_color(img[x][y]):
                result.append((x,y))
    #print(result)
    return result

def _mark_it_on_map(xy_list,pic_name):
    img=cv2.imread(pic_name)
    for (x,y) in xy_list:
        img[x][y]=np.array([0,0,255])
    cv2.imwrite(pic_name,img)
    
def _mark_all_city(city_list,pic_name,show_it=False):
    show_map()#创建base_map.png.图片
    n=0
    #print(city_list)
    for city in city_list:
        _get_one_city_mark(city)
        mark_list=_get_mark_xy()
        _mark_it_on_map(mark_list,pic_name)
        n+=1
        print('已标记{}个城市'.format(n))
    print('###\n所有城市已标记完成')
    if show_it==True:
        _cv_map(pic_name)
    
def _get_all_city(txt_name):
    """
    txt_name应为存有所有省市数据的txt文档
    格式
    城市名,[地价\n
    ...
    地价应为每平方千米的平均价格
    """
    fp=open(txt_name,'r')
    city_list=[]
    cities=fp.readlines()
    for city in cities:
        city_list.append(city.split(' ')[0])
    return city_list
    
def mark_the_cities(pic_name,city_txt,creat_new=False):
    """
    ###
    将city_txt文档中的所有城市标注在地图上
    ###
    pic_name为标记了所以城市的图片的名称
    city_txt='LandPrice.txt'
    """
    show_map()#创建base_map.png.图片
    if creat_new==True:
        if(os.path.exists(pic_name)):
            os.remove(pic_name)
        os.rename('basemap.png',pic_name)
    city_list=_get_all_city(city_txt)
    _mark_all_city(city_list,pic_name)
########################################################
def deal_with_lingo_data(landPrice_txt,write_type='w',start_number=1):
    """
    ###
    将landPrice.txt文件中的城市及地价和面积做成lingo可以读取的txt文件格式
    ###
    landPrice.txt每一行数据格式：
    城市名 面积1 地价1 面积2 地价2
    用英文空格隔开
    单位：万平方米or万元
    e.g.
    淮北 14768.15 480 186675.25 6030 14768.15 480
    """
    fp=open(landPrice_txt,'r')
    all_data=fp.readlines()
    fp.close()
    factory_supply=[]
    construction_price=[]
    city_list=[]
    for i in range(len(all_data)):
        #print(all_data[i])
        #淮北 14768.15 480 186675.25 6030 14768.15 480\n
        if all_data[i][-1]=='\n':
            the_city=all_data[i][:-1]
        else:
            the_city=all_data[i]
        one_city=the_city.split(' ')
        k=0
        while(k<len(one_city)):
            #删掉列表中因多余的空格导致的空字符
            if one_city[k]=='':
                one_city.remove(one_city[k])
            else:
                k=k+1
        #one_city列表存每一个城市的各种数据 字符型
        #print(one_city)
        for j in range(int((len(one_city)-1)/2)):
            #j*2+1  j*2+2
            S=float(one_city[j*2+1])#面积 单位 平方米
            land_price=float(one_city[j*2+2]) #地价 单位 万元
            supply='{:.4f}'.format(S*0.230769231/10000) #产量 单位 万辆
            price='{:.4f}'.format(land_price+S*0.0846153846)  #总价 单位 万元
            #建设总价=地价+设备厂房建设价
            factory_supply.append((one_city[0],supply))
            construction_price.append((one_city[0],price))
            city_list.append(one_city[0])
        ##
    _write_lingo_data('lingo_factory_supply.txt',factory_supply,write_type=write_type,start_number=start_number)
    _write_lingo_data('lingo_construction_price.txt',construction_price,write_type=write_type,start_number=start_number)
    _write_lingo_cij('lingo_transportation_cij.txt',city_list,write_type=write_type)
    n=0
    lingo_k=[]
    while(n<len(factory_supply)):
        k=float(construction_price[n][1])/float(factory_supply[n][1])
        k='{:.4f}'.format(k)
        lingo_k.append((construction_price[n][0],k))
        n=n+1
    _write_lingo_data('lingo_k.txt',lingo_k,write_type=write_type,start_number=start_number)
    #lingo_k为每万辆的工程建设成本
    fp=open('all_city.txt','w')
    city_set=set(city_list)
    for city in city_set:
        fp.write('{}\n'.format(city))
    fp.close()
    

def _write_lingo_data(data_name_txt,python_data,write_type='w',start_number=1):
    """
    python_data为列表，每个列表元素为(城市名,data)
    """
    if write_type=='w':
        fp=open(data_name_txt,'w')
        fp.write('!此文件为lingo输入数据文件，"!"为注释行;\n!数据格式：工厂产量or建设总费用;\n!单位：\t万辆or万元;\n\n')
    elif write_type=='a':
        fp=open(data_name_txt,'a')
        
    for i in range(len(python_data)):
        fp.write('!index:{} city:{};\n'.format(start_number,python_data[i][0]))
        start_number += 1
        #注明序号和城市名
        fp.write('{}\n'.format(python_data[i][1]))
    fp.close()

def _write_lingo_cij(data_name_txt,city_list,write_type='w'):
    if write_type=='w':
        fp=open(data_name_txt,'w')
        fp.write('!此文件为lingo输入数据文件，"!"为注释行;\n!数据为城市到四个销地的总运费;\n!单位：万元/万辆;\n\n')
    elif write_type=='a':
        fp=open(data_name_txt,'a')
    demand_city=['北京','上海','广州','南京']
    
    def _write(one_city_4demand):
        for one_cost in one_city_4demand:
            fp.write('{:.6f} '.format(one_cost))
        fp.write('\n')
    
    already_gaode_city=[]
    already_gaode_cost={}
    for city in city_list:
        #city为产地
        if city in already_gaode_city:
            pass
        else:
            one_city_4demand=[]
            for demand in demand_city:
                cost=_transportation_expenses_for_one_truck(city,demand)
                one_city_4demand.append(cost/10)
                #cost 每辆货车单次运费 单位：元/辆  同万元/万辆
                #假设每辆货车每次可运10辆小车
            print('已查询完{}的四个路费,现共计{}个城市'.format(city,1+len(already_gaode_city)))
            already_gaode_city.append(city)
            already_gaode_cost[city]=one_city_4demand
            
        _write(already_gaode_cost[city])
            #cost 每辆货车单次运费 单位：元
            #假设每辆货车每次可运10辆小车

    fp.close()
########################################################

########################################################
            
########################################################
if __name__=='__main__':
    global mark_size
    mark_size='large'
    """"
    size可选:
    large mid small
    """
    
    #mark_the_cities('All_city.png','landPrice.txt',creat_new=True)

    #deal_with_lingo_data('landPrice.txt',write_type='w',start_number=1)
    
    #mark_the_cities('area_limited/50years_limited_area.png','area_limited/city_50years.txt',creat_new=True)

    print('all finished')
    pass