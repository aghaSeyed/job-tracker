#!/usr/bin/env python3
"""Crawl job boards (Tehran, software) and flag jobs from target companies."""
import json, re, time, html, urllib.parse, urllib.request, pathlib, datetime
D = pathlib.Path(__file__).parent
UA = {"User-Agent": "Mozilla/5.0"}
KEYWORDS = ["php","laravel","backend","بک‌اند","python","golang","node.js","java","software engineer","برنامه نویس","developer","devops","full stack","symfony","react","mobile","android","data engineer"]
PAGES = 3

def get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf8", "replace")

def jobinja(kw):
    out = []
    for p in range(1, PAGES + 1):
        q = urllib.parse.urlencode({"filters[keywords][0]": kw, "filters[locations][0]": "تهران", "sort_by": "published_at_desc", "page": p})
        try: h = get("https://jobinja.ir/jobs?" + q)
        except Exception as e: print("jobinja fail", kw, p, e); break
        items = re.findall(r'<h2 class="o-listView__itemTitle.*?</ul>', h, re.S)
        if not items: break
        for it in items:
            m = re.search(r'href="([^"]+)"[^>]*>\s*(.*?)\s*</a>', it, re.S)
            c = re.search(r'c-icon--construction"></i>\s*<span>\s*(.*?)\s*</span>', it, re.S)
            ago = re.search(r'\((.*?)\)', it, re.S)
            if not m: continue
            url = html.unescape(m.group(1)).split("?")[0]
            out.append({"source": "jobinja", "title": html.unescape(re.sub(r"<.*?>", "", m.group(2))).strip(),
                        "company": html.unescape(c.group(1)).strip() if c else "?", "url": url,
                        "posted": " ".join(ago.group(1).split()) if ago else ""})
        time.sleep(1)
    return out

def jobvision(kw):
    out = []
    for p in range(1, PAGES + 1):
        body = json.dumps({"keyword": kw, "sortBy": 0, "searchId": None, "locationWrapper": "all-cities-of-tehran",
                           "pageSize": 30, "requestedPage": p}).encode()
        try:
            j = json.loads(get("https://candidateapi.jobvision.ir/api/v1/JobPost/List", body,
                               {"Content-Type": "application/json", "Origin": "https://jobvision.ir",
                                "ngsw-bypass": "true", "web-app-version": "19.0.184"}))
        except Exception as e:
            print("jobvision fail", kw, p, e); break
        posts = (j.get("data") or {}).get("jobPosts") or []
        if not posts: break
        for x in posts:
            co = x.get("company") or {}; sal = x.get("salary") or {}
            out.append({"source": "jobvision", "title": x.get("title", ""), "company": co.get("nameFa") or co.get("nameEn") or "?",
                        "url": f"https://jobvision.ir/jobs/{x['id']}",
                        "posted": ((x.get("activationTime") or {}).get("date") or "")[:10],
                        "salary": (f"{sal['min']}-{sal['max']}M" if sal.get("max") else f"{sal['min']}M") if sal.get("min") else ""})
        time.sleep(1)
    return out

def main():
    companies = json.loads((D / "companies.json").read_text("utf8"))
    jobs = {}
    for kw in KEYWORDS:
        print("keyword", kw)
        for src in (jobinja, jobvision):
            for j in src(kw): jobs.setdefault(j["url"], j)
    def match(job):
        t = job["company"].lower().replace("\u200c"," ")
        for c in companies:
            if any(a.lower().replace("\u200c"," ") in t for a in c["aliases"]): return c
    for j in jobs.values():
        c = match(j); j["target"] = c["name"] if c else None; j["group"] = c["group"] if c else None
    (D / "jobs.json").write_text(json.dumps({"crawled": datetime.datetime.now().isoformat(timespec="minutes"), "jobs": list(jobs.values())}, ensure_ascii=False, indent=1), "utf8")
    print(len(jobs), "jobs,", sum(1 for j in jobs.values() if j["target"]), "from target companies")

if __name__ == "__main__": main()
