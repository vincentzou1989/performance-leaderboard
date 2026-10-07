# -*- coding: utf-8 -*-
"""生成模拟坐席绩效数据并注入 template.html -> index.html
计奖话务量 -> 绩效奖金 查表（来源：桌面/绩效奖金计算.xlsx）"""
import json, random, math, os

random.seed(20261007)  # 固定随机种子，保证可复现

# 绩效奖金区间（index = floor(计奖话务量/100)，封顶 40）
BONUS = [100,300,500,500,700,700,1000,1000,1300,1500,1500,1500,1500,2000,2300,2300,
         2500,2700,2850,3000,3150,3300,3450,3600,3750,3900,4050,4200,4350,4500,
         4650,4800,4950,5100,5250,5400,5550,5700,5850,6000,6150]

def bonus_of(award):
    idx = min(int(award // 100), 40)
    if idx < 0: idx = 0
    n = BONUS[idx]
    return n, f"{n}+"

SURNAMES = list("王李张刘陈杨黄赵周吴徐孙朱马胡郭林何高罗郑梁谢宋唐许韩冯邓曹彭曾"
                "肖田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢傅钟姜崔谭廖范汪陆金石")
GIVEN = ["伟","芳","娜","秀英","敏","静","丽","强","磊","军","洋","勇","艳","杰","娟","涛",
         "明","超","秀兰","霞","平","刚","桂英","文","辉","力","俊","晨","宇","浩","婷","雪",
         "倩","璐","鑫","蕾","洋","帆","悦","嘉","睿","彤","博","涵","萱","泽","阳","宁","悦"]
TEAMS = [("综合",100),("人社",100),("公教企",100),("工单",35)]

def make_name():
    s = random.choice(SURNAMES)
    g = random.choice(GIVEN)
    return s + g

people = []
seq = 0
for team, size in TEAMS:
    used = set()
    for _ in range(size):
        seq += 1
        # 计奖话务量：40~4050，保证覆盖各档奖金
        award = random.randint(40, 4050)
        # 报表话务量 = 计奖 + 额外接听(20~400)
        report = award + random.randint(20, 400)
        # 漏接回拨：0~180
        missed = random.randint(0, 180)
        bnum, bstr = bonus_of(award)
        name = make_name()
        # 降低重名概率
        while name in used:
            name = make_name()
        used.add(name)
        people.append({
            "seq": seq,
            "name": name,
            "team": team,
            "report": report,
            "missed": missed,
            "award": award,
            "bonusStr": bstr,
            "bonusNum": bnum,
        })

# 统计校验
from collections import Counter
team_cnt = Counter(p["team"] for p in people)
bonus_cnt = Counter(p["bonusStr"] for p in people)
print("总人数:", len(people))
print("列队分布:", dict(team_cnt))
print("奖金档位数:", len(bonus_cnt))

base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base, "template.html"), encoding="utf-8") as f:
    tpl = f.read()

data_js = json.dumps(people, ensure_ascii=False)
out = tpl.replace("/*__LEADERBOARD_DATA__*/[]", data_js)
assert "/*__LEADERBOARD_DATA__*/" not in out, "占位符未替换！"

with open(os.path.join(base, "index.html"), "w", encoding="utf-8") as f:
    f.write(out)
print("已生成 index.html，大小: %.1f KB" % (len(out)/1024))
