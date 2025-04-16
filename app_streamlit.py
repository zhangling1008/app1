import streamlit as st
import pymysql
import pyqrcode
from io import BytesIO
import base64
from config import DB_CONFIG

# 页面配置
st.set_page_config(
    page_title="心理调查问卷",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# 自定义CSS样式
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("assets/style.css")


# 数据库连接
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


# 保存问卷数据
def save_to_database(data):
    try:
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


# 生成二维码
def generate_qrcode(url):
    qr = pyqrcode.create(url)
    buffer = BytesIO()
    qr.png(buffer, scale=6)
    return base64.b64encode(buffer.getvalue()).decode()


# 问卷页面
def show_questionnaire():
    st.title("🧠 心理调查问卷")
    st.markdown("感谢您参与本次心理调查！您的回答将帮助我们更好地了解您的心理状态和需求，本问卷所有数据将严格保密。")

    with st.form("survey_form", clear_on_submit=True):
        # 基本信息
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名", key="name", max_chars=50)
            age = st.number_input("年龄", min_value=0, max_value=120, key="age")
        with col2:
            gender = st.selectbox("性别", ["男", "女", "其他"], key="gender")
            student_id = st.text_input("学号", key="student_id")

        class_ = st.text_input("班级", key="class_")

        # 问题列表
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
            if i == 41:  # 特殊问题
                ans = st.radio(
                    f"Q{i}",
                    options=["从不", "很少", "有时", "经常", "总是"],
                    index=2,  # 默认选中"有时"
                    horizontal=True,
                    key=f"q{i}"
                )
            else:
                ans = st.radio(
                    f"Q{i}",
                    options=["从不", "很少", "有时", "经常", "总是"],
                    horizontal=True,
                    key=f"q{i}"
                )
            answers[f"q{i}"] = ["从不", "很少", "有时", "经常", "总是"].index(ans) + 1

        if st.form_submit_button("提交问卷"):
            # 准备数据
            form_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "student_id": student_id,
                "class_": class_,
                **answers
            }

            if save_to_database(form_data):
                # 生成反馈链接
                feedback_url = f"{st.experimental_get_this_url()}?feedback_id={student_id}"
                qr_img = generate_qrcode(feedback_url)

                # 显示成功信息
                st.success("问卷提交成功！")
                st.balloons()

                # 显示二维码
                st.subheader("扫描二维码查看个性化反馈")
                st.markdown(
                    f'<img src="data:image/png;base64,{qr_img}" width="200">',
                    unsafe_allow_html=True
                )

                # 直接链接
                st.markdown(f"[点击查看反馈]({feedback_url})")


# 反馈页面
def show_feedback(feedback_id):
    st.title("📊 您的个性化心理建议")

    # 从数据库获取数据
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM survey WHERE student_id = %s", (feedback_id,))
            result = cursor.fetchone()

        if result:
            # 显示基本信息
            st.write(f"**姓名**: {result['name']}")
            st.write(f"**年龄**: {result['age']}")
            st.write(f"**性别**: {result['gender']}")

            # 分析结果
            st.subheader("分析结果")

            # 示例分析逻辑（实际应根据专业规则）
            total_score = sum([v for k, v in result.items() if k.startswith('q') and k != 'q41'])
            avg_score = total_score / 95

            if avg_score < 2:
                st.success("您的心理健康状况良好")
            elif avg_score < 3.5:
                st.warning("您存在轻度心理困扰")
            else:
                st.error("您可能存在显著心理困扰，建议寻求专业帮助")

            # 详细建议
            st.subheader("专业建议")
            st.markdown("""
            - 每天保持7-8小时规律睡眠
            - 每周进行3次以上有氧运动
            - 练习正念冥想缓解压力
            - 如有需要可联系学校心理咨询中心
            """)

        else:
            st.warning("未找到您的问卷记录")

    except Exception as e:
        st.error(f"数据库错误: {str(e)}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()


# 主程序
def main():
    # 检查URL参数
    query_params = st.experimental_get_query_params()
    if 'feedback_id' in query_params:
        show_feedback(query_params['feedback_id'][0])
    else:
        show_questionnaire()


if __name__ == "__main__":
    main()