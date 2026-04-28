from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


budget = 0.0
expenses = []


def totals():
    total_spent = sum(expense["amount"] for expense in expenses)
    remaining = budget - total_spent
    return total_spent, remaining


def format_currency(value):
    return f"₹{value:,.2f}"


def render_page(message=""):
    total_spent, remaining = totals()
    warning = ""

    if remaining < 0:
        warning = "You are over budget."
    elif budget > 0 and remaining < budget * 0.2:
        warning = "Budget is running low."

    expense_rows = ""
    if expenses:
        for expense in reversed(expenses):
            expense_rows += (
                f"<tr><td>{expense['category']}</td>"
                f"<td>{format_currency(expense['amount'])}</td></tr>"
            )
    else:
        expense_rows = '<tr><td colspan="2" class="muted">No expenses yet.</td></tr>'

    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Budget Planner</title>
    <style>
        :root {{
            color-scheme: light;
            --bg: #f4f7fb;
            --card: #ffffff;
            --text: #1f2937;
            --muted: #6b7280;
            --accent: #2563eb;
            --accent-dark: #1d4ed8;
            --border: #dbe4f0;
            --shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
        }}

        * {{ box-sizing: border-box; }}

        body {{
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: linear-gradient(160deg, #eef4ff 0%, var(--bg) 55%, #f8fafc 100%);
            color: var(--text);
        }}

        .wrap {{
            max-width: 980px;
            margin: 0 auto;
            padding: 40px 20px 56px;
        }}

        .hero {{
            margin-bottom: 24px;
        }}

        h1 {{
            margin: 0 0 10px;
            font-size: clamp(2rem, 4vw, 3.5rem);
        }}

        .subtitle {{
            margin: 0;
            color: var(--muted);
            max-width: 60ch;
            line-height: 1.6;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 18px;
            margin: 24px 0;
        }}

        .card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 22px;
            box-shadow: var(--shadow);
        }}

        .stat-label {{
            margin: 0 0 10px;
            color: var(--muted);
            font-size: 0.95rem;
        }}

        .stat-value {{
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
        }}

        .warning {{
            margin-top: 10px;
            color: #b45309;
            font-weight: 600;
        }}

        .message {{
            margin: 0 0 18px;
            padding: 14px 16px;
            border-radius: 14px;
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
        }}

        .forms {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 18px;
        }}

        form {{ display: grid; gap: 12px; }}

        label {{
            display: grid;
            gap: 8px;
            font-weight: 600;
        }}

        input {{
            width: 100%;
            padding: 12px 14px;
            border: 1px solid var(--border);
            border-radius: 12px;
            font: inherit;
        }}

        button {{
            border: 0;
            border-radius: 12px;
            background: var(--accent);
            color: white;
            padding: 12px 16px;
            font: inherit;
            font-weight: 700;
            cursor: pointer;
        }}

        button:hover {{ background: var(--accent-dark); }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
        }}

        th, td {{
            text-align: left;
            padding: 12px 10px;
            border-bottom: 1px solid var(--border);
        }}

        .muted {{ color: var(--muted); }}
    </style>
</head>
<body>
    <main class="wrap">
        <section class="hero">
            <h1>Budget Planner</h1>
            <p class="subtitle">Set a monthly budget, add expenses, and see a simple live summary in your browser.</p>
        </section>

        {f'<p class="message">{message}</p>' if message else ''}

        <section class="grid">
            <div class="card">
                <p class="stat-label">Monthly Budget</p>
                <p class="stat-value">{format_currency(budget)}</p>
            </div>
            <div class="card">
                <p class="stat-label">Spent</p>
                <p class="stat-value">{format_currency(total_spent)}</p>
            </div>
            <div class="card">
                <p class="stat-label">Remaining</p>
                <p class="stat-value">{format_currency(remaining)}</p>
                {f'<p class="warning">{warning}</p>' if warning else ''}
            </div>
        </section>

        <section class="forms">
            <div class="card">
                <h2>Set Budget</h2>
                <form method="post">
                    <input type="hidden" name="action" value="set_budget">
                    <label>
                        Monthly budget
                        <input type="number" name="budget" step="0.01" min="0" placeholder="5000" required>
                    </label>
                    <button type="submit">Save budget</button>
                </form>
            </div>

            <div class="card">
                <h2>Add Expense</h2>
                <form method="post">
                    <input type="hidden" name="action" value="add_expense">
                    <label>
                        Amount
                        <input type="number" name="amount" step="0.01" min="0" placeholder="250" required>
                    </label>
                    <label>
                        Category
                        <input type="text" name="category" placeholder="Groceries" required>
                    </label>
                    <button type="submit">Add expense</button>
                </form>
            </div>
        </section>

        <section class="card" style="margin-top: 18px;">
            <h2>Expenses</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {expense_rows}
                </tbody>
            </table>
        </section>
    </main>
</body>
</html>"""


class BudgetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        message = query.get("message", [""])[0]

        html = render_page(message)
        payload = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        global budget

        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        form = parse_qs(data)
        action = form.get("action", [""])[0]

        message = ""
        if action == "set_budget":
            budget = float(form.get("budget", ["0"])[0])
            message = "Budget updated successfully."
        elif action == "add_expense":
            amount = float(form.get("amount", ["0"])[0])
            category = form.get("category", [""])[0].strip() or "Uncategorized"
            expenses.append({"amount": amount, "category": category})
            message = "Expense added successfully."
        else:
            message = "Unknown action."

        self.send_response(303)
        self.send_header("Location", f"/?message={message.replace(' ', '+')}")
        self.end_headers()


def main():
    server = HTTPServer(("127.0.0.1", 8000), BudgetHandler)
    print("Budget Planner running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()