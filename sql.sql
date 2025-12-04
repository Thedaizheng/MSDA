USE storm_wiki_test;
-- 创建表格
CREATE TABLE research_data (
    cate VARCHAR(255),  /* 类别 */
    auid VARCHAR(255),  /* 用户ID */
    patent INT,         /* 专利数量 */
    cg INT,             /* CG数量 */
    org VARCHAR(255),   /* 组织名称 */
    count INT,          /* 数量 */
    freq VARCHAR(255),  /* 频率 */
    h VARCHAR(255),     /* H值 */
    title VARCHAR(255), /* 标题 */
    quoteCount VARCHAR(255), /* 引用次数 */
    name VARCHAR(255),  /* 名称 */
    base INT,           /* 基础值 */
    ckey VARCHAR(255)   /* 搜索关键词 */
);


CREATE TABLE ExpertRelated (
    `key` VARCHAR(100),
    value INTEGER,
    city VARCHAR(50)
);


CREATE TABLE enterprise_data (
    name VARCHAR(255),   -- 名称
    value INT,           -- 数值
    ckey VARCHAR(255),   -- 新增列，字段为 ckey，数据类型为 VARCHAR(255)
    year INT             -- 新增列，字段为 year，数据类型为 INT
);




CREATE TABLE authors_data (
    org VARCHAR(255),   -- 组织名称
    name VARCHAR(255),  -- 作者名称
    value INT,          -- 数值
    ckey VARCHAR(255)   -- 查询关键词
);

CREATE TABLE authors_statistics (
    org VARCHAR(255),     -- 组织名称
    author VARCHAR(255),  -- 作者名称
    value INT,            -- 数值
    ckey VARCHAR(255),    -- 查询关键词
    idx INT               -- 索引值（避免与保留字冲突）
);



CREATE TABLE enterprise_recommendation (
    org VARCHAR(255), -- 组织名称
    name VARCHAR(255),  -- 作者名称
    value INT,         -- 数值
    ckey VARCHAR(255) -- 新增列，字段为ckey，数据类型为VARCHAR(255)
);

CREATE TABLE org_recommend (
    ORGID VARCHAR(50),
    TRADE VARCHAR(255),        -- 逗号分隔的字符串s
    INDUSTRY VARCHAR(255),     -- 逗号分隔的字符串
    CITY VARCHAR(255),
    AREACODE VARCHAR(50),
    SOURCE VARCHAR(50),
    PROV VARCHAR(50),
    FLMC VARCHAR(255),         -- 逗号分隔的字符串
    TAGS VARCHAR(255),         -- 逗号分隔的字符串
    MARK NUMERIC,
    NAME VARCHAR(255),
    SCORE NUMERIC
);





CREATE TABLE tech_achievements (
    id SERIAL PRIMARY KEY, -- 自增的主键，用于唯一标识每条记录
    scientific_achievements INT, -- 科技成果的数量
    funded_projects INT, -- 基金项目的数量
    patents INT, -- 专利的数量
    scientific_papers INT, -- 科技论文的数量
    technical_core INT -- 技术骨干的数量
);


CREATE TABLE company_info (
    id VARCHAR(20) PRIMARY KEY, -- 唯一标识
    type VARCHAR(50), -- 类型
    corpname VARCHAR(255), -- 公司名称
    contact VARCHAR(50), -- 联系方式
    ckey TEXT, -- 关键词
    companytype VARCHAR(100), -- 公司类型
    industry VARCHAR(100), -- 行业
    fund VARCHAR(50), -- 资金（可为空）
    intro TEXT, -- 公司简介
    creditcode VARCHAR(50), -- 信用代码（可为空）
    legalperson VARCHAR(100), -- 法人
    oper TEXT, -- 经营范围
    prov VARCHAR(50), -- 省份
    email VARCHAR(100), -- 邮箱（可为空）
    url VARCHAR(255), -- 网址（可为空）
    addr VARCHAR(255), -- 地址
    date DATE, -- 成立日期
    status VARCHAR(50), -- 状态
    tags TEXT -- 标签（可为空）
);


CREATE TABLE project_data (
    id INT AUTO_INCREMENT PRIMARY KEY, /* 自增主键 */
    `key` VARCHAR(100), /* 类型名称 */
    count INT /* 数量 */
);


CREATE TABLE publications (
    id SERIAL PRIMARY KEY, -- 自增主键
    wid VARCHAR(50), -- 文献标识
    year VARCHAR(10), -- 发表年份
    au VARCHAR(255), -- 作者
    ti VARCHAR(255), -- 文章标题
    pg VARCHAR(50), -- 页码
    orgc VARCHAR(255), -- 作者单位
    title VARCHAR(255), -- 文章标题（完整版）
    joucn VARCHAR(100), -- 期刊名称
    per VARCHAR(10), -- 期刊期号
    pn VARCHAR(10), -- 期刊页码
    type VARCHAR(50), -- 文献类型
    vol VARCHAR(10) -- 卷号
);

CREATE TABLE research_articles (
    id SERIAL PRIMARY KEY, -- 自增主键
    pte VARCHAR(255), -- 可能为空的字段
    dop DATE NOT NULL, -- 发布日期
    au TEXT NOT NULL, -- 作者信息
    fitclass VARCHAR(255) NOT NULL, -- 分类信息
    aw VARCHAR(255), -- 可能为空的字段
    orgc TEXT NOT NULL, -- 组织信息
    title TEXT NOT NULL, -- 标题信息
    fitlevel VARCHAR(255), -- 可能为空的字段
    unique_id VARCHAR(255) UNIQUE NOT NULL, -- 唯一标识符
    ckey VARCHAR(255) NOT NULL -- 新增字段，存储固定值 '临沂'
);

CREATE TABLE  Patent_Output_List (
    id SERIAL PRIMARY KEY, -- 自增主键
    patno VARCHAR(50) NOT NULL, -- 专利号
    reqpep TEXT NOT NULL, -- 申请人
    patt VARCHAR(50) NOT NULL, -- 专利类型
    au TEXT NOT NULL, -- 发明人
    annodate DATE NOT NULL, -- 公告日期
    title TEXT NOT NULL, -- 专利名称
    reqno VARCHAR(50) NOT NULL, -- 申请号
    unique_id VARCHAR(50) UNIQUE NOT NULL, -- 唯一标识符
    ckey VARCHAR(50) NOT NULL DEFAULT '临沂' -- 新增字段，值默认为 '临沂'
);
