# -*- coding: utf-8 -*-
"""Reddit自动发布 — PRAW"""
import praw, time, json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# PRAW配置 — 需要先在 https://www.reddit.com/prefs/apps 创建应用
REDDIT_CONFIG = {
    "client_id": "YOUR_CLIENT_ID",      # 去 reddit.com/prefs/apps 创建
    "client_secret": "YOUR_CLIENT_SECRET",
    "user_agent": "factory_info_bot/1.0",
    "username": "YOUR_REDDIT_USERNAME",
    "password": "YOUR_REDDIT_PASSWORD",
}

POSTS = [
  {
    "subreddit": "dropshipping",
    "title": "Found a reliable kids clothing factory in China — 60% reorder rate, A-class fabric",
    "body": "Been working with this factory in Zhongshan, China for 2+ years. Thought I'd share for anyone sourcing kids clothing.\n\nWhat they make: kids underwear, base layers, pajamas, t-shirts, baby rompers — all basic kidswear.\n\nFactory details:\n- 10 years in business, 1000sqm facility\n- ALL A-Class fabric (safe for infant skin, no formaldehyde)\n- Dropshipping supported, as low as 50pcs for custom orders\n- 48-hour dispatch after order\n- Their cross-border clients have 60%+ reorder rate\n\nPrice reference:\nKids underwear: factory price ~$0.40/pc\nKids t-shirts: ~$1.50/pc\nBaby rompers: ~$3.00/pc\n\nCompare that to what you'd pay on AliExpress or through a 1688 trader (30-50% markup).\n\nThey're on 1688 (shop2669750515e84) but you can also reach them directly. Happy to share contact via DM.\n\nNot affiliated — just a satisfied buyer sharing a good supplier."
  },
  {
    "subreddit": "AmazonFBA",
    "title": "Kids underwear on Amazon — my numbers after 2 years",
    "body": "Saw a few questions about kids clothing PL on Amazon, so sharing my experience.\n\nI sell kids underwear (private label) on Amazon US. Source from a factory in Zhongshan, China.\n\nNumbers (per unit):\n- Factory cost: ~$0.50\n- Shipping (sea freight): ~$0.07\n- FBA fees: ~$1.15\n- Amazon referral fee: ~$0.60\n- Total cost: ~$2.32\n- Selling price: $4.99\n- Net profit: ~$2.67/unit\n\nMonthly volume: 1500-2000 units\nMonthly net: $4000-5000\n\nThe key is finding a FACTORY not a trader. 1688 has tons of \"factories\" that are actually traders. Look for:\n1. Location in an industry cluster (Zhongshan/Huzhou/Qingdao for kids wear)\n2. Reorder rate above 30% (traders can't maintain this)\n3. Willing to do small batches (50-100pcs)\n\nDM me if you want the factory contact."
  },
  {
    "subreddit": "ecommerce",
    "title": "Why kids clothing basics are the most underrated ecom niche",
    "body": "Everyone's chasing trending products on TikTok. Meanwhile the boring kids basics sellers are quietly making bank.\n\nKids underwear, base layers, pajamas — these aren't exciting products. But:\n\n1. They NEVER go out of style\n2. Kids outgrow them every season = automatic reorders\n3. Return rate is tiny (kids aren't picky about fit)\n4. Lightweight = cheap shipping\n5. Competition is way lower than adult clothing\n6. Quality barrier keeps out the worst competitors (A-class fabric required for infants)\n\nThe right supplier makes all the difference. Find a factory-direct source (not a 1688 trader) and you're already ahead of 90% of sellers.\n\nBeen sourcing from a factory in Zhongshan for years. Their reorder rate is 60%+ which tells you everything about quality. DM for details."
  }
]
COMMENTS = {
  "kids clothing": "I've been sourcing kids clothing from a factory in Zhongshan, China. They do A-class fabric (safe for infant skin) and support dropshipping from 50pcs. Reorder rate 60%+ which says everything about quality. If you want their contact just DM me — not gonna spam the thread.",
  "children supplier": "Check out factories in Zhongshan (not just the famous Huzhou ones). I use a factory there for kids basics — underwear, tees, pajamas. Factory-direct pricing, no trader markup. DM for details.",
  "baby clothes": "For baby clothes specifically — make sure you're getting A-class fabric. It's the highest safety standard (no formaldehyde, no fluorescent agents). My factory in Zhongshan uses all A-class. DM if you want their info.",
  "sourcing china": "One tip for sourcing from China: go to the actual industry clusters. Zhongshan for kids wear, not random 1688 stores. Factory-direct pricing is 30-50% cheaper than traders. Happy to share my contact.",
  "1688 supplier": "Heads up — 1688 has tons of \"factories\" that are actually traders. Real factories: located in industry clusters, reorder rate >30%, can send workshop videos instantly. I use a Zhongshan factory for kids wear. DM for details.",
  "dropshipping clothes": "For clothing dropshipping — find a factory that actually WANTS small orders. My kids clothing factory does dropshipping from 50pcs. 48hr dispatch. DM for contact."
}

def post_to_reddit():
    try:
        reddit = praw.Reddit(**REDDIT_CONFIG)
        me = reddit.user.me()
        print(f"登录成功: u/{me.name}")
    except Exception as e:
        print(f"登录失败: {e}")
        print("请先在 https://www.reddit.com/prefs/apps 创建应用")
        print("类型选 'script', redirect_uri 填 http://localhost:8080")
        return

    posted = []
    for i, p in enumerate(POSTS):
        try:
            sub = reddit.subreddit(p["subreddit"])
            submission = sub.submit(p["title"], selftext=p["body"])
            print(f"[{i+1}/{len(POSTS)}] r/{p['subreddit']}: {submission.url}")
            posted.append({"subreddit": p["subreddit"], "url": submission.url, "title": p["title"]})
            time.sleep(60 * 5)  # Reddit有发帖频率限制，每5分钟发一篇
        except Exception as e:
            print(f"[{i+1}/{len(POSTS)}] 失败: {e}")
            # 如果是karma不够，先在一些小subreddit积累karma
            if "karma" in str(e).lower() or "removed" in str(e).lower():
                print("  -> 可能是karma不够或账号太新，先手动用几天再发布")
            time.sleep(60)

    # 保存发布记录
    out = Path.home() / ".auto_ops" / "publish" / "reddit_posted.json"
    out.write_text(json.dumps(posted, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已发布 {len(posted)}/{len(POSTS)} 篇")
    print(f"记录保存在: {out}")

def monitor_and_comment():
    """监控相关subreddit的新帖子，自动提醒"""
    try:
        reddit = praw.Reddit(**REDDIT_CONFIG)
    except:
        return

    subreddits = "+".join(["dropshipping", "AmazonFBA", "ecommerce", "AmazonSeller"])
    print(f"监控: r/{subreddits}")
    print("触发词:", list(COMMENTS.keys()))

    for submission in reddit.subreddit(subreddits).stream.submissions(skip_existing=True):
        title_lower = (submission.title + " " + submission.selftext).lower()
        for trigger, reply in COMMENTS.items():
            if trigger.lower() in title_lower:
                print(f"\n触发: r/{submission.subreddit} — {submission.title[:80]}")
                print(f"回复: {reply[:100]}...")
                # 注意: 自动评论风险较高，建议先打印不实际发
                # submission.reply(reply)  # 取消注释以实际发布
                break
        time.sleep(5)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_and_comment()
    else:
        post_to_reddit()
