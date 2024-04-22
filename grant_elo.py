# streamlit_app.py
import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
import matplotlib.pyplot as plt
import seaborn as sns


# Initialize connection.
conn = st.connection("supabase", type=SupabaseConnection)

# table = "test"
table = "grants_elo"


def get_data():
    result = conn.query("*", table=table, ttl="0").execute()
    df = pd.DataFrame(result.data)
    return df


def update_data(df):
    conn.table(table).upsert(df.to_dict(orient="records")).execute()


st.title("Elo Everygrant")

if "df" not in st.session_state:
    st.session_state.df = get_data()

total_ratings = st.session_state.df["count"].sum()
st.subheader(f"Total Ratings: {total_ratings}")

df = st.session_state.df
original_df = df.copy()  # Store the original DataFrame

show_elo = st.toggle("Show Current Elo", value=False)

# Add checkboxes for each fund
funds = original_df["fund"].unique()
selected_funds = []

fund_cols = st.columns(3)
for i, fund in enumerate(funds):
    with fund_cols[i % 3]:
        selected = st.checkbox(fund, value=True)
        if selected:
            selected_funds.append(fund)
st.subheader("Which grant is better?")

# Filter the DataFrame based on selected funds
filtered_df = original_df[original_df["fund"].isin(selected_funds)]


if "random_rows" not in st.session_state:
    st.session_state.random_rows = filtered_df.sample(n=2)


def update_elo(winner):
    try:
        grant_a = st.session_state.random_rows.iloc[0]
        grant_b = st.session_state.random_rows.iloc[1]
        R_A = grant_a["elo"]
        R_B = grant_b["elo"]
        E_A = 1 / (1 + 10 ** ((R_B - R_A) / 400))
        E_B = 1 / (1 + 10 ** ((R_A - R_B) / 400))
        A_index = st.session_state.random_rows.index[0]
        B_index = st.session_state.random_rows.index[1]
        if winner == "A":
            st.session_state.df.at[A_index, "elo"] += 32 * (1 - E_A)
            st.session_state.df.at[B_index, "elo"] += 32 * (0 - E_B)
        if winner == "B":
            st.session_state.df.at[B_index, "elo"] += 32 * (1 - E_B)
            st.session_state.df.at[A_index, "elo"] += 32 * (0 - E_A)
        if winner == "Draw":
            st.session_state.df.at[B_index, "elo"] += 32 * (0.5 - E_B)
            st.session_state.df.at[A_index, "elo"] += 32 * (0.5 - E_A)
        st.session_state.df.at[A_index, "count"] += 1
        st.session_state.df.at[B_index, "count"] += 1
        st.session_state.random_rows = filtered_df.sample(n=2)
        update_data(st.session_state.df)
    except Exception as err:
        import pickle

        with open("./problem.pkl", "w") as f:
            pickle.dump(dict(A_index=A_index, filtered_df=filtered_df, err=err), f)


def sample_nearby(df):
    p1 = df.loc[df["count"].idxmin()]
    df_exclude_p1 = df[df.index != p1.name].copy()  # Create a copy of the slice
    df_exclude_p1.loc[:, "weights"] = 1 / (abs(p1.elo - df_exclude_p1["elo"] + 1e-6))
    st.dataframe(df_exclude_p1)
    sampled_row = df_exclude_p1.sample(n=1, weights="weights")
    return pd.concat([p1.to_frame().T, sampled_row], axis=0)


def skip():
    st.session_state.random_rows = filtered_df.sample(n=2)


left_half, right_half = st.columns(2)
col1, col2, col3 = st.columns(3)
grant_a = st.session_state.random_rows.iloc[0]
grant_b = st.session_state.random_rows.iloc[1]


def dispay_grant(grant, label):
    a = st.container(border=True)
    a.subheader(label)
    a.write(grant.fund)
    a.write(grant.grantee)
    a.write(grant.description)
    a.write(grant["round"])
    a.write(f"${grant.amount:,}")
    if show_elo:
        a.write(f"ELO: {grant['elo']:.0f}")
    a.button(
        label, on_click=update_elo, args=(label,), use_container_width=True, key=label
    )


with left_half:
    dispay_grant(grant_a, "A")


with right_half:
    dispay_grant(grant_b, "B")


st.button("Draw", on_click=update_elo, args=("Draw",), use_container_width=True)
st.button(
    "Skip (No ELO Change)", on_click=skip, use_container_width=True, type="primary"
)


with st.expander("Leaderboard"):
    st.table(
        st.session_state.df.drop(columns=["grantee", "round", "highlighted", "id"])
        .sort_values(by="elo", ascending=False)
        .reset_index(drop=True)
        .rename(columns={"elo": "ELO", "fund": "Fund", "description": "Description"})
    )


def plot_elo_distribution():
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.kdeplot(data=st.session_state.df, x="elo", fill=True, ax=ax)
    ax.set_xlabel("ELO Rating")
    ax.set_ylabel("Density")
    ax.set_title("ELO Distribution")
    st.pyplot(fig)


plot_elo_distribution()


def plot_rating_frequency_distribution():
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(data=st.session_state.df, x="count", bins=20, ax=ax)
    ax.set_xlabel("Number of Ratings")
    ax.set_ylabel("Frequency")
    ax.set_title("Rating Frequency Distribution")
    st.pyplot(fig)


plot_rating_frequency_distribution()
