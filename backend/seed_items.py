"""
种子数据脚本：删除旧商品，生成约 200 个新商品。
用法：cd backend && python seed_items.py
"""
import sys, os, random
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.models import Item, UserAction, Order, CartItem, ItemEmbedding

# ==================== 配置 ====================

CATEGORY_MAP = {
    '04990b17-7c49-42f2-91f4-9226abd879f4': '数码产品',
    '8558e9f8-2212-49f3-9c71-9a40c859779a': '图书教材',
    '61c35377-943d-4c5c-8afc-68b19ae6126b': '运动装备',
    'a0d67dc4-aa41-4c2c-9060-eee5f3a7e432': '生活用品',
    'd9924fff-209c-4bc2-8e31-74deb97ca38a': '服装鞋包',
    '9cbd4f89-c236-4f58-ac43-1e143bc495e4': '其他物品',
}

SELLER_IDS = [1, 2, 3, 4, 5]
LOCATIONS = ['图书馆', '食堂门口', '教学楼', '操场', '宿舍楼']
CONDITIONS = ['全新', '几乎全新', '稍有瑕疵', '7成新以下']

# ==================== 商品数据 ====================

PRODUCTS = {
    '04990b17-7c49-42f2-91f4-9226abd879f4': [  # 数码产品
        ('iPhone 15 Pro Max', '256GB 原色钛金属，电池健康度96%，无划痕', 7999, 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600'),
        ('iPhone 14', '128GB 蓝色，9成新，配件齐全', 4599, 'https://images.unsplash.com/photo-1663499482523-1c0c1bae4ce1?w=600'),
        ('iPhone 13 Pro', '256GB 远峰蓝，电池健康92%', 4299, 'https://images.unsplash.com/photo-1632661674596-df8be070a5c5?w=600'),
        ('iPhone 13', '128GB 星光色，轻微使用痕迹', 3499, 'https://images.unsplash.com/photo-1632661674241-5828f04a6741?w=600'),
        ('iPhone 12', '64GB 黑色，功能正常，电池健康85%', 2299, 'https://images.unsplash.com/photo-1611605698335-8b1569810432?w=600'),
        ('MacBook Pro 14 M3', '16GB+512GB，2024款，带原装充电器', 12999, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600'),
        ('MacBook Air M2', '8GB+256GB，午夜色，几乎全新', 6999, 'https://images.unsplash.com/photo-1611186871348-b1ec696e5237?w=600'),
        ('MacBook Air M1', '8GB+256GB，银色，学生自用', 4999, 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600'),
        ('iPad Pro 12.9 M2', 'WiFi 256GB，带妙控键盘和Apple Pencil', 6999, 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600'),
        ('iPad Air 5', 'WiFi 64GB，紫色，几乎全新', 3499, 'https://images.unsplash.com/photo-1587033411391-5d9e51cce126?w=600'),
        ('iPad mini 6', 'WiFi 64GB，星光色，轻便好用', 2799, 'https://images.unsplash.com/photo-1632634395498-1f3a0e1b1b1a?w=600'),
        ('AirPods Pro 2', 'USB-C版，降噪效果好，带保修', 1299, 'https://images.unsplash.com/photo-1588423771073-b8903fde1c68?w=600'),
        ('AirPods 3', '无线充电盒，音质不错', 799, 'https://images.unsplash.com/photo-1606841837239-c5a1a4a07af7?w=600'),
        ('Apple Watch Series 9', '45mm GPS版，午夜色铝金属', 2499, 'https://images.unsplash.com/photo-1434493907317-a46b53b81822?w=600'),
        ('Apple Watch SE', '44mm GPS版，星光色', 1499, 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600'),
        ('Sony WH-1000XM5', '降噪耳机，黑色，音质极佳', 1899, 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=600'),
        ('小米14', '12GB+256GB，白色，骁龙8Gen3', 2999, 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600'),
        ('华为MatePad Pro', '11英寸，8GB+128GB，带手写笔', 2499, 'https://images.unsplash.com/photo-1585790050230-5dd28404ccb9?w=600'),
        ('三星Galaxy S24', '8GB+256GB，暗影紫', 4299, 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=600'),
        ('Switch OLED', '白色，带3个游戏卡带', 1899, 'https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=600'),
        ('戴尔U2723QE', '27寸4K显示器，Type-C接口', 2999, 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600'),
        ('罗技MX Master 3S', '无线鼠标，办公神器', 499, 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600'),
        ('机械键盘 Cherry MX', '红轴，87键，RGB背光', 399, 'https://images.unsplash.com/photo-1595225476474-87563907a212?w=600'),
        ('索尼A6400微单', '带16-50mm镜头，快门数2万', 4999, 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600'),
        ('大疆Mini 3', '无人机，带遥控器，续航38分钟', 2999, 'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=600'),
        ('Kindle Paperwhite 5', '6.8寸，32GB，几乎全新', 699, 'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600'),
        ('小米移动电源', '20000mAh，支持快充', 99, 'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=600'),
        ('闪迪256GB U盘', 'USB3.2，读速400MB/s', 129, 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600'),
        ('JBL蓝牙音箱', 'Flip 6，防水便携，续航12小时', 599, 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600'),
        ('联想小新Pro 16', 'R7-7840H，16GB+512GB', 4599, 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600'),
        ('华为MateBook 14', 'i5-1340P，16GB+512GB', 4299, 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=600'),
        ('GoPro Hero 12', '运动相机，防水，带自拍杆', 2499, 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600'),
        ('Bose QC45', '降噪耳机，舒适佩戴', 1599, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600'),
        ('小米手环8', 'NFC版，运动健康监测', 199, 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=600'),
        ('漫步者TWS1 Pro', '真无线耳机，降噪，续航好', 249, 'https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=600'),
    ],
    '8558e9f8-2212-49f3-9c71-9a40c859779a': [  # 图书教材
        ('高等数学同济第七版上下册', '考研必备，有少量笔记标注', 35, 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600'),
        ('线性代数同济第六版', '几乎全新，无笔记', 15, 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600'),
        ('概率论与数理统计浙大第四版', '有部分课后答案标注', 18, 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600'),
        ('大学物理马文蔚第六版', '上下册合售，品相好', 30, 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=600'),
        ('C程序设计谭浩强第五版', '计算机入门经典教材', 12, 'https://images.unsplash.com/photo-1515879218367-8466d910auj7?w=600'),
        ('数据结构C语言版严蔚敏', '考研408必备，有笔记', 20, 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600'),
        ('计算机网络谢希仁第八版', '408考研用书，9成新', 25, 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=600'),
        ('操作系统汤小丹第四版', '有课后习题答案', 22, 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=600'),
        ('Python编程从入门到实践', '第三版，适合初学者', 35, 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600'),
        ('算法导论第三版', '经典算法书，中文版', 55, 'https://images.unsplash.com/photo-1550399105-c4db5fb85c18?w=600'),
        ('深入理解计算机系统CSAPP', '程序员必读，第三版', 65, 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=600'),
        ('机器学习周志华西瓜书', '入门机器学习经典', 30, 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=600'),
        ('统计学习方法李航', '第二版，机器学习理论', 28, 'https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=600'),
        ('大学英语四级真题集', '2023-2024年真题，含听力', 15, 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=600'),
        ('六级词汇闪过', '按频率排序，高效背单词', 12, 'https://images.unsplash.com/photo-1491841573634-28140fc7ced7?w=600'),
        ('考研英语黄皮书', '2025版阅读理解专项', 25, 'https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=600'),
        ('张宇考研数学18讲', '2025版，数学一', 35, 'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=600'),
        ('肖秀荣考研政治精讲精练', '2025版全套', 40, 'https://images.unsplash.com/photo-1553729459-afe8f2e2ed08?w=600'),
        ('微观经济学高鸿业第七版', '经管类考研用书', 20, 'https://images.unsplash.com/photo-1554244933-d876deb6b2ff?w=600'),
        ('宏观经济学曼昆第十版', '英文原版，有中文注释', 45, 'https://images.unsplash.com/photo-1589998059171-988d887df646?w=600'),
        ('有机化学邢其毅第四版', '化学专业核心教材', 25, 'https://images.unsplash.com/photo-1532153975070-2e9ab71f1b14?w=600'),
        ('普通生物学陈阅增', '生物专业入门教材', 18, 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=600'),
        ('工程力学刘鸿文', '材料力学部分，有习题解答', 15, 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600'),
        ('电路邱关源第六版', '电子信息类核心课', 20, 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=600'),
        ('模拟电子技术童诗白', '第五版，有实验报告参考', 18, 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=600'),
        ('数字电子技术阎石', '第六版，数电经典教材', 16, 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600'),
        ('信号与系统奥本海姆', '第二版，通信专业必备', 30, 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600'),
        ('自动控制原理胡寿松', '第七版，控制类核心课', 22, 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=600'),
        ('TOEFL官方指南OG', '第六版，托福备考必备', 55, 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=600'),
        ('GRE核心词汇助记与精练', '再要你命3000，背单词神器', 25, 'https://images.unsplash.com/photo-1550399105-c4db5fb85c18?w=600'),
        ('三体全集刘慈欣', '科幻经典，三册合售', 45, 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=600'),
        ('百年孤独马尔克斯', '范晔译本，品相好', 25, 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=600'),
        ('人类简史尤瓦尔赫拉利', '中文版，通识读物', 20, 'https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=600'),
    ],
    '61c35377-943d-4c5c-8afc-68b19ae6126b': [  # 运动装备
        ('Nike Air Force 1', '白色经典款，42码，9成新', 399, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600'),
        ('Adidas Ultraboost 22', '黑色跑鞋，43码，缓震好', 499, 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600'),
        ('李宁跑步鞋飞电3', '竞速跑鞋，42码，穿过几次', 399, 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=600'),
        ('瑜伽垫加厚15mm', 'TPE材质，防滑，送收纳袋', 59, 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600'),
        ('哑铃一对20kg', '可调节重量，包胶防滑', 129, 'https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=600'),
        ('羽毛球拍尤尼克斯', 'ARC-7，进攻型，送球包', 299, 'https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=600'),
        ('乒乓球拍蝴蝶王', '横拍，双面反胶，手感好', 199, 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600'),
        ('篮球斯伯丁官方', '7号球，室内外通用', 129, 'https://images.unsplash.com/photo-1519861531473-9200262188bf?w=600'),
        ('足球阿迪达斯', '5号训练球，耐磨', 89, 'https://images.unsplash.com/photo-1614632537197-38a17061c2bd?w=600'),
        ('网球拍Wilson', '初学者款，带拍包和网球', 199, 'https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=600'),
        ('跳绳专业竞速', '钢丝绳芯，轴承顺滑', 29, 'https://images.unsplash.com/photo-1434682881908-b43d0467b798?w=600'),
        ('泡沫轴肌肉放松', '瑜伽柱，运动后恢复', 39, 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600'),
        ('运动水壶1000ml', '大容量，保温保冷', 49, 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600'),
        ('游泳镜防雾', '高清镜片，硅胶舒适', 59, 'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=600'),
        ('滑板初学者', '双翘板，枫木板面', 159, 'https://images.unsplash.com/photo-1547447134-cd3f5c716030?w=600'),
        ('登山杖碳纤维', '超轻便携，三节可调', 89, 'https://images.unsplash.com/photo-1551632811-561732d1e306?w=600'),
        ('帐篷双人户外', '防雨防风，自动速开', 199, 'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=600'),
        ('运动护膝一对', '篮球跑步用，透气防滑', 49, 'https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=600'),
        ('拉力带健身套装', '5条不同阻力，送收纳袋', 39, 'https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600'),
        ('自行车山地车', '26寸21速，铝合金车架', 599, 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600'),
        ('轮滑鞋成人', '42码，平花鞋，送护具', 259, 'https://images.unsplash.com/photo-1567013127542-490d757e51fc?w=600'),
        ('仰卧起坐辅助器', '吸盘式，家用健身', 29, 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600'),
        ('速干运动T恤', 'L码，透气排汗', 39, 'https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=600'),
        ('运动短裤Nike', 'M码，速干面料', 69, 'https://images.unsplash.com/photo-1562886877-aaaa5c16396e?w=600'),
        ('头戴式运动耳机', '防汗防水，续航10小时', 129, 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600'),
        ('握力器可调节', '10-60kg，锻炼前臂', 25, 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600'),
        ('棒球帽Nike', '可调节大小，遮阳透气', 59, 'https://images.unsplash.com/photo-1588850561407-ed78c334e67a?w=600'),
        ('运动袜6双装', '加厚毛巾底，吸汗', 35, 'https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=600'),
        ('筋膜枪mini', '4档力度，USB充电', 149, 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600'),
    ],
    'a0d67dc4-aa41-4c2c-9060-eee5f3a7e432': [  # 生活用品
        ('戴森V12吸尘器', '无线手持，吸力强劲', 1999, 'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=600'),
        ('小米空气净化器4', '适用30平米，滤芯新换', 499, 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600'),
        ('美的电饭煲3L', '智能预约，内胆无涂层', 149, 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600'),
        ('九阳豆浆机', '免滤免泡，一键操作', 129, 'https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600'),
        ('小熊酸奶机', '1L容量，恒温发酵', 49, 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=600'),
        ('飞利浦电动牙刷', 'HX6730，3种模式，送刷头', 199, 'https://images.unsplash.com/photo-1559591937-abc1f3e8c0c3?w=600'),
        ('台灯护眼LED', '三档调光，USB充电', 59, 'https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?w=600'),
        ('加湿器桌面', '300ml，静音，USB供电', 39, 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600'),
        ('收纳箱3个装', '可折叠，衣物整理', 35, 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600'),
        ('宿舍小风扇', 'USB夹式，3档风速', 29, 'https://images.unsplash.com/photo-1617375407361-9815c98fbeb2?w=600'),
        ('保温杯500ml', '316不锈钢，12小时保温', 69, 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600'),
        ('懒人沙发', '可拆洗，宿舍神器', 89, 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600'),
        ('折叠桌宿舍用', '笔记本电脑桌，床上书桌', 49, 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600'),
        ('衣架50个装', '防滑无痕，加粗款', 19, 'https://images.unsplash.com/photo-1558171813-4c088753af8f?w=600'),
        ('电热水壶1.5L', '304不锈钢，快速烧水', 49, 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600'),
        ('化妆镜带灯', 'LED补光，可旋转', 35, 'https://images.unsplash.com/photo-1522338140262-f46f5913618a?w=600'),
        ('晾衣架落地', '不锈钢，可伸缩折叠', 59, 'https://images.unsplash.com/photo-1558171813-4c088753af8f?w=600'),
        ('床帘遮光', '宿舍上铺下铺通用', 29, 'https://images.unsplash.com/photo-1540518614846-7eded433c457?w=600'),
        ('插排USB', '5孔+3USB，1.8米线', 25, 'https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=600'),
        ('垃圾桶脚踏式', '12L，静音缓降', 29, 'https://images.unsplash.com/photo-1604187351574-c75ca79f5807?w=600'),
        ('雨伞自动折叠', '抗风加固，一键开合', 35, 'https://images.unsplash.com/photo-1534309466160-70b22cc6254d?w=600'),
        ('洗衣液大瓶', '4kg，薰衣草香型', 25, 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=600'),
        ('蓝牙小音箱', '迷你便携，续航8小时', 59, 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600'),
        ('多功能工具刀', '瑞士军刀款，户外实用', 49, 'https://images.unsplash.com/photo-1567361808960-dec9cb578182?w=600'),
    ],
    'd9924fff-209c-4bc2-8e31-74deb97ca38a': [  # 服装鞋包
        ('优衣库羽绒服', 'L码，黑色，轻薄保暖', 299, 'https://images.unsplash.com/photo-1544923246-77307dd270b5?w=600'),
        ('North Face冲锋衣', 'M码，防水防风，户外必备', 499, 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600'),
        ('Levi\'s 501牛仔裤', '32码，经典直筒', 199, 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=600'),
        ('卫衣连帽加绒', 'XL码，灰色，冬季保暖', 79, 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600'),
        ('西装外套修身', 'L码，藏青色，面试穿', 199, 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600'),
        ('连衣裙碎花', 'M码，夏季清新风', 69, 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600'),
        ('风衣中长款', 'L码，卡其色，春秋穿', 159, 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=600'),
        ('格子衬衫', 'M码，纯棉，休闲百搭', 49, 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600'),
        ('运动套装', 'L码，速干面料，跑步健身', 129, 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600'),
        ('毛衣圆领', 'M码，驼色，羊毛混纺', 89, 'https://images.unsplash.com/photo-1434389677669-e08b4cda3a0a?w=600'),
        ('Polo衫短袖', 'L码，白色，商务休闲', 59, 'https://images.unsplash.com/photo-1625910513413-5fc421e0fd6f?w=600'),
        ('双肩背包', '大容量，防水面料，电脑隔层', 129, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600'),
        ('帆布包托特', '文艺风，大容量，上课用', 39, 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=600'),
        ('斜挎包小众', '复古风，PU皮质', 69, 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600'),
        ('行李箱20寸', '万向轮，TSA锁，登机箱', 199, 'https://images.unsplash.com/photo-1565026057447-bc90a3dceb87?w=600'),
        ('匡威帆布鞋', '经典黑色高帮，41码', 199, 'https://images.unsplash.com/photo-1463100099107-aa0980c362e6?w=600'),
        ('马丁靴女', '38码，黑色8孔，秋冬穿', 169, 'https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=600'),
        ('拖鞋室内', '棉拖鞋，42-43码，保暖', 15, 'https://images.unsplash.com/photo-1603487742131-4160ec999306?w=600'),
        ('棒球帽潮牌', '可调节，刺绣logo', 39, 'https://images.unsplash.com/photo-1588850561407-ed78c334e67a?w=600'),
        ('围巾羊绒', '纯色驼色，柔软保暖', 79, 'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=600'),
        ('墨镜偏光', 'UV400防护，开车户外', 59, 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600'),
        ('手套触屏', '加绒保暖，可操作手机', 25, 'https://images.unsplash.com/photo-1545170241-e489b4e98484?w=600'),
        ('腰带真皮', '自动扣，商务休闲两用', 49, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600'),
        ('袜子礼盒装', '10双，纯棉中筒', 35, 'https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=600'),
    ],
    '9cbd4f89-c236-4f58-ac43-1e143bc495e4': [  # 其他物品
        ('吉他民谣41寸', '云杉面板，送琴包调音器', 399, 'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=600'),
        ('尤克里里23寸', '桃花芯木，适合入门', 129, 'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?w=600'),
        ('口琴24孔', 'C调，初学者练习用', 39, 'https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=600'),
        ('素描画板套装', '含铅笔橡皮炭笔，美术生用', 49, 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600'),
        ('水彩颜料36色', '固体水彩，送画笔水壶', 59, 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=600'),
        ('马克笔80色', '双头油性，动漫手绘', 69, 'https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=600'),
        ('拼图1000片', '风景画，减压神器', 29, 'https://images.unsplash.com/photo-1494059980473-813e73ee784b?w=600'),
        ('乐高积木城市系列', '警察局，拼装完整', 149, 'https://images.unsplash.com/photo-1587654780291-39c9404d7dd0?w=600'),
        ('桌游卡坦岛', '基础版+海洋扩展，中文版', 99, 'https://images.unsplash.com/photo-1606503153255-59d8b8b82176?w=600'),
        ('魔方三阶磁力', 'GAN356，竞速用', 89, 'https://images.unsplash.com/photo-1577401239170-897942555fb3?w=600'),
        ('手账本A5', '活页本，送贴纸胶带', 25, 'https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=600'),
        ('钢笔英雄616', '经典款，送墨水', 15, 'https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=600'),
        ('台历2025', '简约风，桌面摆件', 10, 'https://images.unsplash.com/photo-1506784365847-bbad939e9335?w=600'),
        ('多肉植物组合', '5盆含花盆，好养活', 35, 'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=600'),
        ('鱼缸小型桌面', '带过滤灯光，养小鱼', 59, 'https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?w=600'),
        ('棋盘围棋套装', '实木棋盘+云子', 79, 'https://images.unsplash.com/photo-1585504198199-20277593b94f?w=600'),
        ('象棋实木', '大号，红木棋子', 49, 'https://images.unsplash.com/photo-1586165368502-1bad9cc4be3e?w=600'),
        ('望远镜双筒', '10x42，户外观鸟', 199, 'https://images.unsplash.com/photo-1502920514313-52581002a659?w=600'),
        ('打印机惠普', '彩色喷墨，WiFi打印', 299, 'https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=600'),
        ('计算器卡西欧', 'fx-991CN，考试专用', 59, 'https://images.unsplash.com/photo-1564466809058-bf4114d55352?w=600'),
        ('电子词典卡西欧', 'E-XA800，英日双语', 499, 'https://images.unsplash.com/photo-1555431189-0fabf2667795?w=600'),
        ('投影仪便携', '1080P，支持WiFi投屏', 599, 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=600'),
        ('麻将牌家用', '42mm大号，送桌布', 69, 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600'),
        ('扑克牌德州', '塑料防水，2副装', 15, 'https://images.unsplash.com/photo-1541278107931-e006523892df?w=600'),
    ],
}

def seed():
    app = create_app()
    with app.app_context():
        print("=== 删除旧数据 ===")
        CartItem.query.delete()
        Order.query.delete()
        UserAction.query.delete()
        ItemEmbedding.query.delete()
        Item.query.delete()
        db.session.commit()
        print("旧数据已清除")

        print("=== 插入新商品 ===")
        count = 0
        now = datetime.now()
        for cat_id, products in PRODUCTS.items():
            for name, desc, price, img in products:
                item = Item(
                    name=name,
                    description=desc,
                    price=price,
                    images=[img],
                    category_id=cat_id,
                    seller_id=random.choice(SELLER_IDS),
                    location=random.choice(LOCATIONS),
                    condition=random.choice(CONDITIONS),
                    status='on_sale',
                    created_at=now - timedelta(days=random.randint(0, 60),
                                               hours=random.randint(0, 23)),
                )
                db.session.add(item)
                count += 1
        db.session.commit()
        print(f"成功插入 {count} 个商品")


if __name__ == '__main__':
    seed()
