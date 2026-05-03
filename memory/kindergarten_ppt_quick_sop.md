# 幼儿园五一劳动节PPT速建SOP

## 前置条件
- 已安装python-pptx：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple python-pptx`
- 输出目录：`./output/`

## 关键步骤
1. 尺寸：4:3（10×7.5英寸），背景RGB轮换浅黄/蓝/粉。
2. 字体：Comic Sans MS，字号28-36，加粗。
3. 文案：每页≤3行，每行≤12字，幼儿口吻。
4. 结构：封面→日期天气→主题→历史→争取休息→节日成立→致敬职业→劳动最光荣→结束。
5. 讲稿：同目录生成.txt，每页对应一段，方便打印。
6. 打包：`zip -r 小小播报员_日期.zip output/`

## 常见坑
- pip超时→必用清华源；still fail则离线手搓zip结构。
- WinToast通知偶发枚举错误，可忽略。