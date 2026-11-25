import streamlit as st
from urllib.parse import quote_plus


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CourseCraft AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    max-width: 1180px;
}

.hero {
    padding: 2rem;
    border-radius: 18px;
    background: linear-gradient(120deg,#182b55,#315a91);
    color: white;
}

.hero h1 {
    color: white;
}

.hero p {
    color: #e5edff;
    font-size: 1.05rem;
}

.video-card {
    padding: 12px;
    border-radius: 10px;
    background: rgba(128,128,128,0.08);
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================

if "course" not in st.session_state:
    st.session_state.course = None

if "completed" not in st.session_state:
    st.session_state.completed = set()


# ==========================================
# YOUTUBE SEARCH LINK FUNCTION
# ==========================================

def get_youtube_link(topic, lesson, level):

    query = f"{topic} {lesson} {level} tutorial"

    return (
        "https://www.youtube.com/results?search_query="
        + quote_plus(query)
    )


# ==========================================
# COURSE OUTLINE FUNCTION
# ==========================================

def build_outline(topic, level, weeks, topics_per_module):

    stages = [

        ("Foundations", [
            "Introduction and learning goals",
            "Core terminology",
            "Essential concepts"
        ]),

        ("Fundamentals", [
            "Main building blocks",
            "How the concepts work",
            "Guided examples"
        ]),

        ("Practice", [
            "Beginner exercises",
            "Common mistakes",
            "Problem-solving patterns"
        ]),

        ("Intermediate Concepts", [
            "Important techniques",
            "Real-world applications",
            "Worked examples"
        ]),

        ("Projects", [
            "Mini project",
            "Putting concepts together",
            "Review and improvement"
        ]),

        ("Advanced Learning", [
            "Advanced concepts",
            "Optimization and best practices",
            "Final revision"
        ])
    ]

    count = min(6, max(3, weeks))

    selected = stages[:count]

    modules = []

    for i, (name, topics) in enumerate(selected, start=1):

        modules.append({
            "name": f"Module {i}: {name}",
            "week": min(weeks, i),
            "topics": topics[:topics_per_module]
        })

    return modules


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("🎓 CourseCraft AI")

st.sidebar.caption(
    "Your personal YouTube course planner"
)

page = st.sidebar.radio(
    "Workspace",
    [
        "Create a course",
        "My learning dashboard",
        "About this project"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "CourseCraft AI • Improved Version"
)


# ==========================================
# PAGE 1: CREATE A COURSE
# ==========================================

if page == "Create a course":

    st.markdown("""
    <div class="hero">
        <h1>🎓 Build Your Own Learning Path</h1>
        <p>
        Choose what you want to learn.
        Create a structured course and find
        relevant YouTube lectures.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    left, right = st.columns(
        [1.35, 0.85],
        gap="large"
    )

    with left:

        st.subheader("Course Details")

        with st.form("create_course"):

            topic = st.text_input(
                "What do you want to learn?",
                placeholder="e.g. Data Structures and Algorithms in Java"
            )

            c1, c2 = st.columns(2)

            with c1:

                level = st.selectbox(
                    "Your current level",
                    [
                        "Beginner",
                        "Intermediate",
                        "Advanced"
                    ]
                )

            with c2:

                weeks = st.slider(
                    "Course duration (weeks)",
                    3, 12, 8
                )

            topics_per_module = st.slider(
                "Topics per module",
                2, 3, 3
            )

            goal = st.text_area(
                "Your learning goal (optional)",
                placeholder="e.g. Prepare for interviews"
            )

            submitted = st.form_submit_button(
                "✨ Create My Learning Path",
                use_container_width=True
            )

        if submitted:

            if not topic.strip():

                st.warning(
                    "Please enter a topic first."
                )

            else:

                st.session_state.course = {
                    "topic": topic.strip(),
                    "level": level,
                    "weeks": weeks,
                    "goal": goal.strip(),

                    "modules": build_outline(
                        topic.strip(),
                        level,
                        weeks,
                        topics_per_module
                    )
                }

                st.session_state.completed = set()

                st.success(
                    "Your learning path has been created!"
                )

    with right:

        st.subheader("What You'll Get")

        st.markdown("""
        - Structured learning modules
        - Beginner to advanced topics
        - YouTube tutorial search
        - Direct YouTube search links
        - Lesson completion tracker
        - Learning progress dashboard
        """)

        st.info(
            "This version uses a predefined course outline "
            "and YouTube search links. AI syllabus generation "
            "can be added in a future version."
        )


    # ==========================================
    # DISPLAY GENERATED COURSE
    # ==========================================

    if st.session_state.course:

        st.divider()

        course = st.session_state.course

        st.subheader(
            f"📚 {course['topic']}"
        )

        st.caption(
            f"{course['level']} • "
            f"{course['weeks']} weeks"
        )

        if course["goal"]:

            st.write(
                "**Your learning goal:**",
                course["goal"]
            )

        total = sum(
            len(m["topics"])
            for m in course["modules"]
        )

        done = len(
            st.session_state.completed
        )

        st.progress(
            done / total if total else 0
        )

        st.caption(
            f"{done} of {total} topics completed"
        )


        # ==========================================
        # DISPLAY MODULES AND LESSONS
        # ==========================================

        for mi, module in enumerate(course["modules"]):

            with st.expander(
                f"{module['name']} · Week {module['week']}",
                expanded=(mi == 0)
            ):

                for ti, lesson in enumerate(module["topics"]):

                    key = f"{mi}-{ti}"

                    col1, col2 = st.columns([0.08, 0.92])

                    with col1:

                        checked = st.checkbox(
                            "Done",
                            key=f"check-{key}",
                            value=(
                                key in st.session_state.completed
                            ),
                            label_visibility="collapsed"
                        )

                        if checked:

                            st.session_state.completed.add(key)

                        else:

                            st.session_state.completed.discard(key)

                    with col2:

                        st.markdown(f"### {lesson}")

                        youtube_link = get_youtube_link(
                            course["topic"],
                            lesson,
                            course["level"]
                        )

                        st.link_button(
                            "▶ Find YouTube Videos",
                            youtube_link,
                            use_container_width=True
                        )

                    st.divider()


# ==========================================
# PAGE 2: LEARNING DASHBOARD
# ==========================================

elif page == "My learning dashboard":

    st.title("📈 My Learning Dashboard")

    if not st.session_state.course:

        st.info(
            "You haven't created a course yet. "
            "Go to Create a course to get started."
        )

    else:

        course = st.session_state.course

        st.subheader(course["topic"])

        total = sum(
            len(m["topics"])
            for m in course["modules"]
        )

        done = len(
            st.session_state.completed
        )

        percentage = (
            round(done / total * 100)
            if total else 0
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Lessons Completed",
                f"{done}/{total}"
            )

        with col2:

            st.metric(
                "Course Progress",
                f"{percentage}%"
            )

        st.progress(
            done / total if total else 0
        )

        st.write(
            f"**Level:** {course['level']}"
        )

        st.write(
            f"**Duration:** {course['weeks']} weeks"
        )

        if course["goal"]:

            st.write(
                f"**Learning Goal:** {course['goal']}"
            )

        st.caption(
            "Progress is stored in the current browser "
            "session in this starter version."
        )


# ==========================================
# PAGE 3: ABOUT PROJECT
# ==========================================

else:

    st.title("🎓 About CourseCraft AI")

    st.write(
        "CourseCraft AI is a personal learning "
        "assistant that helps learners organize "
        "their education through structured modules "
        "and YouTube learning resources."
    )

    st.subheader("Technologies Used")

    st.markdown("""
    1. **Python** – Main programming language.
    2. **Streamlit** – Web application framework.
    3. **YouTube Search Links** – Educational video discovery.
    4. **GitHub** – Source code management.
    """)

    st.subheader("Project Features")

    st.markdown("""
    - Course outline generation
    - Topic-wise learning modules
    - YouTube tutorial search
    - Learning progress tracking
    - Interactive dashboard
    - Beginner-friendly interface
    """)

    st.subheader("Future Improvements")

    st.markdown("""
    1. AI-based syllabus generation.
    2. Automatic video relevance ranking.
    3. User login and registration.
    4. Database integration.
    5. Personalized learning recommendations.
    6. Course certificates and assessments.
    """)

    st.success(
        "CourseCraft AI • Learn Smarter, Step by Step."
    )
