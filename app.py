import streamlit as st
from urllib.parse import quote_plus

st.set_page_config(
    page_title="CourseCraft AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1180px;}
.hero {padding: 1.7rem; border-radius: 18px; background: linear-gradient(120deg,#182b55,#315a91); color:white;}
.hero h1 {color:white; margin-bottom:.35rem;}
.hero p {color:#e5edff; font-size:1.05rem;}
.small-muted {color: #8b93a7; font-size:.88rem;}
.module-card {padding:1rem 1.1rem; border:1px solid rgba(128,128,128,.25); border-radius:14px; margin:.55rem 0;}
.video-row {padding:.65rem .8rem; border-radius:10px; background:rgba(128,128,128,.08); margin:.35rem 0;}
</style>
""", unsafe_allow_html=True)

if "course" not in st.session_state:
    st.session_state.course = None
if "completed" not in st.session_state:
    st.session_state.completed = set()

def build_outline(topic, level, weeks, videos_per_module):
    # Starter syllabus template. Replace with an LLM-generated syllabus in the AI integration milestone.
    stages = [
        ("Foundations", ["Introduction and learning goals", "Core terminology", "Essential concepts"]),
        ("Fundamentals", ["Main building blocks", "How the concepts work", "Guided examples"]),
        ("Practice", ["Beginner exercises", "Common mistakes", "Problem-solving patterns"]),
        ("Intermediate concepts", ["Important techniques", "Real-world applications", "Worked examples"]),
        ("Projects", ["Mini project", "Putting concepts together", "Review and improvement"]),
        ("Advanced learning", ["Advanced concepts", "Optimization and best practices", "Final revision"]),
    ]
    count = min(6, max(3, weeks))
    selected = stages[:count]
    modules = []
    for i, (name, topics) in enumerate(selected, start=1):
        modules.append({
            "name": f"Module {i}: {name}",
            "week": min(weeks, i),
            "topics": topics[:videos_per_module],
        })
    return modules

st.sidebar.title("🎓 CourseCraft AI")
st.sidebar.caption("Your personal YouTube course planner")
page = st.sidebar.radio("Workspace", ["Create a course", "My learning dashboard", "About this project"])
st.sidebar.divider()
st.sidebar.caption("Starter version • Local prototype")

if page == "Create a course":
    st.markdown("""
    <div class="hero">
      <h1>Build a course from YouTube</h1>
      <p>Tell us what you want to learn. Create a structured learning path and find lecture videos topic by topic.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.35, 0.85], gap="large")
    with left:
        st.subheader("Course details")
        with st.form("create_course"):
            topic = st.text_input("What do you want to learn?", placeholder="e.g. Data Structures and Algorithms in Java")
            c1, c2 = st.columns(2)
            with c1:
                level = st.selectbox("Your current level", ["Beginner", "Intermediate", "Advanced"])
            with c2:
                weeks = st.slider("Course length (weeks)", 3, 12, 8)
            videos_per_module = st.slider("Topics per module", 2, 3, 3)
            goal = st.text_area("Your learning goal (optional)", placeholder="e.g. Prepare for interviews and solve LeetCode problems")
            submitted = st.form_submit_button("✨ Create my learning path", use_container_width=True)
        if submitted:
            if not topic.strip():
                st.warning("Please enter a topic first.")
            else:
                st.session_state.course = {
                    "topic": topic.strip(),
                    "level": level,
                    "weeks": weeks,
                    "goal": goal.strip(),
                    "modules": build_outline(topic.strip(), level, weeks, videos_per_module),
                }
                st.session_state.completed = set()
                st.success("Your starter learning path is ready!")
    with right:
        st.subheader("What you'll get")
        st.markdown("""
        - A course split into modules
        - Topics arranged from foundations to advanced learning
        - YouTube search links for each topic
        - Checkboxes to track completed lessons
        - A saved course view during this session
        """)
        st.info("This first version creates a starter outline. AI syllabus generation and automatic video selection will be connected in the next build stage.")

    if st.session_state.course:
        st.divider()
        course = st.session_state.course
        st.subheader(f"📚 {course['topic']}")
        st.caption(f"{course['level']} • {course['weeks']} weeks")
        if course["goal"]:
            st.write("**Your goal:**", course["goal"])
        total = sum(len(m["topics"]) for m in course["modules"])
        done = len(st.session_state.completed)
        st.progress(done / total if total else 0)
        st.caption(f"{done} of {total} topics completed")
        for mi, module in enumerate(course["modules"]):
            with st.expander(f"{module['name']}  ·  Week {module['week']}", expanded=(mi == 0)):
                for ti, lesson in enumerate(module["topics"]):
                    key = f"{mi}-{ti}"
                    col1, col2 = st.columns([0.08, 0.92])
                    with col1:
                        checked = st.checkbox("Done", key=f"check-{key}", value=key in st.session_state.completed, label_visibility="collapsed")
                        if checked:
                            st.session_state.completed.add(key)
                        else:
                            st.session_state.completed.discard(key)
                    with col2:
                        search = quote_plus(f"{course['topic']} {lesson} {course['level']} tutorial")
                        st.markdown(f"**{lesson}**  \n[Search YouTube lectures](https://www.youtube.com/results?search_query={search})")
        st.caption("Note: YouTube links open search results; this prototype does not yet fetch, rank, or verify individual videos.")

elif page == "My learning dashboard":
    st.title("📈 My learning dashboard")
    if not st.session_state.course:
        st.info("You haven't created a course yet. Open **Create a course** to get started.")
    else:
        c = st.session_state.course
        st.subheader(c["topic"])
        total = sum(len(m["topics"]) for m in c["modules"])
        done = len(st.session_state.completed)
        st.metric("Lessons completed", f"{done}/{total}")
        st.progress(done / total if total else 0)
        st.write(f"**Level:** {c['level']}  ·  **Duration:** {c['weeks']} weeks")
        st.caption("Progress is stored in this browser session only in this starter version.")

else:
    st.title("About CourseCraft AI")
    st.write("CourseCraft AI is a personal learning assistant that will turn a subject into an organized course using relevant YouTube lectures.")
    st.subheader("Build roadmap")
    st.markdown("""
    1. **Starter website** — course form, outline and progress tracker (included).
    2. **YouTube integration** — retrieve video titles, channels, links and durations with YouTube Data API v3.
    3. **AI syllabus planner** — generate a topic sequence and prerequisites with an LLM.
    4. **Video organizer** — map videos to topics, remove duplicates and rank relevance.
    5. **Persistence** — save courses and progress in SQLite.
    """)
    st.warning("The current version is a working frontend prototype. It does not yet call an AI model or YouTube Data API.")
