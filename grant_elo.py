# streamlit_app.py
import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize connection.
conn = st.connection("supabase", type=SupabaseConnection)


def get_data():
    result = conn.query("*", table="grants_elo", ttl="0").execute()
    df = pd.DataFrame(result.data)
    return df


def update_data(df):
    conn.table("grants_elo").upsert(df.to_dict(orient="records")).execute()


st.title("Elo Everygrant")

if "df" not in st.session_state:
    st.session_state.df = get_data()

df = st.session_state.df

show_elo = st.checkbox("Show Current Elo", value=False)

# Add checkboxes for each fund
funds = df["fund"].unique()
selected_funds = []

fund_cols = st.columns(3)
for i, fund in enumerate(funds):
    with fund_cols[i % 3]:
        selected = st.checkbox(fund, value=True)
        if selected:
            selected_funds.append(fund)
st.subheader("Which grant is better?")

# Filter the DataFrame based on selected funds
filtered_df = df[df["fund"].isin(selected_funds)]


if "random_rows" not in st.session_state:
    st.session_state.random_rows = filtered_df.sample(n=2)


def update_elo(winner):
    grant_a = st.session_state.random_rows.iloc[0]
    grant_b = st.session_state.random_rows.iloc[1]
    R_A = grant_a["elo"]
    R_B = grant_b["elo"]
    E_A = 1 / (1 + 10 ** ((R_B - R_A) / 400))
    E_B = 1 / (1 + 10 ** ((R_A - R_B) / 400))
    A_index = st.session_state.random_rows.index[0]
    B_index = st.session_state.random_rows.index[1]
    if winner == "A":
        filtered_df.at[A_index, "elo"] += 32 * (1 - E_A)
        filtered_df.at[B_index, "elo"] += 32 * (0 - E_B)
    if winner == "B":
        filtered_df.at[B_index, "elo"] += 32 * (1 - E_B)
        filtered_df.at[A_index, "elo"] += 32 * (0 - E_A)
    if winner == "Draw":
        filtered_df.at[B_index, "elo"] += 32 * (0.5 - E_B)
        filtered_df.at[A_index, "elo"] += 32 * (0.5 - E_A)
    filtered_df.at[A_index, "count"] += 1
    filtered_df.at[B_index, "count"] += 1
    st.session_state.random_rows = filtered_df.sample(n=2)
    st.session_state.df = filtered_df
    update_data(filtered_df)


def skip():
    st.session_state.random_rows = filtered_df.sample(n=2)


left_half, right_half = st.columns(2)
col1, col2, col3 = st.columns(3)
grant_a = st.session_state.random_rows.iloc[0]
grant_b = st.session_state.random_rows.iloc[1]

with left_half:
    a = st.container(border=True)
    a.subheader("A")
    a.write(grant_a.fund)
    a.write(grant_a.description)
    a.write(f"${grant_a.amount:,}")
    if show_elo:
        a.write(f"ELO: {grant_a['elo']:.0f}")


with right_half:
    b = st.container(border=True)
    b.subheader("B")
    b.write(grant_b.fund)
    b.write(grant_b.description)
    b.write(f"${grant_b.amount:,}")
    if show_elo:
        b.write(f"ELO: {grant_b['elo']:.0f}")

with col1:
    st.button("A", on_click=update_elo, args=("A",), use_container_width=True)

with col2:
    st.button("Draw", on_click=update_elo, args=("Draw",), use_container_width=True)
    st.button(
        "Skip (No ELO Change)", on_click=skip, use_container_width=True, type="primary"
    )

with col3:
    st.button(f"B", on_click=update_elo, args=("B",), use_container_width=True)

with st.expander("Leaderboard"):
    st.table(
        filtered_df.drop(columns=["grantee", "round", "highlighted", "id"])
        .sort_values(by="elo", ascending=False)
        .reset_index(drop=True)
        .rename(columns={"elo": "ELO", "fund": "Fund", "description": "Description"})
    )


def plot_elo_distribution():
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.kdeplot(data=filtered_df, x="elo", fill=True, ax=ax)
    ax.set_xlabel("ELO Rating")
    ax.set_ylabel("Density")
    ax.set_title("ELO Distribution")
    st.pyplot(fig)


plot_elo_distribution()


def plot_rating_frequency_distribution():
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(data=filtered_df, x="count", bins=20, ax=ax)
    ax.set_xlabel("Number of Ratings")
    ax.set_ylabel("Frequency")
    ax.set_title("Rating Frequency Distribution")
    st.pyplot(fig)


plot_rating_frequency_distribution()

total_ratings = filtered_df["count"].sum()
st.subheader(f"Total Ratings: {total_ratings}")
