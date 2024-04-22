# Elo Everygrant

Elo Everygrant is a Streamlit application that allows users to rate and compare grants from different funds using the Elo rating system. The application fetches grant data from a Supabase database and provides an interactive interface for users to vote on which grant they prefer between two randomly selected grants.

## Features

- Fetches grant data from a Supabase database
- Displays the total number of ratings
- Allows users to filter grants by fund using checkboxes
- Presents two randomly selected grants side by side for comparison
- Enables users to vote for their preferred grant or mark it as a draw
- Updates the Elo ratings of the grants based on user votes
- Provides a leaderboard showing the grants sorted by their Elo ratings
- Visualizes the distribution of Elo ratings using a density plot
- Visualizes the distribution of rating frequencies using a histogram

## Requirements

- Python 3.x
- Streamlit
- Pandas
- Matplotlib
- Seaborn
- Supabase Python Client

## Setup

1. Clone the repository:

```
git clone https://github.com/your-username/elo-everygrant.git
cd elo-everygrant
```

2. Install the required dependencies:

```
pip install streamlit pandas matplotlib seaborn supabase
```

3. Set up your Supabase connection:

- Create a Supabase account and project
- Obtain your Supabase project URL and API key
- Update the `conn` variable in `streamlit_app.py` with your Supabase connection details

4. Run the Streamlit app:

```
streamlit run streamlit_app.py
```

5. Access the app in your web browser at `http://localhost:8501`

## Usage

- The app displays the total number of ratings at the top.
- Use the checkboxes to filter grants by fund.
- The app presents two randomly selected grants side by side for comparison.
- Click on the "A" or "B" button to vote for your preferred grant, or click "Draw" if you consider them equally good.
- The Elo ratings of the grants are updated based on user votes.
- The leaderboard shows the grants sorted by their Elo ratings.
- The Elo distribution plot visualizes the distribution of Elo ratings.
- The rating frequency distribution plot shows the distribution of rating frequencies.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).