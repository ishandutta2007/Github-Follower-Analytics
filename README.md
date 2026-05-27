# 📊 GitHub Follower Analytics

[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![GitHub License](https://img.shields.io/github/license/ishandutta2007/Github-Follower-Analytics)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/ishandutta2007/Github-Follower-Analytics)](https://github.com/ishandutta2007/Github-Follower-Analytics/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/ishandutta2007/Github-Follower-Analytics)](https://github.com/ishandutta2007/Github-Follower-Analytics/issues)

**GitHub Follower Analytics** is a powerful Python-based tool designed to help developers and content creators understand their audience. By leveraging the GitHub API, this tool fetches follower data, cleans up geographical information, and generates insightful visualizations of follower demographics.

---

## 🚀 Features

- **Automated Data Fetching**: Retrieves all followers for any given GitHub username, handling pagination automatically.
- **Local Caching**: Stores follower lists and profile details in `github_cache.json` to minimize API calls and drastically speed up subsequent runs.
- **Location Normalization**: Cleans and normalizes location strings (e.g., "US", "USA", "United States" -> "United States") for accurate reporting.
- **Visual Analytics**: Generates a beautiful pie chart showing the top geographical regions of your followers.
- **Rate Limit Management**: Includes built-in sleep logic to handle GitHub API rate limits gracefully.
- **Environment Variable Support**: Securely manage your GitHub Personal Access Token using `.env` files.

---

## 🛠️ Tech Stack

- **Language**: [Python 3](https://www.python.org/)
- **API Interaction**: [Requests](https://requests.readthedocs.io/)
- **Data Processing**: Python Standard Library (`collections.Counter`)
- **Visualization**: [Matplotlib](https://matplotlib.org/)
- **Environment Management**: [Python-Dotenv](https://pypi.org/project/python-dotenv/)

---

## 📥 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ishandutta2007/Github-Follower-Analytics.git
   cd Github-Follower-Analytics
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Rename `.env.example` to `.env`.
   - Add your [GitHub Personal Access Token](https://github.com/settings/tokens) to the `ADMIN_TOKEN` field (optional but recommended to avoid rate limits).

---

## 📖 Usage

1. Open `github_followers_analytics.py`.
2. Update the `GITHUB_USERNAME` variable with the target user's name:
   ```python
   GITHUB_USERNAME = 'your-username-here'
   ```
3. Run the script:
   ```bash
   python github_followers_analytics.py
   ```

---

## 📊 Sample Visualization

*(Replace this placeholder with an actual screenshot of your generated pie chart!)*

![Follower Demographics Sample](https://via.placeholder.com/800x600?text=Follower+Demographics+Pie+Chart)

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions for new features, better location normalization rules, or improved visualizations, feel free to:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📧 Contact

**Ishan Dutta** - [@ishandutta2007](https://github.com/ishandutta2007)

Project Link: [https://github.com/ishandutta2007/Github-Follower-Analytics](https://github.com/ishandutta2007/Github-Follower-Analytics)

---

**Keywords**: GitHub API, Follower Analytics, Data Visualization, Python, Matplotlib, GitHub Demographics, Social Analytics, Developer Tools.
