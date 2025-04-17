import streamlit as st
import pymysql
import pyqrcode
from io import BytesIO
import base64
from config import DB_CONFIG
import urllib.parse
import time

# 页面配置
st.set_page_config(
    page_title="心理调查问卷",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def local_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("assets/style.css")


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


def save_to_database(data):
    try:
        # 确保所有问题字段都存在
        for q in range(6, 97):
            if f"q{q}" not in data:
                data[f"q{q}"] = 1  # 设置默认值

        connection = get_db_connection()
        with connection.cursor() as cursor:
            columns = ', '.join([f'`{k}`' for k in data.keys()])
            placeholders = ', '.join(['%s'] * len(data))
            sql = f"INSERT INTO survey ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(data.values()))
            st.write(f"DEBUG - 执行的SQL: {sql}")  # 调试输出
            st.write(f"DEBUG - 插入的值: {tuple(data.values())}")
        connection.commit()
        return True
    except Exception as e:
        st.error(f"数据库错误: {str(e)}")
        return False
    finally:
        if 'connection' in locals() and connection:
            connection.close()


def generate_qrcode(url):
    qr = pyqrcode.create(url)
    buffer = BytesIO()
    qr.png(buffer, scale=6)
    return base64.b64encode(buffer.getvalue()).decode()


def get_current_url():
    try:
        ctx = st.runtime.scriptrunner.get_script_run_ctx()
        if ctx:
            return f"http://{ctx.host}:{ctx.port}{ctx.script_route}"
    except:
        pass
    return "http://localhost:8501"  # 本地开发默认


def show_questionnaire():
    st.title("🧠 心理调查问卷")
    st.markdown("感谢您参与本次心理调查！您的回答将帮助我们更好地了解您的心理状态和需求，本问卷所有数据将严格保密。")

    with st.form("survey_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名", key="name", max_chars=50)
            age = st.number_input("年龄", min_value=0, max_value=120, key="age")
        with col2:
            gender = st.selectbox("性别", ["男", "女", "其他"], key="gender")
            student_id = st.text_input("学号", key="student_id").strip()  # 去除空格

        class_ = st.text_input("班级", key="class_")

        questions = [
            "头痛",
            "神经过敏，心中不踏实",
            "头脑中有不必要的想法或字句盘旋",
            "头昏或昏倒",
            "对异性的兴趣减退",
            "对旁人责备求全",
            "感到别人能控制您的思想",
            "责怪别人制造麻烦",
            "忘记性大",
            "担心自己的衣饰整齐以及仪态的端正",
            "容易烦恼和激动",
            "胸痛",
            "害怕空旷的场所或街道",
            "感到自己的精力下降，活动减慢",
            "想结束自己的生命",
            "听到旁人听不到的声音",
            "发抖",
            "感到大多数人都不可信任",
            "胃口不好",
            "容易哭泣",
            "同异性相处时感到害羞不自在",
            "感到受骗、中了圈套或有人想抓住您",
            "无缘无故地突然感到害怕",
            "自己不能控制地大发脾气",
            "怕单独出门",
            "经常责怪自己",
            "腰痛",
            "感到难以完成任务",
            "感到孤独",
            "感到苦闷",
            "过分担忧",
            "对事物不感兴趣",
            "感到害怕",
            "您的感情容易受到伤害",
            "旁人能知道您的私下想法",
            "我这次调查是按照我真实情况和感受填写,此题请选择第3项",
            "感到别人不理解您不同情您",
            "感到人们对您不友好，不喜欢您",
            "做事必须做得很慢以保证做得正确",
            "心跳得很厉害",
            "恶心或胃部不舒服",
            "感到比不上他人",
            "肌肉酸痛",
            "感到有人在监视您谈论您",
            "难以入睡",
            "做事必须反复检查",
            "难以作出决定",
            "怕乘电车、公共汽车、地铁或火车",
            "呼吸有困难",
            "一阵阵发冷或发热",
            "因为感到害怕而避开某些东西、场合或活动",
            "脑子变空了",
            "身体发麻或刺痛",
            "喉咙有梗塞感",
            "感到前途没有希望",
            "不能集中注意",
            "感到身体的某一部分软弱无力",
            "感到紧张或容易紧张",
            "感到手或脚发重",
            "想到死亡的事情",
            "吃得太多",
            "当别人看着您或谈论您时感到不自在",
            "有一些不属于您自己的想法",
            "有想打人或伤害他人的冲动",
            "醒得太早",
            "必须反复洗手，点数目或触摸某些东西",
            "睡得不稳不醒",
            "有想摔坏或破坏东西的冲动",
            "有一些别人没有的想法或念头",
            "感到对别人神经过敏",
            "在商店或电影院等人多的地方感到不自在",
            "感到任何事情都很困难",
            "一阵阵恐惧或惊慌",
            "感到在公共场合吃东西很不舒服",
            "经常与人争论",
            "单独一人时神经很紧张",
            "别人对您的成绩没有做出恰当的评价",
            "即使和别人在一起也感到孤独",
            "感到坐立不安心神不定",
            "感到自己没有什么价值",
            "感到熟悉的东西变得陌生或不像是真的",
            "大叫或摔东西",
            "害怕会在公共场合昏倒",
            "感到别人想占您的便宜",
            "为一些有关“性”的想法而很苦恼",
            "您认为应该因为自己的过错而受到惩罚",
            "感到要赶快把事情做完",
            "感到自己的身体有严重毛病",
            "从未感到和其他人很亲近",
            "感到自己有罪",
            "感到自己的脑子有毛病"
        ]

        answers = {}
        for i, question in enumerate(questions, 6):
            st.subheader(f"问题{i}: {question}")
            if i == 41:
                ans = st.radio(f"Q{i}", options=["从不", "很少", "有时", "经常", "总是"], index=2, horizontal=True,
                               key=f"q{i}")
            else:
                ans = st.radio(f"Q{i}", options=["从不", "很少", "有时", "经常", "总是"], horizontal=True, key=f"q{i}")
            answers[f"q{i}"] = ["从不", "很少", "有时", "经常", "总是"].index(ans) + 1

        if st.form_submit_button("提交问卷"):
            if not student_id:
                st.error("学号不能为空！")
                return

            form_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "student_id": student_id,
                "class_": class_,
                **answers
            }

            if save_to_database(form_data):
                # 生成带时间戳的反馈链接避免缓存问题
                timestamp = int(time.time())
                base_url = get_current_url()
                feedback_url = f"{base_url}?feedback_id={student_id}&t={timestamp}"

                st.success("问卷提交成功！")
                st.balloons()

                # 显示调试信息
                st.write("### 调试信息")
                st.write(f"生成的反馈链接: `{feedback_url}`")

                # 生成二维码
                qr_img = generate_qrcode(feedback_url)
                st.subheader("扫描二维码查看个性化反馈")
                st.markdown(f'<img src="data:image/png;base64,{qr_img}" width="200">', unsafe_allow_html=True)
                st.markdown(f"[点击查看反馈]({feedback_url})")


# ... (前面的import和配置保持不变)

def save_to_database(data):
    try:
        # 确保所有问题字段都存在
        for q in range(6, 97):
            if f"q{q}" not in data:
                data[f"q{q}"] = 1  # 设置默认值

        connection = get_db_connection()
        with connection.cursor() as cursor:
            columns = ', '.join([f'`{k}`' for k in data.keys()])
            placeholders = ', '.join(['%s'] * len(data))
            sql = f"INSERT INTO survey ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(data.values()))
        connection.commit()
        return True
    except Exception as e:
        st.error(f"数据库错误: {str(e)}")
        return False
    finally:
        if 'connection' in locals() and connection:
            connection.close()


def show_feedback(feedback_id):
    st.title("📊 您的个性化心理建议")
    st.write(f"正在查询学号: `{feedback_id}`")

    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 修改为使用字符串查询，确保类型匹配
            sql = "SELECT * FROM survey WHERE student_id = %s"
            cursor.execute(sql, (str(feedback_id),))  # 确保转换为字符串

            result = cursor.fetchone()

            if result:

                # 显示基本信息
                with st.container():
                    st.subheader("基本信息")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("姓名", result.get('name', '未知'))
                    with cols[1]:
                        st.metric("年龄", result.get('age', '未知'))
                    with cols[2]:
                        st.metric("性别", result.get('gender', '未知'))

                # 计算分数
                st.subheader("评估结果")
                scores = [v for k, v in result.items() if k.startswith('q') and k != 'q41']
                total_score = sum(scores)
                avg_score = total_score / len(scores) if scores else 0

                # 创建评分卡
                score_card = st.container()
                with score_card:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("总分", f"{total_score}/380")
                        st.metric("平均分", f"{avg_score:.2f}/4")

                    with col2:
                        # 可视化进度条
                        st.progress(min(avg_score / 4, 1.0))
                        if avg_score < 2:
                            st.success("您的心理健康状况良好")
                        elif avg_score < 3.5:
                            st.warning("您存在轻度心理困扰")
                        else:
                            st.error("您可能存在显著心理困扰")

                # 详细建议
                st.subheader("专业建议")
                if avg_score < 2:
                    st.markdown("""
                    - 😊 您的心理状态非常健康
                    - 继续保持良好的生活习惯
                    - 定期进行自我心理评估
                    """)
                elif avg_score < 3.5:
                    st.markdown("""
                    - 🧘 建议尝试以下缓解方法:
                      - 每天10分钟正念冥想
                      - 每周3次30分钟有氧运动
                      - 保持规律作息
                      - 与朋友家人多交流
                    - 可预约学校心理咨询室进行专业评估
                    """)
                else:
                    st.markdown("""
                    - ❤️ 我们建议您:
                      - 立即联系学校心理咨询中心
                      - 拨打心理援助热线: 12320
                      - 避免独自承受压力
                      - 保持规律生活作息
                    - 专业帮助能有效改善您的状况
                    """)

                # 显示提交时间（如果表中有时间字段）
                if 'create_time' in result:
                    st.caption(f"问卷提交时间: {result['create_time']}")

            else:
                st.warning("未找到您的问卷记录")
                st.markdown("""
                **可能原因及解决方案:**
                1. 学号输入错误 → 请检查学号是否正确
                2. 问卷未成功提交 → 请重新填写提交
                3. 数据库延迟 → 请稍后刷新页面
                """)

                # 提供返回问卷的链接
                if st.button("返回填写问卷"):
                    st.query_params.clear()
                    st.rerun()

    except Exception as e:
        st.error(f"查询出错: {str(e)}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()


def main():
    params = st.query_params
    if 'feedback_id' in params:
        feedback_id = params['feedback_id']
        # 处理可能的列表情况（确保是字符串）
        if isinstance(feedback_id, list):
            feedback_id = feedback_id[0].strip()
        else:
            feedback_id = feedback_id.strip()
        show_feedback(feedback_id)
    else:
        show_questionnaire()


import os


def local_css(file_name):
    # 获取当前脚本所在目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, file_name)

    try:
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS文件未找到: {css_path}")
# ... (后面的代码保持不变)
if __name__ == "__main__":
    main()