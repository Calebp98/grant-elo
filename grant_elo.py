import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns


conn = sqlite3.connect("example.db", check_same_thread=False)


def get_data():
    df = pd.read_sql_query("SELECT * FROM mytable", conn)
    return df


def update_data(df):
    df.to_sql("mytable", conn, if_exists="replace", index=False)


st.title("ELO Everygrant")
st.subheader("Which grant is better?")

if "df" not in st.session_state:
    st.session_state.df = get_data()

df = st.session_state.df

if "random_rows" not in st.session_state:
    st.session_state.random_rows = df.sample(n=2)


def update_elo(winner):

    row1 = st.session_state.random_rows.iloc[0]
    row2 = st.session_state.random_rows.iloc[1]

    R_A = row1["elo"]
    R_B = row2["elo"]

    E_A = 1 / (1 + 10 ** ((R_B - R_A) / 400))
    E_B = 1 / (1 + 10 ** ((R_A - R_B) / 400))

    A_index = st.session_state.random_rows.index[0]
    B_index = st.session_state.random_rows.index[1]

    if winner == "A":
        df.at[A_index, "elo"] += 32 * (1 - E_A)
        df.at[B_index, "elo"] += 32 * (0 - E_B)
    if winner == "B":
        df.at[B_index, "elo"] += 32 * (1 - E_B)
        df.at[A_index, "elo"] += 32 * (0 - E_A)
    if winner == "Draw":
        df.at[B_index, "elo"] += 32 * (0.5 - E_B)
        df.at[A_index, "elo"] += 32 * (0.5 - E_A)
    df.at[A_index, "count"] += 1
    df.at[B_index, "count"] += 1
    st.session_state.random_rows = df.sample(n=2)
    st.session_state.df = df
    update_data(df)

def skip():
    st.session_state.random_rows = df.sample(n=2)



col1, col2, col3 = st.columns(3)

row1 = st.session_state.random_rows.iloc[0]
row2 = st.session_state.random_rows.iloc[1]

with col1:
    button1_text = f"{row1.fund} :{row1.description}:"
    st.button(button1_text, on_click=update_elo, args=("A",))
    st.write(f"ELO: {row1['elo']:.0f}")

with col2:
    st.button("Draw", on_click=update_elo, args=("Draw",))
    st.button("Skip", on_click=skip)

with col3:
    button2_text = f"{row2.fund} :{row2.description}:"
    st.button(button2_text, on_click=update_elo, args=("B",))
    st.write(f"ELO: {row2['elo']:.0f}")

with st.expander("Leaderboard"):
    st.table(
        df.drop(columns=["grantee", "round", "highlighted", "id"])
        .sort_values(by="elo", ascending=False)
        .reset_index(drop=True)
        .rename(columns={"elo": "ELO", "fund": "Fund", "description": "Description"})
    )

def plot_elo_distribution():
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.kdeplot(data=df, x='elo', fill=True, ax=ax)
    ax.set_xlabel('ELO Rating')
    ax.set_ylabel('Density')
    ax.set_title('ELO Distribution')
    st.pyplot(fig)
st.header('ELO Distribution')
plot_elo_distribution()

total_ratings = df['count'].sum()
st.subheader(f"Total Ratings: {total_ratings}")