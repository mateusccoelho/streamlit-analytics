"""
Displays the analytics results within streamlit.
"""

import altair as alt
import pandas as pd
import streamlit as st

from . import utils


def show_results(counts, reset_callback, unsafe_password=None):
    """Show analytics results in streamlit, asking for password if given."""

    # Show header.
    st.title("Analytics Dashboard")
    st.markdown(
        """
        Psst! 👀 You found a secret section generated by 
        [streamlit-analytics](https://github.com/jrieke/streamlit-analytics). 
        If you didn't mean to go here, remove `?analytics=on` from the URL.
        """
    )

    # Ask for password if one was given.
    show = True
    if unsafe_password is not None:
        password_input = st.text_input(
            "Enter password to show results", type="password"
        )
        if password_input != unsafe_password:
            show = False
            if len(password_input) > 0:
                st.write("Nope, that's not correct ☝️")

    if show:
        # Show traffic.
        st.header("Traffic")
        st.write(f"since {counts['start_time']}")
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Pageviews",
            counts["total_pageviews"],
            help="Every time a user (re-)loads the site.",
        )
        col2.metric(
            "Script runs",
            counts["total_script_runs"],
            help="Every time Streamlit reruns upon changes or interactions.",
        )
        col3.metric(
            "Time spent",
            utils.format_seconds(counts["total_time_seconds"]),
            help="Time from initial page load to last widget interaction, summed over all users.",
        )
        st.write("")

        # Plot altair chart with pageviews and script runs.
        try:
            alt.themes.enable("streamlit")
        except:
            pass  # probably old Streamlit version

        df = pd.DataFrame(counts["per_day"])
        # Formatting date by ISO-8601 to fix altair's date parsing bug 
        df["days"] = df["days"] + "T00:00:00"

        base = alt.Chart(df).encode(
            x=alt.X("monthdate(days):O", axis=alt.Axis(title="", grid=True))
        )
        line1 = base.mark_line(point=True, stroke="#5276A7").encode(
            alt.Y(
                "pageviews:Q",
                axis=alt.Axis(
                    titleColor="#5276A7",
                    tickColor="#5276A7",
                    labelColor="#5276A7",
                    format=".0f",
                    tickMinStep=1,
                ),
                scale=alt.Scale(domain=(0, df["pageviews"].max() + 1)),
            )
        )
        line2 = base.mark_line(point=True, stroke="#57A44C").encode(
            alt.Y(
                "script_runs:Q",
                axis=alt.Axis(
                    title="script runs",
                    titleColor="#57A44C",
                    tickColor="#57A44C",
                    labelColor="#57A44C",
                    format=".0f",
                    tickMinStep=1,
                ),
            )
        )
        layer = (
            alt.layer(line1, line2)
            .resolve_scale(y="independent")
            .configure_axis(titleFontSize=15, labelFontSize=12, titlePadding=10)
        )
        st.altair_chart(layer, use_container_width=True)

        # Show widget interactions.
        st.header("Widget interactions")
        st.markdown(
            """
            Find out how users interacted with your app!
            <br>
            Numbers indicate how often a button was clicked, how often a specific text 
            input was given, ...
            <br>
            <sub>Note: Numbers only increase if the state of the widget
            changes, not every time streamlit runs the script.</sub>
            """,
            unsafe_allow_html=True,
        )
        st.write(counts["widgets"])

        # Show button to reset analytics.
        st.header("Danger zone")
        with st.expander("Here be dragons 🐲🔥"):
            st.write(
                """
                Here you can reset all analytics results.
                
                **This will erase everything tracked so far. You will not be able to 
                retrieve it. This will also overwrite any results synced to Firestore.**
                """
            )
            reset_prompt = st.selectbox(
                "Continue?",
                [
                    "No idea what I'm doing here",
                    "I'm absolutely sure that I want to reset the results",
                ],
            )
            if reset_prompt == "I'm absolutely sure that I want to reset the results":
                reset_clicked = st.button("Click here to reset")
                if reset_clicked:
                    reset_callback()
                    st.write("Done! Please refresh the page.")
