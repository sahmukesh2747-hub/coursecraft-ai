


        
import json
import streamlit as st

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# =================================
# PAGE CONFIGURATION
# =================================

st.set_page_config(
    page_title="CourseCraft AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =================================
# YOUTUBE API FUNCTION
# =================================

@st.cache_data(ttl=3600, show_spinner=False)
def search_youtube_videos(query, max_results=5):

    try:
        api_key = st.secrets.get("YOUTUBE_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        raise RuntimeError(
            "YouTube API key is missing. "
            "Please configure YOUTUBE_API_KEY in Streamlit Secrets."
        )

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key,
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

        with urlopen(request, timeout=15) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        videos = []

        for item in data.get("items", []):

            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})

            if not video_id:
                continue

            videos.append({
                "title": snippet.get("title", "Untitled video"),
                "channel": snippet.get("channelTitle", "Unknown channel"),
                "url": f"https://www.youtube.com/watch?v={video_id}",
            })

        return videos

    except HTTPError as e:

        error_body = e.read().decode(
            "utf-8", errors="replace"
        )

        try:
            error_data = json.loads(error_body)
            reason = error_data["error"]["errors"][0]["reason"]
        except (ValueError, KeyError, IndexError, TypeError):
            reason = "unknown"

        if e.code == 429 or reason in (
            "rateLimitExceeded",
            "userRateLimitExceeded"
        ):
            raise RuntimeError(
                "YouTube rate limit reached. "
                "Please wait before trying again."
            )

        if e.code == 403 and reason == "quotaExceeded":
            raise RuntimeError(
                "Daily YouTube API quota exhausted. "
                "Please try again after the quota resets."
            )

        raise RuntimeError(
            f"YouTube API error {e.code}: {reason}"
        )

    except URLError as e:

        raise RuntimeError(
            f"Network error: {e.reason}"
        )

    except Exception as e:

        raise RuntimeError(
            f"Unexpected error: {str(e)}"
        )


# =================================
# CUSTOM CSS
# =================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    max-width: 1180px;
}

.hero {
    padding: 1.7rem;
    border-radius: 18px;
    background: linear-gradient(120deg,#182b55,#315a91);
    color: white;
}

.hero h1 {
    color: white;
    margin-bottom: .35rem;
}

.hero p {
    color: #e5edff;
    font-size: 1.05rem;
}

.small-muted {
    color: #8b93a7;
    font-size: .88rem;
}

.module-card {
    padding: 1rem 1.1rem;
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 14px;
    margin: .55rem 0;
}

.video-row {
    padding: .65rem .8rem;
    border-radius: 10px;
    background: rgba(128,128,128,.08);
    margin: .35rem 0;
}

</style>
""", unsafe_allow_html=True)


# =================================
# SESSION STATE
# =================================

if "course" not in st.session_state:
    st.session_state.course = None

if "completed" not in st.session_state:
    st.session_state.completed = set()


# =================================
# COURSE OUTLINE FUNCTION
# =================================

def build_outline(topic, level, weeks, videos_per_module):

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
        ]),
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
            "topics": topics[:videos_per_module],
        })

    return modules


# =================================
# SIDEBAR
# =================================

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
    "CourseCraft AI • Starter version"
)


# =================================
# PAGE 1: CREATE A COURSE
# =================================

if page == "Create a course":

    st.markdown("""
    <div class="hero">

        <h1>Build a course from YouTube</h1>

        <p>
        Tell us what you want to learn.
        Create a structured learning path and
        find lecture videos topic by topic.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.write("")

    left, right = st.columns(
        [1.35, 0.85],
        gap="large"
    )

    with left:

        st.subheader("Course details")

        with st.form("create_course"):

            topic = st.text_input(
                "What do you want to learn?",
                placeholder=(
                    "e.g. Data Structures and Algorithms in Java"
                )
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
                    "Course length (weeks)",
                    3, 12, 8
                )

            videos_per_module = st.slider(
                "Topics per module",
                2, 3, 3
            )

            goal = st.text_area(
                "Your learning goal (optional)",
                placeholder=(
                    "e.g. Prepare for interviews "
                    "and solve LeetCode problems"
                )
            )

            submitted = st.form_submit_button(
                "✨ Create my learning path",
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
                        videos_per_module
                    ),
                }

                st.session_state.completed = set()

                st.success(
                    "Your starter learning path is ready!"
                )

    with right:

        st.subheader("What you'll get")

        st.markdown("""
        - A course split into modules
        - Topics arranged from foundations to advanced learning
        - Up to 5 YouTube videos for each topic
        - Video titles and teacher/channel names
        - Clickable video links
        - Checkboxes to track completed lessons
        """)

        st.info(
            "The course outline currently uses a starter template. "
            "AI syllabus generation and automatic teacher ranking "
            "are future features."
        )


    # =================================
    # DISPLAY GENERATED COURSE
    # =================================

    if st.session_state.course:

        st.divider()

        course = st.session_state.course

        st.subheader(
            f"📚 {course['topic']}"
        )

        st.caption(
            f"{course['level']} • {course['weeks']} weeks"
        )

        if course["goal"]:

            st.write(
                "**Your goal:**",
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


        # =================================
        # DISPLAY MODULES AND VIDEOS
        # =================================

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
                                key in st.session_state.completed
                            ),
                            label_visibility="collapsed"
                        )

                        if checked:

                            st.session_state.completed.add(key)

                        else:

                            st.session_state.completed.discard(key)

                    with col2:

                        st.markdown(
                            f"### {lesson}"
                        )

                        search_query = (
                            f"{course['topic']} "
                            f"{lesson} "
                            f"{course['level']} tutorial"
                        )

                        try:

                            with st.spinner(
                                "Finding YouTube videos..."
                            ):

                                videos = search_youtube_videos(
                                    search_query,
                                    max_results=5
                                )

                        except RuntimeError as e:

                            st.warning(str(e))
                            videos = None

                        if videos is not None:

                            if videos:

                                for video in videos:

                                    st.markdown(
                                        f"- **{video['title']}**  \n"
                                        f"Teacher: {video['channel']}  \n"
                                        f"[▶ Watch Video]({video['url']})"
                                    )

                            else:

                                st.info(
                                    "No matching YouTube videos found."
                                )


# =================================
# PAGE 2: LEARNING DASHBOARD
# =================================

elif page == "My learning dashboard":

    st.title(
        "📈 My learning dashboard"
    )

    if not st.session_state.course:

        st.info(
            "You haven't created a course yet. "
            "Open Create a course to get started."
        )

    else:

        c = st.session_state.course

        st.subheader(
            c["topic"]
        )

        total = sum(
            len(m["topics"])
            for m in c["modules"]
        )

        done = len(
            st.session_state.completed
        )

        st.metric(
            "Lessons completed",
            f"{done}/{total}"
        )

        st.progress(
            done / total if total else 0
        )

        st.write(
            f"**Level:** {c['level']}  ·  "
            f"**Duration:** {c['weeks']} weeks"
        )

        st.caption(
            "Progress is stored in this browser session "
            "only in this starter version."
        )


# =================================
# PAGE 3: ABOUT PROJECT
# =================================

else:

    st.title(
        "About CourseCraft AI"
    )

    st.write(
        "CourseCraft AI is a personal learning assistant "
        "that helps organize learning through relevant "
        "YouTube lectures."
    )

    st.subheader(
        "Build roadmap"
    )

    st.markdown("""
    1. **Starter website** — course form, outline and progress tracker.
    2. **YouTube integration** — retrieve video titles, channels and links using YouTube Data API v3.
    3. **AI syllabus planner** — generate a topic sequence and prerequisites with an LLM.
    4. **Video organizer** — map videos to topics, remove duplicates and rank relevance.
    5. **Persistence** — save courses and progress in a database.
    """)

    st.info(
        "YouTube search integration is added in the code. "
        "It requires a valid API key in Streamlit Secrets. "
        "AI-based video ranking is not implemented yet."
    )


# =================================
# END OF PROJECT
# =================================

         