person_schema = [
    ['alternative name','别名', [
        ['P1477', 'birth name','出生姓名'],['P1559', 'name in native language', '母语人名'], ['P2093', 'author name string','作者姓名字符串'],
        ['P1814', 'name in kana','日语假名'], 
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['ancestral home','籍贯', [['P66','ancestral home','籍贯'],]],
    ['country of citizenship','国籍',[['P27','country of citizenship','国籍'],]],
    ['place of birth','出生地点', [['P19','place of birth','出生地'],]],
    ['place of death','死亡地点',[['P20','place of death','死亡地点'],['P119','place of burial','墓地'],]],
    ['date of birth','出生日期',[['P569', 'date of birth', '出生日期'],]],
    ['date of death','死亡日期', [['P570', 'date of death','死亡日期'],]],
    ['work','作品',[
        ['P1686','for work','得奖作品'],['P800','notable work','主要作品'],['P50','author','作者'],['P161','cast member','演员'],
        ['P175','performer','表演者'],['P57','director','导演'],['P162','producer','制作人'],['P86','composer','作曲者'],
        ['P676','lyrics by','作词者'],['P58','screenwriter','编剧'],['P3919','contributed to creative work','贡献至发行作品'],
        ]
    ],
    ['occupation','职业',[['P106','occupation','职业'],]],
    ['position held','职务',[
        ['P39','position held','职务'],['P413','position played on team / speciality','球员在球队中的专长'],
        ['P97','noble title','贵族头衔'],['P410','military rank','军衔'],
    ]
    ],
    ['achievement','成就',[['P166','award received','所获奖项'],['P1027','conferred by','授予']]],
    ['member of','所属组织',[
        ['P463','member of','所属组织'],['P108','employer','雇主'],['P118','league','所属联盟'],['P54','member of sports team','效力运动队'],
        ['P1268','represents','代表对象'],['P1416','affiliation','所属机构'],['P945','allegiance','效忠对象'],['P69','educated at','就读学校'],
        ['P102','member of political party','政党成员'],['P4100','parliamentary group','党团'],['P112','founded by','创办者'],
        ]
    ],
    ['parent','父母',[['P40','child','子女'],['P22','father','父亲'],['P25','mother','母亲'],]],
    ['spouse','配偶',[['P26','spouse','配偶'],]],
    ['sibling','兄弟姊妹',[['P3373','sibling','兄弟姊妹'],]],
    ['other','其他',[
        ['P155','follows','前任'],['P1365','replaces','取代'],['P551','residence','居住地'],
        ['P2868','subject has role','主体角色'],['P1441','present in work','出场作品'],
        ['P937','work location','工作地点'],['P6902','era name','年号'],['P156','followed by','后继者'],
        ['P453','character role','人物角色'],['P674','characters','角色'],['P734','family name','姓'],
        ['P169','chief executive officer','首席执行官'],['P35','head of state','国家元首'],['P361','part of','从属于'],
        ['P6087','coach of sports team','运动队教练'],['P6','head of government','政府首脑'],
        ['P286','head coach','主教练'],['P2632','place of detention','拘留场所'],['P451','unmarried partner','非婚伴侣'],
        ['P31','instance of','隶属于'],['P735','given name','人名'],['P541','office contested','竞选职位'],['P642','of','属于'],

        ['P509','cause of death','死因'],['P264','record label','唱片公司'],
        ['P1782', 'courtesy name','表字'],['P1787','art-name','号'],['P1785', 'temple name','庙号'], ['P1786', 'posthumous name','谥号'], 
        ['P1344','participant in','参与'],['P710','participant','参与者'],['P2715','elected in','当选选举'],
        ['P726','candidate','候选人'],['P5021','assessment','参与考试'],['P793','significant event','重大事件'],['P512','academic degree','学位'],
        ['P2650','interested in','研究领域'],['P101','field of work','工作领域'],['P172','ethnic group','种族'],
        ]
    ],
]

person_reverse_list = [
    ['P50','author','作者'],['P161','cast member','演员'],['P175','performer','表演者'],
    ['P57','director','导演'],['P162','producer','制作人'],['P86','composer','作曲者'],
    ['P676','lyrics by','作词者'],['P58','screenwriter','编剧'],['P169','chief executive officer','首席执行官'],
    ['P35','head of state','国家元首'],['P6087','coach of sports team','运动队教练'],['P6','head of government','政府首脑'],
    ['P286','head coach','主教练'],['P710','participant','参与者'],['P726','candidate','候选人'],
    ['P112','founded by','创办者'],['P40','child','子女'],['P1027','conferred by','授予']
]
person_limit = {
    ('alternative name', '别名'): (['人物', '生物'], []), 
    ('ancestral home', '籍贯'): ([], []), 
    ('country of citizenship', '国籍'): ([], []), 
    ('place of birth','出生地点'): ([], []), 
    ('place of death', '死亡地点'): ([], []), 
    ('date of birth', '出生日期'): ([], []), 
    ('date of death','死亡日期'): ([], []), 
    ('work', '作品'): (['人物', '生物'], ['产品','其他','度量1']), 
    ('occupation', '职业'): (['人物', '生物'], []), 
    ('position held', '职务'): (['人物', '生物'], []), 
    ('achievement', '成就'): (['人物', '生物'], []), 
    ('member of', '所属组织'): (['人物','生物'], []), 
    ('parent', '父母'): ([], []), 
    ('spouse', '配偶'): ([], []), 
    ('sibling', '兄弟姊妹'): ([], []), 

     ('ethnic group', '种族'): (['人物', '生物'], []), 
    ('field of work', '工作领域'): (['人物', '生物'], []), 
    ('interested in', '研究领域'): (['人物', '生物'], []), 
    ('academic degree', '学位'): (['人物', '生物'], []), 
    ('relative', '亲属'): ([], []), 
    ('colleague', '同事'): ([], []), 
    ('participant in', '参与'): (['人物','生物'], []), 
    ('nominated for', '提名或入围奖项'): (['人物', '生物'], []), 
    ('cause of death', '死因'): ([], []), 
    ('record label', '唱片公司'): ([], []),
    ('art-name','号'): (['人物', '生物', '其他', '度量1'], []), 
    ('courtesy name','表字'): (['人物', '生物', '其他', '度量1'], []),
    ('temple name','庙号'): (['人物', '生物', '其他', '度量1'], []),
    ('posthumous name','谥号'): (['人物', '生物', '其他', '度量1'], []),
}



location_schema = [
    ['alternative name','别名', [
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['located in','位于',[
        ['P131','located in the administrative territorial entity','所在行政领土'],['P17','country','国家'],
        ['P150','contains the administrative territorial entity','包含行政领土'], ['P30','continent','大洲'],
        ['P706','located in/on physical feature','所处地理环境'],['P6375','street address','所在街道'],
        ]
    ],
    ['length','长度',[['P2043','length','长度'],]],
    ['width','宽度',[['P2049','width','宽度'],]],
    ['height','高度', [['P2048','height','高度'],]],
    ['area','面积',[['P2046','area','面积'],]],
    ['population','人口',[['P1082','population','人口'],]],
    ['capital','行政中心',[['P1376','capital of','首府'],['P36','capital','行政中心'],]],      # 首府实际是“是…的首府”
    ['elevation above sea level', '海拔', [['P2044', 'elevation above sea level', '海拔'],]],
    ['other','其他',[
        ['P1365','replaces','取代'],['P3005','valid in place','有效地点'],['P1001','applies to jurisdiction','管辖区'],
        ['P4330','contains','包含'],['P31','instance of','隶属于'],['P642','of','属于'],['P7938','associated electoral district','所属选区'],
        ['P527','has part(s)','可分为'],['P47','shares border with','接壤'],['P136','genre','类型'],['P518','applies to part','适用部分'],
        
        ['P4552','mountain range','所属山脉'],['P200','inflows','流入水域'],['P403','mouth of the watercourse','河流出口'],
        ['P469','lake on watercourse','流经湖泊'],['P201','lake outflow','流出河流'],['P885','origin of the watercourse','水源'],
        ['P206','located in or next to body of water','相邻水体'],['P138','named after','名称由来'],
        ]
    ],
]
location_reverse_list = [
    ['P150','contains the administrative territorial entity','包含行政领土'],['P4330','contains','包含'],['P710','participant','参与者'],
    ['P1376','capital of','首府'],
]
location_limit = {
    ('alternative name', '别名'): (['地理地区', '其他', '建筑结构', '运输','组织'], []), 
    ('located in', '位于'): (['地理地区', '其他', '建筑结构', '运输','组织'], []), 
    ('area', '面积'): (['地理地区', '其他', '建筑结构', '运输','组织'], []), 
    ('length','长度'): (['地理地区', '其他', '建筑结构', '运输','组织'], []), 
    ('width','宽度'): (['地理地区', '其他', '建筑结构', '运输','组织'], []), 
    ('height','高度'): (['地理地区', '其他', '建筑结构', '运输','组织'], []), 
    ('population', '人口'): (['地理地区', '其他', '建筑结构', '运输','组织'], []), 
    ('capital', '行政中心'): (['地理地区', '其他', '建筑结构', '运输','组织'], []), 
    ('elevation above sea level', '海拔'): (['地理地区', '其他', '建筑结构', '运输','组织'], []), 
   
    ('industry', '产业'): (['地理地区', '其他', '组织', '建筑结构', '运输', '组织'], []), 
    ('mountain range', '所属山脉'): (['地理地区', '其他', '组织', '运输', '建筑结构'], []), 
    ('inflows', '流入水域'): (['地理地区', '其他', '组织', '运输', '建筑结构'], []), 
    ('mouth of the watercourse', '河流出口'): (['地理地区', '其他', '组织', '运输', '建筑结构'], []), 
    ('lake on watercourse', '流经湖泊'): (['地理地区', '其他', '组织', '运输', '建筑结构'], []), 
    ('lake outflow', '流出河流'): (['地理地区', '其他', '组织', '运输', '建筑结构'], []), 
    ('origin of the watercourse', '水源'): (['地理地区', '其他', '组织', '运输', '建筑结构'], []), 
    ('located in or next to body of water', '相邻水体'): (['地理地区', '其他', '组织', '运输', '建筑结构'], []), 
    ('named after', '名称由来'): (['地理地区', '其他', '运输', '组织', '建筑结构'], []), 
    ('part of', '从属于'): (['地理地区', '其他', '组织', '运输', '建筑结构'], [])
}




building_schema = [
    ['alternative name','别名', [
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['located in','位于',[
        ['P131','located in the administrative territorial entity','所在行政领土'],['P17','country','国家'],
        ['P150','contains the administrative territorial entity','包含行政领土'],['P276','location','位置'],
        ['P6375','street address','所在街道'],
        ]
    ],
    ['named after','名称由来',[['P138','named after','名称由来'],]],
    ['length','长度',[['P2043','length','长度'],]],
    ['width','宽度',[['P2049','width','宽度'],]],
    ['height','高度',[['P2048','height','高度'],]],
    ['area','面积',[['P2046','area','面积'],]],
    ['creation time','创建时间',[['P10786', 'date of incorporation' ,'成立日期'],['P571', 'inception','成立或创建时间'],['P580', 'start time', '始于']]],
    ['creator','创建者',[['P84','architect','建筑师'],['P112','founded by','创办者']]],
    ['achievement','成就',[
        ['P1435','heritage designation','文化遗产名称'],['P166','award received','所获奖项'],['P1027','conferred by','授予'],
        ['P972','catalog','目录']
        ]
    ],
    ['event','事件',[['P793','significant event','重大事件'],]],
    ['other','其他',[
        ['P4330','contains','包含'],['P361','part of','从属于'],['P642','of','属于'],['P931','place served by transport hub','机场服务地区'],
        ['P706','located in/on physical feature','所处地理环境'],['P47','shares border with','接壤'],
        ['P31','instance of','隶属于'],['P279','subclass of','上级分类'],['P136','genre','类型'],['P159','headquarters location','总部位置'],

        ['P127','owned by','拥有者'],['P137','operator','运营者'],['P466', 'occupant', '占用者'],['P708','diocese','教区'],['P547', 'commemorates', '纪念对象'],
        ['P137','operator','运营者'],['P177','crosses','跨越'],['P149','architectural style','建筑风格'],
        ]
    ],
]
building_reverse_list = [
    ['P361','part of','从属于'],['P642','of','属于'],['P150','contains the administrative territorial entity','包含行政领土'],
    ['P1027','conferred by','授予']
]
building_limit = {
    ('alternative name', '别名'): (['建筑结构', '组织', '专业','产品','其他','运输'], []), 
    ('located in', '位于'): (['建筑结构', '组织', '地理地区','专业','产品','其他','运输'], []), 
    ('named after', '名称由来'): (['建筑结构', '组织', '专业','产品','其他','运输'], []), 
    ('length', '长度'): ([], []), 
    ('width', '宽度'): ([], []), 
    ('height', '高度'): ([], []), 
    ('area', '面积'): ([], []), 
    ('creation time', '创建时间'): (['建筑结构', '组织', '专业','产品','其他','运输'], []), 
    ('creator', '创建者'): (['建筑结构', '组织', '专业','产品','其他','运输'], []), 
    ('achievement', '成就'): (['建筑结构', '组织', '专业','产品','其他',], []), 
    ('event', '事件'): (['建筑结构', '组织', '产品','其他','运输'], []), 
    
    ('place served by transport hub', '机场服务地区'): (['建筑结构', '组织', '产品','其他'], []), 
    ('owned by', '拥有者'): (['建筑结构', '组织', '产品','其他','运输'], []), 
    ('diocese', '教区'): (['建筑结构', '组织', '产品','其他'], []), 
    ('operator', '运营者'): (['建筑结构', '组织', '产品','其他','运输'], []), 
    ('crosses', '跨越'): (['建筑结构', '组织', '产品','其他','运输'], []), 
    ('architectural style', '建筑风格'): (['建筑结构', '组织', '产品','其他','运输'], []), 
    ('commemorates', '纪念对象'): (['建筑结构', '组织', '产品','其他'], [])
}


        
product_schema = [
    ['alternative name','别名', [
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['achievement','成就',[['P166','award received','所获奖项'],['P1027','conferred by','授予'],]],
    ['brand','品牌',[['P1716','brand','品牌'],]],
    ['country of origin','产地',[
        ['P495','country of origin','原产地'],['P291','place of publication','出版地'],['P1071','location of creation','创作地'],
        ]
    ],
    ['length','长度',[['P2043','length','长度'],]],
    ['width','宽度',[['P2049','width','宽度'],]],
    ['height','高度',[['P2048','height','高度'],]],
    ['mass','质量',[['P2067','mass','质量'],]],
    ['price','价值',[['P2284','price','价值'],]],
    ['manufacturer','制造商',[
        ['P272','production company','制作商'],['P176','manufacturer','生产商'],
        ['P1056','product or material produced','产品'],['P287','designed by','设计者'],['P2378','issued by','发行者'],
        ]
    ],
    ['made from material','材料',[['P186','made from material','材料'],['P1582','natural product of taxon','产自'],]],
    ['has use','用途',[['P366','has use','用途'],]],
    ['discoverer or inventor','发现者或发明者',[['P61','discoverer or inventor','发现者或发明者'],]],

    ['other','其他',[
        ['P642','of','属于'],['P279','subclass of','上级分类'],['P31','instance of','隶属于'],['P136','genre','类型'],
        ['P361','part of','从属于'],['P17','country','国家'],

        ['P137','operator','运营者'],['P138','named after','名称由来'],['P8324','funder','赞助商'],['P580', 'start time', '始于'],['P577','publication date','出版日期'],
        ['P859','sponsor','赞助者'],['P750','distributed by','经销商'],['P178','developer','开发者'],['P306','operating system','操作系统'],
        ['P289','vessel class','船级'],['P2360','intended public','受众'],['P179','part of the series','所属系列'],['P7075','mod of','型号'],
        ]
    ],

]
product_reverse_list = [
    ['P1056','product or material produced','产品'],['P1027','conferred by','授予'],
]
product_limit = {
    ('alternative name', '别名'): (['产品','运输','其他'], []), 
    ('intended public', '受众'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('achievement', '成就'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('brand', '品牌'): ([], []), 
    ('country of origin', '产地'): ([], []), 
    ('length', '长度'): ([], []), 
    ('width', '宽度'): ([], []), 
    ('height', '高度'): ([], []), 
    ('mass', '质量'): ([], []), 
    ('price', '价值'): ([], []), 
    ('manufacturer', '制造商'): ([], []), 
    ('made from material', '材料'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('has use', '用途'): ([], []), 
    ('discoverer or inventor', '发现者或发明者'): ([], []), 

    ('mod of', '型号'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('date of manufacture', '生产日期'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('operator', '运营者'): (['产品','运输','其他','事件'], []), 
    ('named after', '名称由来'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('funder', '赞助商'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('sponsor', '赞助者'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('distributed by', '经销商'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('developer', '开发者'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('operating system', '操作系统'): (['产品','运输','其他','建筑结构','度量1','生物','专业'], []), 
    ('vessel class', '船级'): ([], [])
}



creature_schema = [
    ['alternative name','别名', [
        ['P1420','taxon synonym','同物异名'], 
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['taxon name','学名',[['P225','taxon name','学名'],['P566','basionym','基名'],['P1843', 'taxon common name','生物俗名']]],
    ['distribution','分布',[
        ['P9714','taxon range','物种分布'],['P495','country of origin','原产地'],['P189','location of discovery','发现地点'],
        ['P2341','indigenous to','原产于'],['P5304','type locality (biology)','模式产地（生物）'],
        ]
    ],
    ['parent taxon','父级分类单元',[
        ['P279','subclass of','上级分类'],['P171','parent taxon','父级分类单元'],['P427','taxonomic type','模式分类'],
        ['P361','part of','从属于'],['P4330','contains','包含'],
        ['P1531','parent of this hybrid, breed, or cultivar','此杂交种、品种的父系'],
        ]
    ],
    ['main food source','主要食物来源',[['P1034','main food source','主要食物来源'],]],
    ['has use','用途',[['P366','has use','用途'],]],
    ['length','长度',[['P2043','length','长度'],]],
    ['width','宽度',[['P2049','width','宽度'],]],
    ['height','高度',[['P2048','height','高度'],]],
    ['weight','质量',[['P2067','weight','重量'],]],
    ['diameter','直径',[['P2386','diameter','直径'],]],

    ['other','其他',[['P31','instance of','隶属于'],['P136','genre','类型'],['P105','taxon rank','分类等级'],['P2974','habitat','栖息地']]],
]
creature_reverse_list = [
    ['P427','taxonomic type','模式分类'],['P4330','contains','包含'],
]
creature_limit = {
    ('alternative name', '别名'): (['生物'], []), 
    ('taxon name', '学名'): (['生物','其他'], []), 
    ('distribution', '分布'): (['生物','其他'], []), 
    ('parent taxon', '父级分类单元'): (['生物','其他'], []), 
    ('main food source', '主要食物来源'): ([], []), 
    ('has use', '用途'): (['生物'], []), 
    ('length', '长度'): (['生物'], []), 
    ('width', '宽度'): (['生物'], []), 
    ('height', '高度'): (['生物'], []), 
    ('weight', '重量'): (['生物'], []), 
    ('diameter', '直径'): (['生物'], []), 

    ('taxon rank', '分类等级'): ([], []), 
    ('habitat', '栖息地'): ([], [])
}
    



star_schema = [
    ['alternative name','别名', [
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['discoverer','发现者或发明者',[['P61','discoverer','发现者或发明者'],]],
    ['time of discovery','发现时间',[['P575', 'time of discovery or invention', '发现或发明时间'],]],
    ['named after','名称由来',[['P138','named after','名称由来'],['P3938', 'named by', '命名者'],]],
    ['of','属于',[['P59','constellation','星座'],['P361','part of','从属于'],['P642','of','属于'],]],
    ['diameter','直径',[['P2386','diameter','直径'],]],
    ['length','长度',[['P2043','length','长度'],]],
    ['width','宽度',[['P2049','width','宽度'],]],
    ['height','高度',[['P2048','height','高度'],]],
    ['mass','质量',[['P2067','mass','质量'],]],
    ['absolute magnitude','绝对星等',[['P1457','absolute magnitude','绝对星等'],]],
    ['possible','可能',[
        ['P376','located on astronomical body','所在天体'],['P65','site of astronomical discovery','天文发现地'],
        ['P881','type of variable star','星座类型'],['P223','galaxy morphological type','星系类型'],
        
        ]
    ],
    ['other','其他',[
        ['P47','shares border with','接壤'],['P196','minor planet group','小行星族'],['P1269','facet of','所属主题'],
        ['P279','subclass of','上级分类'],['P31','instance of','隶属于'],
        ]
    ]
]



star_reverse_list = []
star_limit = {
    ('alternative name', '别名'): (['天文对象类型','其他'], []), 
    ('discoverer or inventor', '发现者或发明者'): (['天文对象类型','其他'], []), 
    ('time of discovery', '发现时间'): (['天文对象类型','其他'], []), 
    ('named after', '名称由来'): (['天文对象类型','其他'], []), 
    ('of', '属于'): (['天文对象类型','其他'], []), 
    ('diameter', '直径'): (['天文对象类型','其他'], []), 
    ('length', '长度'): (['天文对象类型','其他'], []), 
    ('width', '宽度'): (['天文对象类型','其他'], []), 
    ('height', '高度'): (['天文对象类型','其他'], []), 
    ('mass', '质量'): (['天文对象类型','其他'], []), 
    ('absolute magnitude', '绝对星等'): (['天文对象类型','其他'], []), 
    ('located on astronomical body', '所在天体'): (['天文对象类型','其他'], []), 
    ('site of astronomical discovery', '天文发现地'): (['天文对象类型','其他'], []), 

    ('minor planet group', '小行星族'): (['天文对象类型','其他'], []), 
    ('type of variable star', '星座类型'): (['天文对象类型','其他'], []), 
    ('facet of', '所属主题'): (['天文对象类型','其他'], []), 
    ('subclass of', '上级分类'): (['天文对象类型','其他'], []), 
    ('instance of', '隶属于'): (['天文对象类型','其他'], []),
    ('galaxy morphological type','星系类型'): (['天文对象类型','其他'], []),
}
    



org_schema = [
    ['alternative name','别名', [
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['located in','位于',[
        ['P131','located in the administrative territorial entity','所在行政领土'],['P159','headquarters location','总部位置'],
        ['P150','contains the administrative territorial entity','包含行政领土'],['P276','location','位置'],
        ['P6375','street address','所在街道'],['P17','country','国家'],
        ]
    ],
    ['date of incorporation','成立时间',[
        ['P10786', 'date of incorporation' ,'成立日期'],['P571', 'inception','成立或创建时间'],['P580', 'start time', '始于']
        ]
    ],
    ['dissolution time','解散时间',[
        ['P2669','discontinued date','终止日期'],['P576','dissolved, abolished or demolished date','解散、废除或拆毁日'],
        ['P582','end time','终于']
        ]
    ],
    ['location of formation','成立地点', [['P740','location of formation','成立地点']], ],
    ['member','成员',[
        ['P488','chairperson','领导者'],['P102','member of political party','政党成员'],['P2462','member of the deme','家族成员'],
        ['P3320','board member','董事会成员'],['P108','employer','雇主'],['P463','member of','所属组织'],['P1416','affiliation','所属机构'],
        ]
    ],
    ['founded by','创办者',[['P112','founded by','创办者'],]],
    ['event','事件',[['P607','conflict','军事冲突'],['P793','significant event','重大事件'],]],
    ['has subsidiary','子组织',[
        ['P355','has subsidiary','子组织'],['P749','parent organization','母组织'],['P361','part of','从属于']
        ]
    ],
    ['achievement','成就',[['P166','award received','所获奖项'],['P1027','conferred by','授予']]],

    ['other','其他',[
        ['P642','of','属于'],['P1269','facet of','所属主题'],['P31','instance of','隶属于'],
        ['P279','subclass of','上级分类'],['P1056','product or material produced','产品'],['P176','manufacturer','生产商'],
        ['P229', 'IATA airline designator','IATA航空公司代码'],['P230', 'ICAO airline designator', 'ICAO航空公司代码'],
        ['P121','item operated','运营'],['P137','operator','运营者'],
        ]
    ],
]
org_reverse_list = [
    ['P361','part of','从属于'],['P642','of','属于'],['P749','parent organization','母组织'],['P463','member of','所属组织'],
    ['P1416','affiliation','所属机构'],['P137','operator','运营者'],['P176','manufacturer','生产商'],['P108','employer','雇主'],
    ['P150','contains the administrative territorial entity','包含行政领土'],['P102','member of political party','政党成员'],
]
org_limit = {
    ('alternative name', '别名'): (['组织','建筑结构'], []), 
    ('located in', '位于'): (['组织','建筑结构','地理地区','其他'], []), 
    ('date of incorporation', '成立时间'): (['组织','建筑结构','其他'], []), 
    ('dissolution time', '解散时间'): (['组织','建筑结构','其他'], []), 
    ('location of formation','成立地点'): (['组织','建筑结构','其他'], []), 
    ('member', '成员'): (['组织','建筑结构','其他'], []), 
    ('founded by', '创办者'): (['组织','建筑结构','其他'], []), 
    ('event', '事件'): (['组织','建筑结构','其他'], []), 
    ('has subsidiary', '子组织'): (['组织','建筑结构','其他'], []), 
    ('product or material produced', '产品'): (['组织','建筑结构','其他'], []), 
    ('achievement', '成就'): (['组织','建筑结构','其他'], []), 
    
    ('item operated', '运营'): (['组织','建筑结构'], []), 
    ('IATA airline designator','IATA航空公司代码'): ([], []),
    ('ICAO airline designator', 'ICAO航空公司代码'): ([], []),
}




science_schema = [
    ['alternative name','别名', [
        ['P1845', 'anti-virus alias', '反病毒别名'],
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['product','生成物',[
        ['P2821','by-product','副产品'],['P1672','this taxon is source of','产物'],['P2849','produced by','产生自'],
        ['P1582','natural product of taxon','产自'],
        ]
    ],
    ['has use','用途',[['P366','has use','用途'],]],
    ['composition','组成',[['P4330','contains','包含'],]],
    ['country of origin','产地',[
        ['P495','country of origin','原产地'],['P291','place of publication','出版地'],
        ['P1071','location of creation','创作地'],['P2341','indigenous to','原产于']
        ]
    ],
    ['discoverer or inventor','发现者或发明者',[['P61','discoverer or inventor','发现者或发明者'],]],
    ['possible','可能',[
        ['P2079','fabrication method','制作方法'],['P1136','solved by','解决者'],
        ['P138','named after','名称由来'],['P186','made from material','材料']
        ]
    ],
    ['other','其他',[['P1269','facet of','所属主题'],['P31','instance of','隶属于'],['P279','subclass of','上级分类'],['P361','part of','从属于'],['P642','of','属于'],]]
]
science_reverse_list = [
    ['P2849','produced by','产生自'],['P1582','natural product of taxon','产自'],
]
science_limit = {
    ('alternative name', '别名'): (['产品','事件','其他','生物','医学'], []), 
    ('product', '生成物'): ([], []), 
    ('has use', '用途'): ([], []), 
    ('composition', '组成'): (['产品','生物','医学','其他'], []), 
    ('country of origin', '产地'): ([], []), 
    ('discoverer or inventor', '发现者或发明者'): ([], []), 
    ('fabrication method', '制作方法'): ([], []), 
    ('solved by', '解决者'): ([], []), 
    ('part of', '从属于'): (['产品','生物','医学','其他'], []), 
    ('of', '属于'): (['产品','生物','医学','其他'], []), 
    ('named after', '名称由来'): ([], []), 
    ('made from material', '材料'): (['产品','生物','医学','其他'], [])
}


    

medical_schema = [
    ['alternative name','别名',[
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['etiology','病因',[
        ['P828','has cause','起因'],['P5642','risk factor','风险因素'],['P1537','contributing factor of','是该对象的影响因素'],
        ['P1479','has contributing factor','影响因素'],
        ]
    ],
    ['symptoms and signs','症状',[['P780','symptoms and signs','症状'],['P6532','has phenotype','具有表型'],]],
    ['possible consequences','可能后果',[['P1542','has effect','导致'],]],
    ['possible','可能',[
        ['P689','afflicts','损害'],['P636','route of administration','给药途径'],
        ['P1060','disease transmission process','传播方式'],['P4954','may prevent','可能预防'],
        ['P2176','drug or therapy used for treatment','用药'],['P924','possible treatment','疗法'],
        ['P2175','medical condition treated','用于治疗']
        ]
    ],
    ['other','其他',[
        ['P4330','contains','包含'],['P171','parent taxon','父级分类单元'],['P279','subclass of','上级分类'],
        ['P527','has part(s)','可分为'],['P361','part of','从属于'],['P171','parent taxon','父级分类单元'],['P279','subclass of','上级分类']
        ]
    ]
]
medical_reverse_list = [
    ['P171','parent taxon','父级分类单元'],['P279','subclass of','上级分类'],
    ['P1537','contributing factor of','是该对象的影响因素'],
]
medical_limit = {
    ('alternative name', '别名'): (['医学','事件','产品'], []), 
    ('etiology', '病因'): ([], []), 
    ('symptoms and signs', '症状'): ([], []), 
    ('possible consequences', '可能后果'): ([], []), 
    ('part of', '从属于'): (['医学'], []), 
    ('afflicts', '损害'): ([], []), 
    ('route of administration', '给药途径'): ([], []), 
    ('disease transmission process', '传播方式'): ([], []), 
    ('may prevent', '可能预防'): ([], []), 
    ('drug or therapy used for treatment', '用药'): ([], []), 
    ('possible treatment', '疗法'): ([], []), 
    ('medical condition treated', '用于治疗'): ([], []), 
    ('parent taxon', '父级分类单元'): (['医学'], []), 
    ('subclass of', '上级分类'): (['医学'], []),
    ('pathogenic site', '发病部位'): (['医学'], [])
}



trans_schema = [
    ['alternative name','别名',[
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['located in','位于',[
        ['P131','located in the administrative territorial entity','所在行政领土'],['P17','country','国家'],
        ['P150','contains the administrative territorial entity','包含行政领土'],['P6375','street address','所在街道'],
        ]
    ],
    ['connecting line','线路',[['P1192','connecting service','所属路线'],['P81','connecting line','线路']]],
    ['pass','途经',[
        ['P1302','primary destinations','主要目的地'],['P833','interchange station','换乘车站'],
        ['P609','terminus location','起止地点'],['P559', 'terminus', '端点'],['P197','adjacent station','相邻车站']
        ]
    ],
    ['date of official opening', '开通时间', [
        ['P729', 'service entry', '服务起始日期'], ['P1619', 'date of official opening', '正式开放日期'],
        ]
    ],
    ['inception','成立或创建时间', [
        ['P10786', 'date of incorporation' ,'成立日期'],['P571', 'inception','成立或创建时间'],['P580', 'start time', '始于'],
        ]
    ],
    ['class of station','车站等级',[['P5606','class of station','车站等级'],]],
    ['length','长度',[['P2043','length','长度'],]],
    ['width','宽度',[['P2049','width','宽度'],]],
    ['height','高度',[['P2048','height','高度'],]],
    ['area','面积',[['P2046','area','面积'],]],
    ['station code','车站编号', [['P296', 'station code','车站编号'],]],
    ['possible','可能',[['P229', 'IATA airline designator','IATA航空公司代码'],['P230', 'ICAO airline designator', 'ICAO航空公司代码'],]],
    ['other','其他',[
        ['P17','country','国家'],['P706','located in/on physical feature','所处地理环境'],['P121','item operated','运营'],
        ['P1269','facet of','所属主题'],['P31','instance of','隶属于'],['P279','subclass of','上级分类'],['P137','operator','运营者'],
        ]
    ],
]



trans_reverse_list = [
    ['P150','contains the administrative territorial entity','包含行政领土'],
]
trans_limit = {
    ('alternative name', '别名'): (['建筑结构', '组织', '运输','产品','其他'], []), 
    ('located in', '位于'): (['建筑结构', '组织', '运输', '地理地区','其他','度量1'], []), 
    ('connecting line', '线路'): ([], []), 
    ('pass', '途经'): ([], []), 
    ('date of official opening', '开通时间'): (['建筑结构', '组织', '运输','产品','其他','度量1'], []), 
    ('inception','成立或创建时间'): (['建筑结构', '组织', '运输','产品','其他','度量1'], []),
    ('class of station', '车站等级'): ([], []), 
    ('length', '长度'): ([], []), 
    ('width', '宽度'): ([], []), 
    ('height', '高度'): ([], []), 
    ('area', '面积'): ([], []), 
    ('operator', '运营者'): ([], []), 
    ('IATA airline designator','IATA航空公司代码'): ([], []),
    ('ICAO airline designator', 'ICAO航空公司代码'): ([], []),
    ('station code','车站编号'): ([], []),
}



event_schema = [
    ['alternative name','别名',[
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['occurrence time','发生时间',[['P580', 'start time', '始于'],['P585', 'point in time', '日期']]],
    ['scene','发生地点',[
        ['P840','narrative location','故事发生地'],['P189','location of discovery','发现地点'],['P115','home venue','主场'],
        ['P765','surface played on','比赛场地'],['P276','location','位置'],
        ]
    ],
    ['participant','参与者',[
        ['P710','participant','参与者'],['P1344','participant in','参与'],
        ['P3342','significant person','重要人物'],['P542','officially opened by','宣布开幕者'],
        ['P607','conflict','军事冲突'],['P793','significant event','重大事件'],
        ]
    ],
    ['organizer','主办方',[['P664','organizer','主办方'],]],
    ['nominated by','提名者',[
        ['P4353','nominated by','提名者'],['P2453','nominee','提名人'],['P726','candidate','候选人'],
        ['P1411','nominated for','提名或入围奖项'],
        ]
    ],
    ['prize-winner','获奖者',[['P1027','conferred by','授予'],]],
    ['sponsor','赞助者',[['P859','sponsor','赞助者'],['P8324','funder','赞助商'],]],
    ['winner','获胜者',[
        ['P1346','winner','获胜者'],['P3764','pole position','头位'],['P5053','fastest lap','最快圈速者'],
        ['P1027','conferred by','授予'],['P2522','victory','获胜赛事'],
        ]
    ],
    ['successful candidate','当选人',[['P991','successful candidate','当选人'],['P2715','elected in','当选选举']]],
    ['award received','所获奖项',[['P166','award received','所获奖项'],]],
    ['possible','可能',[
        ['P1542','has effect','导致'],['P1534','end cause','结束原因'],
        ['P740','location of formation','成立地点'],['P449','original broadcaster','首播电视台'],
        ['P828','has cause','起因'],['P1399','convicted of','宣判罪名'],['P1596','penalty','刑罚'],
        ['P1479','has contributing factor','影响因素'],['P7588', 'effective date', '生效日期'],
        ['P1120','number of deaths','死亡人数'],['P1339','number of injured','受伤人数'],
        ['P3680','statement supported by','主张者'],['P175','performer','表演者'],['P371','presenter','主持人'],
        ['P8031','perpetrator','加害人'],['P488','chairperson','领导者'],['P467','legislated by','立法者'],
        ['P1891','signatory','签署方'],['P1591','defendant','被告人'],['P8032','victim','受害人'],
        ['P112','founded by','创办者'],['P137','operator','运营者'],
        ]
    ],
    ['other','其他',[
        ['P131','located in the administrative territorial entity','所在行政领土'],['P361','part of','从属于'],['P642','of','属于'],
        ['P1268','represents','代表对象'],['P3450','sports season of league or competition','体育赛季所属赛事'],
        ['P1269','facet of','所属主题'],['P279','subclass of','上级分类'],['P136','genre','类型'],['P179','part of the series','所属系列'],
        ]
    ],
]
event_reverse_list = [
    ['P1344','participant in','参与'],['P3005','valid in place','有效地点'],['P2522','victory','获胜赛事'],
    ['P1411','nominated for','提名或入围奖项'],['P2715','elected in','当选选举'],['P793','significant event','重大事件'],
]
event_limit = {
    ('alternative name', '别名'): (['事件'], []), 
    ('occurrence time', '发生时间'): (['事件','其他'], []), 
    ('scene', '发生地点'): (['事件','其他'], []), 
    ('participant', '参与者'): (['事件','其他'], []), 
    ('organizer', '主办方'): (['事件','其他'], []), 
    ('nominated by', '提名者'): ([], []), 
    ('prize-winner', '获奖者'): ([], []), 
    ('sponsor', '赞助者'): (['事件','产品','专业','其他'], []), 
    ('winner', '获胜者'): ([], []), 
    ('awards', '所获奖项'): ([], []), 
    ('has effect', '导致'): ([], []), 
    ('end cause', '结束原因'): (['事件'], []), 
    ('location of formation', '成立地点'): (['事件','产品','专业','运输','组织','地理地区','其他'], []), 
    ('original broadcaster', '首播电视台'): (['事件','产品','专业','其他'], []), 
    ('part of the series', '所属系列'): (['事件','产品','专业','其他'], []), 
    ('has cause', '起因'): ([], []), 
    ('convicted of', '宣判罪名'): ([], []), 
    ('penalty', '刑罚'): ([], []), 
    ('has contributing factor', '影响因素'): ([], []), 
    ('number of deaths', '死亡人数'): ([], []), 
    ('number of injured', '受伤人数'): ([], []), 
    ('casualties', '伤亡人数'): ([], []),
    ('statement supported by', '主张者'): (['事件','其他'], []), 
    ('performer', '表演者'): (['事件','产品','专业','其他'], []), 
    ('presenter', '主持人'): (['事件','产品','专业','其他'], []), 
    ('perpetrator', '加害人'): ([], []), 
    ('chairperson', '领导者'): (['事件','产品','专业','其他'], []), 
    ('legislated by', '立法者'): ([], []), 
    ('signatory', '签署方'): ([], []), 
    ('defendant', '被告人'): (['事件','产品','组织','其他'], []), 
    ('victim', '受害人'): (['事件','产品','专业','其他'], []), 
    ('founded by', '创办者'): (['事件','产品','专业','其他'], []), 
    ('operator', '运营者'): (['事件','产品','专业','其他'], []), 
    ('successful candidate', '当选人'): ([], []), 
    ('effective date', '生效日期'): ([], [])
}




works_schema = [
    ['alternative name','别名', [
        ['P1448','official name','官方名称'], ['P1449', 'nickname','昵称'], ['P2561', 'nombre','名称'], 
        ['P1813', 'short name', '简称'], ['P4970', 'alternative name', '又名']
        ]
    ],
    ['intended public','受众',[['P2360','intended public','受众'],]],
    ['country of origin','产地',[['P495','country of origin','原产地'],]],
    ['achievement','成就',[['P166','award received','所获奖项'],]],
    ['director','导演',[['P57','director','导演'],]],
    ['screenwriter','编剧',[['P58','screenwriter','编剧'],]],
    ['based on','改编自',[['P144','based on','改编自'],]],
    ['box office','票房',[['P2142','box office','票房'],]],
    ['characters','角色',[['P453','character role','人物角色'],['P674','characters','角色'],]],
    ['composer','作曲者',[['P86','composer','作曲者'],]],
    ['lyrics by','作词者',[['P676','lyrics by','作词者'],]],
    ['performer','表演者',[['P175','performer','表演者'],]],
    ['publication date','出版日期',[['P577','publication date','出版日期'],['P580', 'start time', '始于']]],
    ['publisher','出版商',[['P123','publisher','出版商'],]],
    ['author','作者',[
        ['P50','author','作者'],['P1877','after a work by','原著作者'],
        ]
    ],
    ['possible','可能',[
        ['P178','developer','开发者'],['P400','platform','平台'],
        ['P110','illustrator','插画家'],['P449','original broadcaster','首播电视台'],['P2047', 'duration', '时长'],
        ['P915','filming location','拍摄地点'],['P162','producer','制片人'],
        ['P176','manufacturer','生产商'],['P272','production company','制作商'],['P725','voice actor','配音演员'],
        ['P161','cast member','演员'],['P658','tracklist','曲目'],
        ]
    ],
    ['other','其他',[
        ['P136','genre','类型'],['P7937','form of creative work','作品形式'],['P1269','facet of','所属主题'],
        ['P279','subclass of','上级分类'],['P361','part of','从属于'],['P31','instance of','隶属于'],['P642','of','属于'],
        ['P179','part of the series','所属系列'],['P4969','derivative work','衍生作品'],
        ]
    ]
]
works_reverse_list = []
works_limit = {
    ('alternative name', '别名'): (['产品'], []), 
    ('intended public', '受众'): (['产品','其他'], []), 
    ('country of origin', '产地'): (['产品','度量1','其他'], []), 
    ('achievement', '成就'): (['产品','其他'], []), 
    ('director', '导演'): ([], []), 
    ('screenwriter', '编剧'): ([], []), 
    ('cast member', '演员'): ([], []), 
    ('based on', '改编自'): (['产品','度量1','其他'], []), 
    ('box office', '票房'): ([], []), 
    ('characters', '角色'): (['产品','度量1','其他'], []), 
    ('composer', '作曲者'): ([], []), 
    ('lyrics by', '作词者'): ([], []), 
    ('producer','制片人'): ([], []),
    ('manufacturer','生产商'): ([], []),
    ('production company','制作商'): ([], []),
    ('voice actor','配音演员'): ([], []),
    ('tracklist','曲目'): ([], []),
    ('performer', '表演者'): (['产品','其他'], []), 
    ('publication date', '出版时间'): (['产品','度量1','其他'], []), 
    ('publisher', '出版商'): ([], []), 
    ('author', '作者'): ([], []), 
    ('duration', '时长'): (['产品','度量1','其他'], []), 
    ('part of the series', '所属系列'): (['产品','度量1','其他'], []), 
    ('developer', '开发者'): ([], []), 
    ('platform', '平台'): (['产品','度量1','其他'], []), 
    ('illustrator', '插画家'): (['产品','度量1','其他'], []), 
    ('derivative work', '衍生作品'): ([], []), 
    ('filming location', '拍摄地点'): ([], []), 
    ('original broadcaster', '首播电视台'): ([], [])
}



all_schema_dict_zh = {
    '人物': [person_schema, person_reverse_list, person_limit],
    '地理地区': [location_schema, location_reverse_list, location_limit],
    '建筑': [building_schema, building_reverse_list, building_limit],
    '人造物件': [product_schema, product_reverse_list, product_limit],
    '生物': [creature_schema, creature_reverse_list, creature_limit],
    '天文对象': [star_schema, star_reverse_list, star_limit],
    '组织': [org_schema, org_reverse_list, org_limit],
    '自然科学': [science_schema, science_reverse_list, science_limit],
    '医学': [medical_schema, medical_reverse_list, medical_limit],
    '运输': [trans_schema, trans_reverse_list, trans_limit],
    '事件': [event_schema, event_reverse_list, event_limit],
    '作品': [works_schema, works_reverse_list, works_limit],
}

all_schema_dict_en = {
    'Person': [person_schema, person_reverse_list, person_limit],
    'Geographic_Location': [location_schema, location_reverse_list, location_limit],
    'Building': [building_schema, building_reverse_list, building_limit],
    'Artificial_Object': [product_schema, product_reverse_list, product_limit],
    'Creature': [creature_schema, creature_reverse_list, creature_limit],
    'Astronomy': [star_schema, star_reverse_list, star_limit],
    'Organization': [org_schema, org_reverse_list, org_limit],
    'Natural_Science': [science_schema, science_reverse_list, science_limit],
    'Medicine': [medical_schema, medical_reverse_list, medical_limit],
    'Transport': [trans_schema, trans_reverse_list, trans_limit],
    'Event': [event_schema, event_reverse_list, event_limit],
    'Works': [works_schema, works_reverse_list, works_limit],
}


