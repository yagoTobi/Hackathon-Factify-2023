import os
import sys
import streamlit as st

# Ensure parent directory (NewsAgent) is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from article_creator import (
    generate_final_article,
    batch_classify_articles,
    filter_and_balance_proportions,
    article_bullet_points_parallel,
    generate_article
)
from news_extractor import obtain_articles_from_query

def display_results_page():
    if 'user_query' in st.session_state:
        user_query = st.session_state.user_query

        st.subheader(f"Synthesizing balanced perspective for: *{user_query}*")

        col1, col2 = st.columns([6, 4], gap="medium")

        # Ingest and balance articles
        with st.spinner("Fetching and classifying sources for political balance..."):
            raw_articles = obtain_articles_from_query(user_query)
            if not raw_articles:
                st.error("No articles found for this topic. Please try another query.")
                return

            classified = batch_classify_articles(raw_articles)
            balanced_articles = filter_and_balance_proportions(classified, max_proportion=0.40, extremism_threshold=0.85)

        with col1:
            st.markdown("### 📰 Synthesized Story")
            with st.spinner("Generating unified Economist-style narrative..."):
                bullet_points = article_bullet_points_parallel(user_query, balanced_articles)
                final_story = generate_article(user_query, bullet_points)
                st.markdown(final_story)

        with col2:
            st.markdown("### ⚖️ Balanced Source Breakdown")
            
            # Category summary counts
            left_count = sum(1 for a in balanced_articles if a.get('category') == 'left')
            center_count = sum(1 for a in balanced_articles if a.get('category') == 'center')
            right_count = sum(1 for a in balanced_articles if a.get('category') == 'right')
            total = len(balanced_articles)

            st.info(f"**Curated Cohort**: {total} sources total  \n🔵 Left: {left_count} | ⚪ Center: {center_count} | 🔴 Right: {right_count}")

            for i, article in enumerate(balanced_articles):
                source_name = article.get('source', {}).get('name', 'Source') if isinstance(article.get('source'), dict) else str(article.get('source', 'Source'))
                category = str(article.get('category', 'center')).upper()
                slant = article.get('slant_score', 0.0)

                cat_badge = "🔵" if category == "LEFT" else ("🔴" if category == "RIGHT" else "⚪")

                with st.expander(f"{cat_badge} [{category}] {source_name}: {article.get('title', 'Article')[:55]}..."):
                    img_url = article.get('top_image') or article.get('image')
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    st.caption(f"**Slant Score**: {slant:+.2f} | **Extremism**: {article.get('extremism_score', 0.0):.2f}")
                    st.write(article.get('summary', 'No summary available.'))
                    if article.get('url'):
                        st.link_button("Read Original Source", article['url'])
