"""Smoke-test admin CMS CRUD against local Flask API."""

from __future__ import annotations



import json

import os

import sys

import time

import urllib.error

import urllib.request



BASE = os.environ.get("API_BASE", "http://127.0.0.1:3050")

EMAIL = os.environ.get("ADMIN_EMAIL", "admin@databiqs.com")

PASSWORD = os.environ.get("ADMIN_PASSWORD", "DatabiqsAdmin2026!")





def req(method: str, path: str, body=None, token: str | None = None):

    headers = {"Content-Type": "application/json"}

    if token:

        headers["Authorization"] = f"Bearer {token}"

    data = json.dumps(body).encode("utf-8") if body is not None else None

    request = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)

    try:

        with urllib.request.urlopen(request, timeout=15) as resp:

            raw = resp.read().decode("utf-8")

            return resp.status, json.loads(raw) if raw else {}

    except urllib.error.HTTPError as exc:

        raw = exc.read().decode("utf-8")

        try:

            payload = json.loads(raw)

        except json.JSONDecodeError:

            payload = {"error": raw}

        return exc.code, payload





def fail(msg: str):

    print(f"FAIL: {msg}")

    sys.exit(1)





def ok(msg: str):

    print(f"OK: {msg}")





def put_content(token: str, content: dict) -> dict:

    code, resp = req("PUT", "/api/admin/content", content, token=token)

    if code != 200:

        fail(f"put content {code} {resp}")

    return content





def get_content(token: str) -> dict:

    code, content = req("GET", "/api/admin/content", token=token)

    if code != 200 or not isinstance(content, dict):

        fail(f"get content {code}")

    return content





def main():

    code, _ = req("GET", "/api/health")

    if code != 200:

        fail(f"health {code}")

    ok("health")



    code, login = req("POST", "/api/admin/login", {"email": EMAIL, "password": PASSWORD})

    if code != 200 or not login.get("token"):

        fail(f"login {code} {login}")

    token = login["token"]

    ok("login")



    content = get_content(token)

    ok("get full content")



    marker = f"crud-{int(time.time())}"

    content["_adminCrudMarker"] = marker

    put_content(token, content)

    reread = get_content(token)

    if reread.get("_adminCrudMarker") != marker:

        fail("put round-trip marker missing")

    ok("put round-trip")



    ts = int(time.time())



    # services add/delete

    services = reread.get("services") or {}

    slist = list(services.get("list") or [])

    details = dict(services.get("details") or {})

    test_slug = f"crud-svc-{ts}"

    slist.append(

        {

            "id": ts,

            "slug": test_slug,

            "title": "CRUD Test Service",

            "shortDescription": "temp",

            "features": [],

            "themeClass": "core-card--chatbot",

        }

    )

    details[test_slug] = {"hero": {"title": "CRUD Test Service"}}

    reread["services"] = {**services, "list": slist, "details": details}

    put_content(token, reread)

    after_add = get_content(token)

    if not any(s.get("slug") == test_slug for s in after_add.get("services", {}).get("list", [])):

        fail("service not added")

    ok("services add")



    after_add["services"]["list"] = [

        s for s in after_add["services"]["list"] if s.get("slug") != test_slug

    ]

    after_add["services"]["details"] = {

        k: v for k, v in after_add["services"]["details"].items() if k != test_slug

    }

    put_content(token, after_add)

    after_del = get_content(token)

    if any(s.get("slug") == test_slug for s in after_del.get("services", {}).get("list", [])):

        fail("service not deleted")

    ok("services delete")



    # blogs add/update/delete

    blogs = after_del.get("blogs") or {}

    posts = list(blogs.get("posts") or [])

    test_post_id = ts + 1

    posts.append(

        {

            "id": test_post_id,

            "tag": "Test",

            "topicKey": (blogs.get("categories") or [{"key": "ai-automation"}])[0]["key"],

            "category": "Test",

            "title": "CRUD Blog Post",

            "date": "May 22, 2026",

            "readTime": "1 Min Read",

            "image": "",

            "excerpt": "temp",

            "content": "test",

        }

    )

    after_del["blogs"] = {**blogs, "posts": posts}

    put_content(token, after_del)

    b1 = get_content(token)

    found = next((p for p in b1.get("blogs", {}).get("posts", []) if p.get("id") == test_post_id), None)

    if not found:

        fail("blog not added")

    ok("blogs add")



    b1["blogs"]["posts"] = [

        {**p, "title": "CRUD Blog Updated"} if p.get("id") == test_post_id else p

        for p in b1["blogs"]["posts"]

    ]

    put_content(token, b1)

    b2 = get_content(token)

    updated = next((p for p in b2.get("blogs", {}).get("posts", []) if p.get("id") == test_post_id), None)

    if not updated or updated.get("title") != "CRUD Blog Updated":

        fail("blog not updated")

    ok("blogs update")



    b2["blogs"]["posts"] = [p for p in b2["blogs"]["posts"] if p.get("id") != test_post_id]

    put_content(token, b2)

    b3 = get_content(token)

    if any(p.get("id") == test_post_id for p in b3.get("blogs", {}).get("posts", [])):

        fail("blog not deleted")

    ok("blogs delete")



    # case studies add/delete

    cs = b3.get("caseStudies") or {}

    cards = list(cs.get("cards") or [])

    details_cs = dict(cs.get("details") or {})

    test_case_id = f"crud-case-{ts}"

    cards.append(

        {

            "id": test_case_id,

            "categoryKey": (cs.get("categories") or [{"key": "ai-automation"}])[0]["key"],

            "category": "Test",

            "filterKey": "Test",

            "company": "CRUD Co",

            "title": "CRUD Case",

            "description": "temp",

            "metrics": [],

            "href": f"/case-studies/{test_case_id}",

        }

    )

    details_cs[test_case_id] = {"hero": {"title": "CRUD Case"}}

    b3["caseStudies"] = {**cs, "cards": cards, "details": details_cs}

    put_content(token, b3)

    c1 = get_content(token)

    if not any(c.get("id") == test_case_id for c in c1.get("caseStudies", {}).get("cards", [])):

        fail("case study not added")

    ok("case studies add")



    c1["caseStudies"]["cards"] = [c for c in c1["caseStudies"]["cards"] if c.get("id") != test_case_id]

    c1["caseStudies"]["details"] = {

        k: v for k, v in c1["caseStudies"]["details"].items() if k != test_case_id

    }

    put_content(token, c1)

    c2 = get_content(token)

    if any(c.get("id") == test_case_id for c in c2.get("caseStudies", {}).get("cards", [])):

        fail("case study not deleted")

    ok("case studies delete")



    # testimonials add/update/delete

    t_items = list(c2.get("testimonials", {}).get("items") or [])

    test_tid = ts + 99

    t_items.append({"id": test_tid, "quote": '"CRUD testimonial."', "audioUrl": ""})

    c2["testimonials"] = {"items": t_items}

    put_content(token, c2)

    t1 = get_content(token)

    t_found = next((t for t in t1.get("testimonials", {}).get("items", []) if t.get("id") == test_tid), None)

    if not t_found:

        fail("testimonial not added")

    ok("testimonials add")



    t1["testimonials"]["items"] = [

        {**t, "quote": '"CRUD testimonial updated."'} if t.get("id") == test_tid else t

        for t in t1["testimonials"]["items"]

    ]

    put_content(token, t1)

    t2 = get_content(token)

    t_upd = next((t for t in t2.get("testimonials", {}).get("items", []) if t.get("id") == test_tid), None)

    if not t_upd or "updated" not in t_upd.get("quote", ""):

        fail("testimonial not updated")

    ok("testimonials update")



    t2["testimonials"]["items"] = [t for t in t2["testimonials"]["items"] if t.get("id") != test_tid]

    put_content(token, t2)

    t3 = get_content(token)

    if any(t.get("id") == test_tid for t in t3.get("testimonials", {}).get("items", [])):

        fail("testimonial not deleted")

    ok("testimonials delete")

    saved_testimonials = t3.get("testimonials")

    # patch testimonials section
    code, patch = req(
        "PATCH",
        "/api/admin/content/testimonials",
        {"items": [{"id": 1, "quote": "patch ok", "audioUrl": ""}]},
        token=token,
    )
    if code != 200:
        fail(f"patch testimonials {code} {patch}")
    ok("patch testimonials section")
    if saved_testimonials is not None:
        restore = get_content(token)
        restore["testimonials"] = saved_testimonials
        put_content(token, restore)
        t3 = restore

    # team add/delete
    team = list(t3.get("team") or [])

    team.append({"name": "CRUD Member", "role": "Test", "image": "", "featured": False})

    t3["team"] = team

    put_content(token, t3)

    t4 = get_content(token)

    if not any(m.get("name") == "CRUD Member" for m in t4.get("team", [])):

        fail("team add")

    t4["team"] = [m for m in t4.get("team", []) if m.get("name") != "CRUD Member"]

    put_content(token, t4)

    ok("team add/delete")



    # patch media

    saved_media = dict(t3.get("media") or {})
    code, patch = req(
        "PATCH",
        "/api/admin/content/media",
        {
            **saved_media,
            "blogHeroVideo": "https://res.cloudinary.com/deelyxcjk/video/upload/f_mp4,q_auto:good,w_1920,c_limit/v1779295410/8084751-uhd_3840_2160_25fps_gloxzu.mp4",
        },
        token=token,
    )

    if code != 200:

        fail(f"patch media {code} {patch}")

    ok("patch media section")



    # unknown section

    code, bad = req("PATCH", "/api/admin/content/unknown", {}, token=token)

    if code != 400:

        fail(f"expected 400 for unknown section, got {code}")

    ok("reject unknown section")



    # cleanup marker (reload after patch may have changed store)

    final = get_content(token)

    final.pop("_adminCrudMarker", None)

    put_content(token, final)



    print("\nAll admin CRUD smoke tests passed.")





if __name__ == "__main__":

    main()

