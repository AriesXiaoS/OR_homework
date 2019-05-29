# OR_homework
big homework of Operations Research in 2019 in Tongji University

同济大学自动化专业运筹学大作业
-----------------
## 问题重述
### 背景
某汽车制造企业TM公司，生产一种轿车
### 销售市场
北京、上海、广州、南京
### 规划管理
#### 工厂选址
考察并决策建厂地点，在满足各销地的需求情况下，使建厂的固定成本和运输费用之和最小？

## 模型假设
### 各地需求：假设四个城市年需求一定
这四个城市作为中国主要大都市，车牌的限购政策已经或者在不久后肯定都会实施，所以假设在未来的每年的年需求量都一样
#### 具体数据来源（于前期思路word文档中）
由2017中国各主要城市汽车保有量
> https://baijiahao.baidu.com/s?id=1595539728686322152&wfr=spider&for=pc

获得者四个城市的2017汽车总量
乘上2017中国汽车保有量增长率 11.85% 作为城市汽车年需求

由2018上海大众车销量/广义乘用车合计 作为此汽车品牌销售占比，作为最终的个城市年需求量
> http://www.sohu.com/a/291095741_662681
#### 最终需求
北京=5.98
上海=3.79
广州=2.53
南京=2.53
单位：万辆

### 固定成本:假设建成的固定成本=工厂建设成本+土地价格
#### 土地价格
土地价格从中国土地市场网获得
> http://www.landchina.com/

##### 城市选择
在调用高德API静态地图缩放级别room=5的地图上
中国中部、东部显示的绝大部分城市

##### 具体价格
查询每个城市的土地出让公告，随机挑选最近发布的两到三个，面积大于一万平方米的土地，
记录土地总面积，土地起始价
其中土地起始价直接作为土地价格

#### 建设成本：假设工厂建设成本与工厂面积成正比，工厂产量与工厂面积成正比
最终还是以上海大众仪征工厂的数据作为参照
> 仪征工厂：位于江苏省仪征市，占地面积128.05万平方米，年产能为30万辆。2012年7月26日投产。总投资11亿 其中6.2亿为设备采购，4.8亿为设备安装和厂房建设

##### 单位面积工厂造价
110000万元/130 0000平方米=0.0846153846万元/平方米
##### 单位面积工厂产量
30万辆/130万平方米=0.230769231 辆/平方米

### 运输费用=油费+路费
#### 运输距离：假设工厂的建设位于城市最中心
为简化模型，假设工厂的建设位于城市最中心，以高德地图直接搜索城市名返回的坐标为准
（城市郊区到市中心的距离相对于两城市之间的距离可以忽略）
#### 获得途径
调用高德API路径规划，获得任意两城市之间的导航方案
##### 油费
导航方案的距离作为行驶距离
> 查询得到每升柴油的价格大约为6.72元 （2019.5.10）
> 百度、知乎查询得到货车每百公里油耗为30-50升，取0.4L/公里

所以最终油费=行驶距离×0.4×6.72

##### 路费
货车路费=导航方案的道路收费×5
> 查询全国高速公路收费情况，大多数省份小轿车收费0.4元/公里，重型货车2元/公里，而
> 因为个人无法获得高德的货车路径规划，所以我们只能使用高德的小轿车驾车规划

##### 最优选择
每两个城市的高德路径规划，分别获得三种导航策略下的方案：
>速度优先，费用优先，距离优先

选择总费用最小者作为这两个城市之间的运输费用


