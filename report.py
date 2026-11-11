#!/usr/bin/env python3
"""Build report.html from jobs.json + companies.json + status.json.
Update status:  python3 status.py <url-or-company> applied|rejected|interview|offer|saved|ignored
"""
import json, html, pathlib
D = pathlib.Path(__file__).parent
e = html.escape
jobs = json.loads((D/"jobs.json").read_text("utf8")) if (D/"jobs.json").exists() else {"jobs": [], "crawled": "never"}
companies = json.loads((D/"companies.json").read_text("utf8"))
sf = D/"status.json"; status = json.loads(sf.read_text("utf8")) if sf.exists() else {}
STATES = ["new","saved","applied","interview","offer","rejected","ignored"]
def sel(key):
    cur = status.get(key, "new")
    return f'<select data-key="{e(key)}" class="st st-{cur}">' + "".join(f'<option{" selected" if s==cur else ""}>{s}</option>' for s in STATES) + "</select>"
rows = lambda js: "".join(f'<tr data-src="{e(j["source"])}"><td>{sel(j["url"])}</td><td><a href="{e(j["url"])}" target="_blank">{e(j["title"])}</a></td><td>{e(j["company"])}</td><td>{e(j.get("target") or "")}</td><td>{e(j["source"])}</td><td>{e(j.get("posted",""))}</td><td>{e(j.get("salary",""))}</td></tr>' for j in js)
jl = jobs["jobs"]; tgt = sorted([j for j in jl if j.get("target")], key=lambda j:(j["group"], j["company"])); oth = [j for j in jl if not j.get("target")]
head = "<tr><th>Status</th><th>Title</th><th>Company</th><th>Target</th><th>Source</th><th>Posted</th><th>Salary</th></tr>"
comp = "".join(f'<tr><td>{sel("company:"+c["name"])}</td><td>{e(c["name"])}</td><td>{e(c["group"])}</td><td>{"<a target=_blank href=%s>careers</a>"%e(c["careers"]) if c["careers"] else ""}</td><td><a target=_blank href="https://jobinja.ir/companies?q={e(c["aliases"][0])}">jobinja</a> · <a target=_blank href="https://www.google.com/search?q={e(c["name"])}+career+tehran">google</a> · <a target=_blank href="https://www.linkedin.com/jobs/search/?keywords={e(c["name"])}&location=Tehran">linkedin</a></td></tr>' for c in companies)
out = f"""<!doctype html><meta charset=utf-8><title>Job tracker</title><style>
body{{font:14px system-ui;margin:24px;background:#fafafa;color:#222}}table{{border-collapse:collapse;width:100%;background:#fff;margin-bottom:32px}}
td,th{{border:1px solid #ddd;padding:6px 8px;text-align:left}}th{{background:#eee}}a{{color:#0645ad}}
.st-applied{{background:#cfe8ff}}.st-rejected{{background:#ffd3d3}}.st-interview{{background:#fff2b3}}.st-offer{{background:#c8f2c8}}.st-ignored{{color:#999}}
#sum span{{margin-right:14px}}</style>
<h1>Job tracker — Tehran software</h1><p>Crawled: {e(jobs["crawled"])} · {len(jl)} jobs · {len(tgt)} at target companies</p><p id=sum></p>
<input id=f placeholder="filter..." style="width:300px;padding:6px"> <label><input type=checkbox id=hide> hide rejected/ignored</label>
<h2>Jobs at target companies</h2><table>{head}{rows(tgt)}</table>
<h2>Target companies (follow up / careers pages)</h2><table><tr><th>Status</th><th>Company</th><th>Group</th><th>Careers</th><th>Search</th></tr>{comp}</table>
<h2>Other Tehran software jobs</h2><table>{head}{rows(oth)}</table>
<script>
const KEY='jobstatus',base={json.dumps(status)};let st=Object.assign({{}},base,JSON.parse(localStorage.getItem(KEY)||'{{}}'));
document.querySelectorAll('select.st').forEach(s=>{{const v=st[s.dataset.key];if(v){{s.value=v;s.className='st st-'+v}}
 s.onchange=()=>{{st[s.dataset.key]=s.value;s.className='st st-'+s.value;localStorage.setItem(KEY,JSON.stringify(st));sum()}}}});
function sum(){{const c={{}};document.querySelectorAll('select.st').forEach(s=>c[s.value]=(c[s.value]||0)+1);
 document.getElementById('sum').innerHTML=Object.entries(c).map(([k,v])=>`<span>${{k}}: <b>${{v}}</b></span>`).join('');apply()}}
function apply(){{const q=f.value.toLowerCase(),h=hide.checked;document.querySelectorAll('tr').forEach(r=>{{const s=r.querySelector('select');if(!s)return;
 r.style.display=(r.textContent.toLowerCase().includes(q)||(r.querySelector('select')&&false))&&!(h&&['rejected','ignored'].includes(s.value))?'':'none'}})}}
f.oninput=apply;hide.onchange=apply;sum();
</script>"""
(D/"report.html").write_text(out, "utf8"); print("wrote", D/"report.html")
