import html
from datetime import datetime


class ReportGenerator:
    def __init__(self, config, results, output_path):
        self.config = config
        self.results = results
        self.output_path = output_path

    def generate(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASSED")
        failed = sum(1 for r in self.results if r["status"] == "FAILED")
        errored = sum(1 for r in self.results if r["status"] == "ERROR")
        skipped = sum(1 for r in self.results if r["status"] == "SKIPPED")
        duration = sum(r["duration"] for r in self.results)
        pass_rate = (passed / total * 100) if total else 0
        pc = "#22c55e"; fc = "#ef4444"; ec = "#f59e0b"; sc = "#64748b"; ac = "#25c967"

        features = {}
        for r in self.results:
            features.setdefault(r["feature"], {"PASSED":0,"FAILED":0,"ERROR":0,"SKIPPED":0,"total":0})
            features[r["feature"]][r["status"]] += 1
            features[r["feature"]]["total"] += 1

        feat_cards = ""
        for feat, s in features.items():
            color = pc if s["FAILED"] == 0 and s["ERROR"] == 0 else fc
            feat_cards += (
                '<div class="feature-card" style="--c:' + color + '">'
                '<div class="feat-title">' + html.escape(feat.title()) + '</div>'
                '<div class="feat-stats">'
                '<span style="color:' + pc + '">PASS ' + str(s["PASSED"]) + '</span>'
                '<span style="color:' + fc + '">FAIL ' + str(s["FAILED"]) + '</span>'
                '<span style="color:' + ec + '">ERR ' + str(s["ERROR"]) + '</span>'
                '<span style="color:' + sc + '">SKIP ' + str(s["SKIPPED"]) + '</span>'
                '</div>'
                '<div class="feat-total">' + str(s["total"]) + ' test(s)</div>'
                '</div>'
            )

        def card(label, value, color):
            return ('<div class="card" style="--c:' + color + '">'
                    '<div class="card-value">' + str(value) + '</div>'
                    '<div class="card-label">' + label + '</div></div>')

        cards = (card("Total", total, "#3b82f6") + card("Passed", passed, pc)
                 + card("Failed", failed, fc) + card("Errors", errored, ec)
                 + card("Skipped", skipped, sc) + card("Duration", f"{duration:.2f}s", "#8b5cf6")
                 + card("Pass Rate", f"{pass_rate:.1f}%", ac))

        rows = "\n".join(self._render_row(i + 1, r) for i, r in enumerate(self.results))
        title = html.escape(self.config.get("report_title", "Test Report"))
        browser = html.escape(self.config.get("browser", "chrome"))
        base_url = html.escape(self.config.get("base_url", ""))
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        overall = "PASSED" if failed == 0 and errored == 0 else "FAILED"
        ov_cls = "passed" if overall == "PASSED" else "failed"

        css = (
            "*{box-sizing:border-box;margin:0;padding:0}"
            "body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;"
            "background:#0f172a;color:#e2e8f0;padding:32px;line-height:1.5}"
            ".container{max-width:1280px;margin:0 auto}"
            "header{display:flex;justify-content:space-between;align-items:center;gap:20px;"
            "flex-wrap:wrap;margin-bottom:28px;padding-bottom:24px;border-bottom:1px solid #1e293b}"
            "h1{font-size:26px;font-weight:800;color:#f8fafc}"
            ".meta{font-size:13px;color:#94a3b8}"
            ".meta span{color:#cbd5e1;font-weight:600}"
            ".pill{display:inline-block;padding:5px 14px;border-radius:999px;font-size:12px;"
            "font-weight:700;text-transform:uppercase}"
            ".pill.passed{background:rgba(34,197,94,.15);color:#22c55e}"
            ".pill.failed{background:rgba(239,68,68,.15);color:#ef4444}"
            ".cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));"
            "gap:14px;margin-bottom:20px}"
            ".card{background:#111827;border:1px solid #1e293b;border-radius:14px;padding:18px;"
            "position:relative;overflow:hidden}"
            ".card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c)}"
            ".card-value{font-size:26px;font-weight:800;color:#f8fafc}"
            ".card-label{font-size:12px;text-transform:uppercase;letter-spacing:.6px;color:#94a3b8;margin-top:4px}"
            ".features{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));"
            "gap:14px;margin-bottom:28px}"
            ".feature-card{background:#111827;border:1px solid #1e293b;border-left:4px solid var(--c);"
            "border-radius:12px;padding:16px}"
            ".feat-title{font-size:15px;font-weight:700;color:#f8fafc;margin-bottom:8px}"
            ".feat-stats{display:flex;gap:12px;font-size:13px;font-weight:600;flex-wrap:wrap}"
            ".feat-total{margin-top:8px;font-size:12px;color:#94a3b8}"
            ".filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}"
            ".filter-btn{background:#111827;color:#94a3b8;border:1px solid #1e293b;padding:8px 16px;"
            "border-radius:8px;font-size:13px;font-weight:600;cursor:pointer}"
            ".filter-btn.active{background:" + ac + ";color:#fff;border-color:" + ac + "}"
            "table{width:100%;border-collapse:collapse;background:#111827;border-radius:14px;"
            "overflow:hidden;border:1px solid #1e293b}"
            "thead{background:#0b1220}"
            "th{text-align:left;padding:14px 16px;font-size:12px;text-transform:uppercase;"
            "letter-spacing:.6px;color:#94a3b8;font-weight:700;border-bottom:1px solid #1e293b}"
            "td{padding:14px 16px;border-bottom:1px solid #1e293b;font-size:14px;vertical-align:top}"
            "tr:hover{background:#0b1220}"
            ".key{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:" + ac + ";font-weight:700}"
            ".feat-tag{display:inline-block;background:#1e293b;color:#cbd5e1;padding:2px 8px;"
            "border-radius:6px;font-size:11px;font-weight:600;text-transform:uppercase}"
            ".status{display:inline-block;padding:4px 10px;border-radius:6px;font-size:11px;"
            "font-weight:800;text-transform:uppercase}"
            ".status.PASSED{background:rgba(34,197,94,.15);color:#22c55e}"
            ".status.FAILED{background:rgba(239,68,68,.15);color:#ef4444}"
            ".status.ERROR{background:rgba(245,158,11,.15);color:#f59e0b}"
            ".status.SKIPPED{background:rgba(100,116,139,.2);color:#94a3b8}"
            ".msg{margin-top:8px;padding:10px 12px;background:#0b1220;border-left:3px solid #334155;"
            "border-radius:6px;font-family:ui-monospace,Menlo,monospace;font-size:12.5px;"
            "color:#cbd5e1;white-space:pre-wrap;word-break:break-word}"
            ".msg.error{border-color:#ef4444;color:#fecaca}"
            ".shot{display:inline-block;margin-top:8px;font-size:12px;color:" + ac + ";text-decoration:none}"
            "footer{text-align:center;margin-top:36px;color:#64748b;font-size:12px}"
        )

        filters = ('<div class="filters">'
                   '<button class="filter-btn active" data-filter="all">All (' + str(total) + ')</button>'
                   '<button class="filter-btn" data-filter="PASSED">Passed (' + str(passed) + ')</button>'
                   '<button class="filter-btn" data-filter="FAILED">Failed (' + str(failed) + ')</button>'
                   '<button class="filter-btn" data-filter="ERROR">Errors (' + str(errored) + ')</button>'
                   '<button class="filter-btn" data-filter="SKIPPED">Skipped (' + str(skipped) + ')</button>'
                   '</div>')

        js = (
            "var btns=document.querySelectorAll('.filter-btn');"
            "btns.forEach(function(b){b.addEventListener('click',function(){"
            "btns.forEach(function(x){x.classList.remove('active')});"
            "b.classList.add('active');var f=b.dataset.filter;"
            "document.querySelectorAll('#results-table tbody tr').forEach(function(tr){"
            "tr.style.display=(f==='all'||tr.dataset.status===f)?'':'none';});});});"
        )

        page = (
            '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
            '<title>' + title + '</title><style>' + css + '</style></head><body>'
            '<div class="container">'
            '<header><div>'
            '<h1>' + title + '</h1>'
            '<div class="meta">Generated <span>' + now + '</span> &middot; Browser: <span>' + browser + '</span></div>'
            '<div class="meta">Target: <span>' + base_url + '</span></div>'
            '</div><div class="pill ' + ov_cls + '">' + overall + '</div></header>'
            '<section class="cards">' + cards + '</section>'
            '<section class="features">' + feat_cards + '</section>'
            + filters +
            '<table id="results-table"><thead><tr>'
            '<th style="width:50px">#</th>'
            '<th style="width:130px">Key</th>'
            '<th style="width:100px">Feature</th>'
            '<th>Test</th>'
            '<th style="width:120px">Category</th>'
            '<th style="width:110px">Status</th>'
            '<th style="width:90px">Time</th>'
            '</tr></thead><tbody>'
            + (rows if rows else '<tr><td colspan="7" style="text-align:center;padding:40px;color:#64748b">No tests</td></tr>') +
            '</tbody></table>'
            '<footer>Generated by Selenium Test Suite Runner &middot; ' + now + '</footer>'
            '</div><script>' + js + '</script></body></html>'
        )
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(page)

    def _render_row(self, idx, r):
        status = r["status"]
        msg = ""
        if r["message"]:
            cls = "msg error" if status in ("FAILED", "ERROR") else "msg"
            msg = '<div class="' + cls + '">' + html.escape(r["message"]) + '</div>'
        shot = ""
        if r.get("screenshot"):
            shot = '<a class="shot" href="' + html.escape(r["screenshot"]) + '" target="_blank">View screenshot</a>'
        return (
            '<tr data-status="' + status + '" data-feature="' + html.escape(r["feature"]) + '">'
            '<td>' + str(idx) + '</td>'
            '<td><span class="key">' + html.escape(r["key"]) + '</span></td>'
            '<td><span class="feat-tag">' + html.escape(r["feature"]) + '</span></td>'
            '<td><div style="font-weight:600;color:#f1f5f9">' + html.escape(r["name"]) + '</div>'
            '<div style="font-size:12.5px;color:#94a3b8;margin-top:2px">' + html.escape(r["description"]) + '</div>'
            + msg + shot + '</td>'
            '<td style="color:#cbd5e1">' + html.escape(r["category"]) + '</td>'
            '<td><span class="status ' + status + '">' + status + '</span></td>'
            '<td style="color:#94a3b8;font-family:ui-monospace,Menlo,monospace">' + str(r["duration"]) + 's</td>'
            '</tr>'
        )
