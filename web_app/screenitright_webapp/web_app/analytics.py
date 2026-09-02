import streamlit as st

from feedback import FeedbackLoop


@st.cache_resource
def get_feedback_loop():
    return FeedbackLoop()


def render_feedback_loop():
    st.subheader("Closed-Loop Feedback")
    st.caption(
        "PILLAR 4 · IDENTIFY → DEFEND → FEEDBACK → EVOLVE"
    )

    loop = get_feedback_loop()

    st.markdown("### Test the PhantomGuard closed loop")

    text = st.text_area(
        "Input to scan",
        placeholder=(
            "Enter a request or adversarial prompt..."
        ),
        height=120,
    )

    category = st.selectbox(
        "Category",
        [
            "user",
            "adversarial",
            "prompt_injection",
            "fraud",
        ],
    )

    if st.button(
        "Run Closed-Loop Scan",
        type="primary",
        use_container_width=True,
    ):
        if not text.strip():
            st.warning("Enter some text first.")
            return

        with st.spinner("Running IDENTIFY → DEFEND → FEEDBACK..."):
            result = loop.run(
                text=text,
                category=category,
                evolve=True,
            )

        st.session_state["last_feedback_result"] = result

    result = st.session_state.get(
        "last_feedback_result"
    )

    if result is not None:
        st.markdown("### Result")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Identified",
                "YES"
                if result.identification.detected
                else "NO",
            )

        with col2:
            st.metric(
                "Defended",
                "BLOCKED"
                if result.defense.blocked
                else "ALLOWED",
            )

        with col3:
            st.metric(
                "Detection Score",
                f"{result.identification.score:.2f}",
            )

        with col4:
            st.metric(
                "Feedback Score",
                f"{result.feedback.score:.2f}",
            )

        if result.defense.blocked:
            st.error(
                "🛡️ PhantomGuard blocked this request."
            )
        else:
            st.success(
                "Request was allowed."
            )

        st.markdown("### Evaluation")

        st.write(
            result.evaluation.reason
        )

        st.markdown("### Defense Output")

        st.code(
            result.defense.output
            or "No output returned."
        )

        if result.next_attack:
            st.markdown("### Evolved Attack")

            st.code(
                result.next_attack.text
            )

        with st.expander(
            "View complete loop data"
        ):
            st.json(
                loop.serialize(result)
            )

    st.divider()

    st.markdown("### Feedback Statistics")

    stats = loop.stats()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Total Cycles",
            stats["total"],
        )

    with c2:
        st.metric(
            "Average Score",
            f"{stats['average_score']:.2f}",
        )

    with c3:
        st.metric(
            "Successful",
            stats["successful_attacks"],
        )

    with c4:
        st.metric(
            "Failed",
            stats["failed_attacks"],
        )