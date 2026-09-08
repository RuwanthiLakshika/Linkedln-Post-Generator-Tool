import streamlit as st
from few_shot import FewShotPosts
from llm_helper import get_model_options
from post_generator import generate_post


# Options for length and language
length_options = ["Short", "Medium", "Long"]
language_options = ["English", "Hinglish"]


# Main app layout
def main():
    st.subheader("LinkedIn Post Generator: Codebasics")

    # Create three columns for the dropdowns
    col1, col2, col3 = st.columns(3)

    fs = FewShotPosts()
    tags = fs.get_tags()
    with col1:
        # Dropdown for Topic (Tags)
        selected_tag = st.selectbox("Topic", options=tags)

    with col2:
        # Dropdown for Length
        selected_length = st.selectbox("Length", options=length_options)

    with col3:
        # Dropdown for Language
        selected_language = st.selectbox("Language", options=language_options)

    model_options = get_model_options()
    selected_model_label = st.selectbox(
        "Model",
        options=list(model_options),
        key="selected_model_label",
    )
    selected_model = model_options[selected_model_label]


    # Generate Button
    if st.button("Generate"):
        try:
            post, usage = generate_post(
                selected_length,
                selected_language,
                selected_tag,
                selected_model,
            )
            st.write(post)
            st.caption(
                "Tokens used for this request: "
                f"{usage.get('input_tokens', usage.get('prompt_tokens', 0)):,} input + "
                f"{usage.get('output_tokens', usage.get('completion_tokens', 0)):,} output = "
                f"{usage.get('total_tokens', 0):,} total."
            )
            remaining_tokens = usage.get("remaining_tokens")
            limit_tokens = usage.get("limit_tokens")
            reset_tokens = usage.get("reset_tokens")
            if remaining_tokens:
                reset_message = f" Resets in about {reset_tokens}." if reset_tokens else ""
                limit_message = (
                    f" / {int(limit_tokens):,}" if limit_tokens else ""
                )
                st.info(
                    f"Tokens remaining in the current Groq per-minute window: "
                    f"{int(remaining_tokens):,}{limit_message} TPM.{reset_message}"
                )
            else:
                st.warning("Groq did not return remaining-token information for this request.")
        except Exception as error:
            error_text = str(error)
            if "rate_limit" in error_text.lower() or "quota" in error_text.lower():
                st.error(
                    "Groq token or rate limit reached. Wait for the limit to reset "
                    "or choose another available model."
                )
            else:
                st.error(f"Unable to generate the post: {error_text}")


# Run the app
if __name__ == "__main__":
    main()
