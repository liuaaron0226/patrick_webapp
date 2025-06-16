# patrick_method_solver.py
# Patrick Method - Minimal SOP Solver (Single and Multiple Output)
# 完整 Flask 應用（含後端邏輯與前端 HTML 與檔案上傳）

from flask import Flask, render_template_string, request
from datetime import datetime
from itertools import combinations, product
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 頁面模板（直接內嵌 HTML）
HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>Patrick Method Solver</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        textarea { width: 100%; height: 100px; margin-bottom: 10px; }
        input[type=submit] { padding: 10px 20px; }
        .result { margin-top: 20px; white-space: pre-line; background: #f0f0f0; padding: 10px; }
    </style>
</head>
<body>
    <h1>Patrick Method 最小 SOP 化簡工具</h1>
    <form method="post" enctype="multipart/form-data">
        <label>PI 輸入（多輸出以 ; 分隔）：</label><br>
        <textarea name="pi_input">A'B, AB; A'C</textarea><br>
        <label>Minterm 輸入（多輸出以 ; 分隔）：</label><br>
        <textarea name="minterms">1,3; 2,6</textarea><br>
        <label>或上傳含 PI 與 Minterms 的文字檔 (.txt)：</label><br>
        <input type="file" name="input_file"><br><br>
        <input type="submit" value="計算最小 SOP">
    </form>
    {% if result %}
    <div class="result">
        <strong>計算結果：</strong><br>{{ result }}
    </div>
    {% endif %}
    <footer><hr><small>&copy; {{ year }} Patrick Solver</small></footer>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        pi_input = request.form.get("pi_input", "")
        minterms = request.form.get("minterms", "")
        file = request.files.get("input_file")

        if file and file.filename.endswith(".txt"):
            content = file.read().decode("utf-8")
            lines = content.strip().split('\n')
            if len(lines) >= 2:
                pi_input = lines[0]
                minterms = lines[1]

        result = run_patrick_method(pi_input, minterms)
    return render_template_string(HTML_PAGE, result=result, year=datetime.now().year)


def run_patrick_method(pi_input: str, minterms: str):
    pi_groups, mt_groups = parse_input(pi_input, minterms)
    all_results = []

    for index, (pi_list, mt_list) in enumerate(zip(pi_groups, mt_groups)):
        chart = build_prime_chart(pi_list, mt_list)
        min_sop = find_min_sop(chart, pi_list)
        all_results.append(f"F{index}(Minterms: {mt_list}) → 最小 SOP: {' + '.join(min_sop) if min_sop else '找不到涵蓋所有 minterm 的組合'}")

    return "\n".join(all_results)


def parse_input(pi_input: str, minterm_input: str):
    pi_groups = [x.strip() for x in pi_input.strip().split(';')]
    mt_groups = [x.strip() for x in minterm_input.strip().split(';')]
    pi_list_grouped = [[term.strip() for term in group.split(',')] for group in pi_groups]
    mt_list_grouped = [[int(m) for m in group.split(',') if m.strip().isdigit()] for group in mt_groups]
    return pi_list_grouped, mt_list_grouped


def build_prime_chart(pi_list, mt_list):
    chart = {m: [] for m in mt_list}
    for i, pi in enumerate(pi_list):
        covered = get_covered_minterms(pi)
        for m in mt_list:
            if m in covered:
                chart[m].append(i)
    return chart


def find_min_sop(chart, pi_list):
    minterms = list(chart.keys())
    num_pis = len(pi_list)
    for r in range(1, num_pis + 1):
        for combo in combinations(range(num_pis), r):
            covered = set()
            for idx in combo:
                covered |= get_covered_minterms(pi_list[idx])
            if all(m in covered for m in minterms):
                return [pi_list[i] for i in combo]
    return []


def get_covered_minterms(pi_expr):
    vars_order = ['A', 'B', 'C', 'D']  # 支援最多四變數
    covered = set()

    for bits in product([0, 1], repeat=len(vars_order)):
        terms = [f"{v}'" if b == 0 else v for v, b in zip(vars_order, bits)]
        if match_pi(pi_expr, terms):
            idx = int(''.join(map(str, bits)), 2)
            covered.add(idx)
    return covered


def match_pi(pi_expr, term_bits):
    pi_parts = pi_expr.replace(' ', '').split('+')
    for part in pi_parts:
        if all(t in term_bits for t in split_literals(part)):
            return True
    return False


def split_literals(expr):
    i = 0
    literals = []
    while i < len(expr):
        if i + 1 < len(expr) and expr[i+1] == "'":
            literals.append(expr[i:i+2])
            i += 2
        else:
            literals.append(expr[i])
            i += 1
    return literals


if __name__ == "__main__":
    app.run(debug=True)
