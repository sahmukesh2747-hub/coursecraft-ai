import streamlit as st
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


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
# YOUTUBE API FUNCTION
# ==========================================

@st.cache_data(ttl=3600, show_spinner=False)
def search_youtube_videos(api_key, query, max_results=5):

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key
    }

    url = (
        "https://www.googleapis.com/youtube/v3/search?"
        + urlencode(params)
    )

    try:

        request = Request(
            url,
            headers={"Accept": "application/json"}
        )

        with urlopen(request, timeout=20) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        videos = []

        for item in data.get("items", []):

            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            videos.append({
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "url": (
                    "https://www.youtube.com/watch?v="
                    + video_id
                )
            })

        return {
            "videos": videos,
            "error": None
        }

    except HTTPError as e:

        try:
            error_data = json.loads(
                e.read().decode("utf-8")
            )

            reason = (
                error_data.get("error", {})
                .get("errors", [{}])[0]
                .get("reason", "")
            )

        except Exception:
            reason = ""

        if e.code == 429 or reason == "rateLimitExceeded":

            message = (
                "YouTube rate limit reached. "
                "Please wait before searching again."
            )

        elif reason in [
            "quotaExceeded",
            "dailyLimitExceeded"
        ]:

            message = (
                "YouTube daily API quota exhausted. "
                "Wait until the quota resets."
            )

        elif e.code == 403:

            message = (
                "YouTube API access denied. "
                "Check API key restrictions and API settings."
            )

        elif e.code == 400:

            message = (
                "Invalid YouTube API request. "
                "Please check the search query."
            )

        else:

            message = f"YouTube API error: HTTP {e.code}"

        return {
            "videos": [],
            "error": message
        }

    except URLError:

        return {
            "videos": [],
            "error": (
                "Network error. Check your internet connection."
            )
        }

    except Exception as e:

        return {
            "videos": [],
            "error": str(e)
        }


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

        ("Intermediate concepts", [
            "Important techniques",
            "Real-world applications",
            "Worked examples"
        ]),

        ("Projects", [
            "Mini project",
            "Putting concepts together",
            "Review and improvement"
        ]),

        ("Advanced learning", [
            "Advanced concepts",
            "Optimization and best practices",
            "Final revision"
        ])
    ]

    count = min(6, max(3, weeks))

    selected = stages[:count]

    modules = []

    for i, (name, topics) in enumerate(
        selected, start=1
    ):

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
    "CourseCraft AI • Improved Starter Version"
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

                # Clear old video results
                for key in list(st.session_state.keys()):

                    if key.startswith("videos-"):
                        del st.session_state[key]

                st.success(
                    "Your learning path has been created!"
                )

    with right:

        st.subheader("What You'll Get")

        st.markdown("""
        - Structured learning modules
        - Beginner to advanced topics
        - YouTube lecture search
        - Video titles and channel names
        - Direct video links
        - Lesson completion tracker
        - Learning progress dashboard
        """)

        st.info(
            "This starter version uses a predefined "
            "course outline. AI syllabus generation "
            "will be added in a future version."
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
        # API KEY
        # ==========================================

        api_key = st.secrets.get(
            "YOUTUBE_API_KEY",
            ""
        )


        # ==========================================
        # DISPLAY MODULES
        # ==========================================

        for mi, module in enumerate(
            course["modules"]
        ):

            with st.expander(
                f"{module['name']} · Week {module['week']}",
                expanded=(mi == 0)
            ):

                for ti, lesson in enumerate(
                    module["topics"]
                ):

                    key = f"{mi}-{ti}"

                    col1, col2 = st.columns(
                        [0.08, 0.92]
                    )

                    with col1:

                        checked = st.checkbox(
                            "Done",
                            key=f"check-{key}",
                            value=(
                                key in
                                st.session_state.completed
                            ),
                            label_visibility="collapsed"
                        )

                        if checked:

                            st.session_state.completed.add(
                                key
                            )

                        else:

                            st.session_state.completed.discard(
                                key
                            )

                    with col2:

                        st.markdown(
                            f"### {lesson}"
                        )

                        search_query = (
                            f"{course['topic']} "
                            f"{lesson} "
                            f"{course['level']} tutorial"
                        )

                        if not api_key:

                            st.error(
                                "YouTube API key is missing. "
                                "Add YOUTUBE_API_KEY in "
                                "Streamlit Secrets."
                            )

                        else:

                            if st.button(
                                "🔍 Find YouTube Videos",
                                key=f"search-{key}"
                            ):

                                with st.spinner(
                                    "Searching YouTube..."
                                ):

                                    result = search_youtube_videos(
                                        api_key,
                                        search_query,
                                        max_results=5
                                    )

                                    st.session_state[
                                        f"videos-{key}"
                                    ] = result

                            result = st.session_state.get(
                                f"videos-{key}"
                            )

                            if result is not None:

                                if result["error"]:

                                    st.warning(
                                        result["error"]
                                    )

                                elif result["videos"]:

                                    for video in result["videos"]:

                                        st.markdown(
                                            f"""
                                            <div class="video-card">
                                            <b>{video['title']}</b><br>
                                            Teacher: {video['channel']}<br>
                                            <a href="{video['url']}"
                                            target="_blank">
                                            ▶ Watch Video
                                            </a>
                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )

                                else:

                                    st.info(
                                        "No matching videos found."
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

        st.metric(
            "Lessons Completed",
            f"{done}/{total}"
        )

        st.progress(
            done / total if total else 0
        )

        percentage = (
            round(done / total * 100)
            if total else 0
        )

        st.metric(
            "Course Progress",
            f"{percentage}%"
        )

        st.write(
            f"**Level:** {course['level']}"
        )

        st.write(
            f"**Duration:** {course['weeks']} weeks"
        )

        st.caption(
            "Progress is stored in the current "
            "browser session in this starter version."
        )


# ==========================================
# PAGE 3: ABOUT PROJECT
# ==========================================

else:

    st.title("🎓 About CourseCraft AI")

    st.write(
        "CourseCraft AI is a personal learning "
        "assistant that helps learners organize "
        "their education through YouTube lectures."
    )

    st.subheader("Technologies Used")

    st.markdown("""
    1. **Python** – Main programming language.
    2. **Streamlit** – Web application framework.
    3. **YouTube Data API v3** – Video search integration.
    4. **JSON** – Data exchange format.
    5. **GitHub** – Source code management.
    """)

    st.subheader("Project Features")

    st.markdown("""
    - Course outline generation
    - Topic-wise learning modules
    - YouTube video search
    - Learning progress tracking
    - Dashboard
    - API error handling
    - Cached video search results
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
