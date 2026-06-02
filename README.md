# DataTalk 📊
### Chat with your CSV data in plain English — no SQL, no formulas

🔗 **[Live Demo](https://datatalk-tool.streamlit.app)** &nbsp;|&nbsp; Built with Python, Streamlit, and Gemini API

---

## What it does

Upload any CSV file and ask questions about your data in plain English. DataTalk uses Google's Gemini AI to understand your question, analyze the data, and return clear answers with auto-generated charts.

**No SQL. No formulas. No technical knowledge needed.**

---

## Examples

- *"What are the top 10 products by revenue?"* → Bar chart + answer
- *"Show me sales trends over time"* → Line chart + insight
- *"Which customer segment spends the most?"* → Pie chart + breakdown
- *"Are there any outliers in the price column?"* → Histogram + analysis

---

## Screenshots

> <img width="959" height="434" alt="Screenshot 2026-06-02 170830" src="https://github.com/user-attachments/assets/686ee5fd-a8c1-4809-a532-da5f36c848fa" />
<img width="960" height="432" alt="Screenshot 2026-06-02 173658" src="https://github.com/user-attachments/assets/cd5f5e56-f4e5-43f5-a75b-8d964725be1b" />
<img width="958" height="433" alt="Screenshot 2026-06-02 173835" src="https://github.com/user-attachments/assets/8908566b-fcc2-49b5-adec-6fbc47f7b16e" />



---

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend / UI | Streamlit |
| AI Engine | Google Gemini 2.5 Flash |
| Data Processing | Pandas |
| Visualization | Matplotlib, Seaborn |
| Deployment | Streamlit Community Cloud |

---

## Run Locally

```bash
git clone https://github.com/arshaimran/DataTalk.git
cd DataTalk
pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

Run:
```bash
streamlit run app.py
```

---

## Who is this for?

Small business owners, analysts, and anyone who has data in a spreadsheet but doesn't know how to query it. DataTalk turns your CSV into a conversation.

---

Built by [Arsha Imran](https://www.linkedin.com/in/arsha-imran-ba13341b1/) · Open to freelance projects involving data, dashboards, and AI tools.
