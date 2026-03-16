#!/usr/bin/env python3
from __future__ import annotations

import html
import os
import re
import shutil
from copy import deepcopy
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "site" / "caamp.jp"
OUTPUT_ROOT = ROOT / "docs"
X_EMBED_SOURCE = ROOT / "X_EMBED.txt"
ASSETS_DIR = OUTPUT_ROOT / "assets"
MEDIA_DIR = ASSETS_DIR / "media"
DOCS_DIR = ASSETS_DIR / "docs"


ROUTES = ["", "about", "technology", "related-work", "news", "publications", "contact"]
SITE_SETTINGS = {
    "brand_alt": {
        "jp": "一般社団法人 次世代移動支援技術開発コンソーシアム",
        "en": "Consortium for Advanced Assistive Mobility Platform",
    },
    "menu_label": {
        "jp": "Menu",
        "en": "Menu",
    },
    "follow_href": "https://twitter.com/AISuitcaseCAAMP",
    "follow_label": {
        "jp": "Follow Us on X",
        "en": "Follow Us on X",
    },
    "follow_aria_label": {
        "jp": "AIスーツケース・コンソーシアムのXをフォロー",
        "en": "Follow Consortium for Advanced Assistive Mobility Platform on X",
    },
    "home_logos": [
        {
            "name": {
                "jp": "アルプスアルパイン株式会社",
                "en": "Alps Alpine Co., Ltd.",
            },
            "asset": "media/logo-alps.png",
            "href": "https://www.alpsalpine.com/j/",
        },
        {
            "name": {
                "jp": "日本アイ・ビー・エム株式会社",
                "en": "IBM Japan, Ltd.",
            },
            "asset": "media/logo-ibm.png",
            "href": "https://www.ibm.com/jp-ja",
        },
        {
            "name": {
                "jp": "オムロン株式会社",
                "en": "OMRON Corporation",
            },
            "asset": "media/logo-omron.png",
            "href": "https://www.omron.co.jp/",
        },
        {
            "name": {
                "jp": "清水建設株式会社",
                "en": "Shimizu Corporation",
            },
            "asset": "media/logo-shimizu.png",
            "href": "https://www.shimz.co.jp/",
        },
    ],
    "about_mission_title": {
        "jp": "Our Mission",
        "en": "Our Mission",
    },
    "news_titles": {
        "jp": {
            "page_title": "News",
            "press_releases": "Press Releases",
            "media": "Media",
        },
        "en": {
            "page_title": "News",
            "press_releases": "Press Releases",
            "media": "Media",
        },
    },
    "publications_titles": {
        "jp": {
            "page_title": "Publications",
        },
        "en": {
            "page_title": "Publications",
        },
    },
    "related_titles": {
        "jp": {
            "page_title": "Related Work",
            "open_source": "Open Source",
            "resources": "Outside Resources",
        },
        "en": {
            "page_title": "Related Work",
            "open_source": "Open Source",
            "resources": "Outside Resources",
        },
    },
    "contact_labels": {
        "jp": {
            "address": "Address",
            "email": "Email",
        },
        "en": {
            "address": "Address",
            "email": "Email",
        },
    },
}
NAV_LABELS = {
    "jp": {
        "about": "About",
        "technology": "Technology",
        "related-work": "Related Work",
        "news": "News",
        "publications": "Publications",
        "contact": "Contact",
    },
    "en": {
        "about": "About",
        "technology": "Technology",
        "related-work": "Related Work",
        "news": "News",
        "publications": "Publications",
        "contact": "Contact",
    },
}

PAGE_META = {
    "jp": {
        "": {
            "title": "AI Suitcase | CAAMP",
            "description": "AIスーツケース・コンソーシアムの活動、技術、研究成果をまとめた静的サイト。",
        },
        "about": {
            "title": "About | AI Suitcase",
            "description": "AIスーツケース・コンソーシアムのミッション、理事会、支援メンバー。",
        },
        "technology": {
            "title": "Technology | AI Suitcase",
            "description": "AIスーツケースを支える要素技術とシステム構成。",
        },
        "related-work": {
            "title": "Related Work | AI Suitcase",
            "description": "AIスーツケースに関連するオープンソースと外部リソース。",
        },
        "news": {
            "title": "News | AI Suitcase",
            "description": "コンソーシアムのプレスリリースとメディア掲載。",
        },
        "publications": {
            "title": "Publications | AI Suitcase",
            "description": "AIスーツケース関連の論文・研究発表一覧。",
        },
        "contact": {
            "title": "Contact | AI Suitcase",
            "description": "AIスーツケース・コンソーシアムへの問い合わせ先。",
        },
    },
    "en": {
        "": {
            "title": "AI Suitcase | CAAMP",
            "description": "Static site for the AI Suitcase consortium, its technology, and research output.",
        },
        "about": {
            "title": "About | AI Suitcase",
            "description": "Mission, board members, and collaborators behind CAAMP.",
        },
        "technology": {
            "title": "Technology | AI Suitcase",
            "description": "Technology demos, component areas, and embedded videos for AI Suitcase.",
        },
        "related-work": {
            "title": "Related Work | AI Suitcase",
            "description": "Open-source projects and external resources related to AI Suitcase.",
        },
        "news": {
            "title": "News | AI Suitcase",
            "description": "Press releases and media coverage for AI Suitcase.",
        },
        "publications": {
            "title": "Publications | AI Suitcase",
            "description": "Research publications connected to AI Suitcase and related work.",
        },
        "contact": {
            "title": "Contact | AI Suitcase",
            "description": "Contact information for the Consortium for Advanced Assistive Mobility Platform.",
        },
    },
}

CURATED_ASSETS = {
    "media/logo-header.png": RAW_ROOT / "wp-content/uploads/2023/03/ロゴ_white-1.png",
    "media/logo-header-en.png": RAW_ROOT / "en/wp-content/uploads/2023/03/ロゴ_white.png",
    "media/logo-footer.png": RAW_ROOT / "wp-content/uploads/2023/03/ロゴ-e1603751120183-1.png",
    "media/logo-footer-en.png": RAW_ROOT / "en/wp-content/uploads/2023/03/ロゴ-e1603751120183.png",
    "media/logo-alps.png": RAW_ROOT / "wp-content/uploads/2023/03/alpsalpine_logo.png",
    "media/logo-ibm.png": RAW_ROOT / "wp-content/uploads/2023/03/ibm_logo.png",
    "media/logo-omron.png": RAW_ROOT / "wp-content/uploads/2023/03/omron_logo.png",
    "media/logo-shimizu.png": RAW_ROOT / "wp-content/uploads/2023/03/shimizu_logo.png",
    "media/hero-home.jpg": RAW_ROOT / "wp-content/uploads/2023/03/IMG_9023-1-e1602126938507-2048x1982.jpg",
    "media/home-intro.jpg": RAW_ROOT / "wp-content/uploads/2023/03/IMG_8925BA-L2-scaled.jpg",
    "media/home-contact.jpg": RAW_ROOT / "wp-content/uploads/2023/03/IMG_5649-1536x1152.jpg",
    "media/about-mission-en.jpg": RAW_ROOT / "en/wp-content/uploads/2023/03/IMG_5584-1024x768.jpg",
    "media/hero-community.jpg": RAW_ROOT / "wp-content/uploads/2023/03/IMG_5649-1536x1152.jpg",
    "media/member-asakawa.jpg": RAW_ROOT / "wp-content/uploads/2023/03/y_4581-e1603413731726.jpg",
    "media/member-asakawa-en.jpg": RAW_ROOT / "en/wp-content/uploads/elementor/thumbs/y_4581-e1603413731726-q34p97r59s9g6wdd0uju015yowa0gzc8d8pnwmzy8c.jpg",
    "media/member-fukuda.jpg": RAW_ROOT / "wp-content/uploads/2023/03/IBM福田-scaled.jpg",
    "media/member-kakegawa.jpg": RAW_ROOT / "wp-content/uploads/2023/03/掛川-秀史-写真.jpg",
    "media/member-suwa.jpg": RAW_ROOT / "wp-content/uploads/2023/03/諏訪理事.jpg",
    "media/member-ito.jpeg": RAW_ROOT / "wp-content/uploads/2023/03/ALAP_伊藤直樹-写真-scaled.jpeg",
    "media/member-sato.png": RAW_ROOT / "wp-content/uploads/2023/10/佐藤さん280.png",
    "media/member-sato-en.jpg": RAW_ROOT / "en/wp-content/uploads/elementor/thumbs/daisuke-sato-cmu-qe94e2f86on4w00pkm68p3u5kn5n74fhbs4eaeakuk.jpg",
    "media/about-primary-alps-jp.png": RAW_ROOT / "wp-content/uploads/2023/03/alpsalpine-1.png",
    "media/about-primary-ibm-jp.png": RAW_ROOT / "wp-content/uploads/2023/03/IBM-Logo.png",
    "media/about-primary-omron-jp.png": RAW_ROOT / "wp-content/uploads/2023/03/blue_logo-1-1.png",
    "media/about-primary-shimizu-jp.png": RAW_ROOT / "wp-content/uploads/2023/03/shimz_logo.png",
    "media/about-primary-alps-en.png": RAW_ROOT / "wp-content/uploads/2023/03/alpsalpine_logo.png",
    "media/about-primary-ibm-en.png": RAW_ROOT / "wp-content/uploads/2023/03/IBM-Logo.png",
    "media/about-primary-omron-en.png": RAW_ROOT / "wp-content/uploads/2023/03/omron_logo.png",
    "media/about-primary-shimizu-en.png": RAW_ROOT / "wp-content/uploads/2023/03/shimizu_logo.png",
    "media/about-tech-dialogue.png": RAW_ROOT / "wp-content/uploads/2023/03/ibm.png",
    "media/about-tech-sponsor-alps-jp.png": RAW_ROOT / "wp-content/uploads/2023/03/alpsalpine-1.png",
    "media/about-tech-sponsor-omron-jp.png": RAW_ROOT / "wp-content/uploads/2023/03/omron-1.png",
    "media/about-tech-sponsor-ibm-jp.png": RAW_ROOT / "wp-content/uploads/2023/03/IBM-Logo.png",
    "media/about-tech-sponsor-shimizu-jp.png": RAW_ROOT / "wp-content/uploads/2023/03/shimz_logo.png",
    "media/about-tech-sponsor-alps-en.png": RAW_ROOT / "wp-content/uploads/2023/03/alpsalpine_logo.png",
    "media/about-tech-sponsor-omron-en.png": RAW_ROOT / "wp-content/uploads/2023/03/omron_logo.png",
    "media/about-tech-sponsor-ibm-en.png": RAW_ROOT / "wp-content/uploads/2023/03/ibm_logo.png",
    "media/about-tech-sponsor-shimizu-en.png": RAW_ROOT / "wp-content/uploads/2023/03/shimizu_logo.png",
    "media/about-tech-sponsor-cmu.png": RAW_ROOT / "wp-content/uploads/2023/03/cmu-1.png",
    "media/tech-tactile.png": RAW_ROOT / "wp-content/uploads/2023/03/touch.png",
    "media/tech-vision.png": RAW_ROOT / "wp-content/uploads/2023/03/face.png",
    "media/tech-dialogue.png": RAW_ROOT / "wp-content/uploads/2023/03/ibm.png",
    "media/tech-system.png": RAW_ROOT / "wp-content/uploads/2023/03/image5-1.png",
    "media/tech-navigation.png": RAW_ROOT / "wp-content/uploads/2023/03/robot_navi.png",
    "media/tech-mobility.png": RAW_ROOT / "wp-content/uploads/2023/03/mobilty-1.png",
    "media/tech-accessibility.png": RAW_ROOT / "wp-content/uploads/2023/03/eye.png",
    "media/ai-suitcase.mp4": RAW_ROOT / "wp-content/uploads/2023/03/ai_mono_480p_hd.mp4",
    "docs/article-of-incorporation.pdf": RAW_ROOT / "wp-content/uploads/2023/03/一般社団法人次世代移動支援技術開発コンソーシアム-定款_20191217.pdf",
}

HOME_CONTENT = {
    "jp": {
        "eyebrow": "Go Beyond Our Dreams",
        "title": "AI Suitcase",
        "lede": "視覚障がい者の独立した移動や街歩きを支援する先進的なモビリティ・ソリューション。",
        "hero_image_alt": "夕日をバックに日本科学未来館で撮影したAIスーツケース",
        "technology_label": "Our Technology",
        "intro_eyebrow": "Making Impossible Possible",
        "intro_title": "Consortium for Advanced Assistive Mobility Platform (CAAMP)",
        "intro_body": "一般社団法人 次世代移動支援技術開発コンソーシアム",
        "intro_cta": "About Us",
        "intro_image": "media/home-intro.jpg",
        "intro_image_alt": "AIスーツケースで日本科学未来館を移動する特別会員・浅川智恵子",
        "news_eyebrow": "We Update regularly!",
        "news_title": "What's New",
        "news_cta": "More News",
        "membership_eyebrow": "Meet Our Team",
        "membership_title": "Our Membership",
        "membership_body": "研究開発、そして社会実装実現のため専門分野に秀でた企業、大学と共にグローバルにプロジェクトを進めています。",
        "contact_eyebrow": "Contact",
        "contact_title": "Any Questions?",
        "contact_body": "AI スーツケース・コンソーシアムでは、実験に参加していただけるユーザーや活用可能なデータを提供していただける企業からの連絡をお待ちしています。その他ご質問、取材等もお気軽にお問い合わせください。",
        "contact_cta": "Contact Us",
        "contact_image": "media/home-contact.jpg",
        "contact_image_alt": "実験中のメンバーの様子",
    },
    "en": {
        "eyebrow": "Go Beyond Our Dreams",
        "title": "AI Suitcase",
        "lede": "Epoch-making mobility solution to help visually-impaired users independently walk around and self-navigate.",
        "hero_image_alt": "AI Suitcase photographed at Miraikan against the sunset",
        "technology_label": "Our Technology",
        "intro_eyebrow": "Making Impossible Possible",
        "intro_title": "Consortium for Advanced Assistive Mobility Platform (CAAMP)",
        "intro_body": "一般社団法人 次世代移動支援技術開発コンソーシアム",
        "intro_cta": "About Us",
        "intro_image": "media/home-intro.jpg",
        "intro_image_alt": "Distinguished Member Chieko Asakawa moving through Miraikan with the AI Suitcase",
        "news_eyebrow": "We Update regularly!",
        "news_title": "What's New",
        "news_cta": "More News",
        "membership_eyebrow": "Meet Our Team",
        "membership_title": "Our Membership",
        "membership_body": "Epoch-making mobility solution to help visually-impaired users independently walk around and self-navigate.",
        "contact_eyebrow": "Contact",
        "contact_title": "Any Questions?",
        "contact_body": "We welcome feedback and questions from users, corporate communities and academia. Please feel free to drop in and let us know.",
        "contact_cta": "Contact Us",
        "contact_image": "media/home-contact.jpg",
        "contact_image_alt": "Consortium members during an experiment",
    },
}

ABOUT_PAGE_DATA = {
    "jp": {
        "page_title": "About",
        "mission": {
            "body": "一般社団法人 次世代移動支援技術開発コンソーシアム (通称 : AIスーツケース・コンソーシアム) は、視覚障がい者の実社会におけるアクセシビリティ (\"リアルワールド・アクセシビリティ\") と QOL 向上に資する、AI を活用した先進的移動支援技術の研究開発を行っています。",
            "media": {
                "type": "video",
            },
        },
        "team": {
            "title": "Our team",
            "board": {
                "title": "理事会",
                "members": [
                    {
                        "name": "福田 剛志",
                        "role": "代表理事",
                        "org": "日本アイ・ビー・エム株式会社",
                        "image": "media/member-fukuda.jpg",
                    },
                    {
                        "name": "掛川 秀史",
                        "role": "理事",
                        "org": "清水建設株式会社",
                        "image": "media/member-kakegawa.jpg",
                    },
                    {
                        "name": "諏訪 正樹",
                        "role": "理事",
                        "org": "オムロン株式会社",
                        "image": "media/member-suwa.jpg",
                    },
                    {
                        "name": "伊藤 直樹",
                        "role": "監事",
                        "org": "アルプスアルパイン株式会社",
                        "image": "media/member-ito.jpeg",
                    },
                ],
            },
            "primary": {
                "title": "正会員",
                "members": [
                    {
                        "name": "アルプスアルパイン株式会社",
                        "image": "media/about-primary-alps-jp.png",
                        "href": "https://www.alpsalpine.com/j/",
                    },
                    {
                        "name": "日本アイ・ビー・エム株式会社",
                        "image": "media/about-primary-ibm-jp.png",
                        "href": "https://www.ibm.com/jp-ja",
                    },
                    {
                        "name": "オムロン株式会社",
                        "image": "media/about-primary-omron-jp.png",
                        "href": "https://www.omron.co.jp/",
                    },
                    {
                        "name": "清水建設株式会社",
                        "image": "media/about-primary-shimizu-jp.png",
                        "href": "https://www.shimz.co.jp/",
                    },
                ],
            },
            "associate": {
                "title": "準会員",
            },
            "distinguished": {
                "title": "特別会員",
                "members": [
                    {
                        "name": "浅川 智恵子",
                        "role": "特別会員",
                        "org": "カーネギーメロン大学 / IBM Corporation",
                        "image": "media/member-asakawa.jpg",
                        "href": "https://researcher.watson.ibm.com/researcher/view.php?person=us-chiekoa",
                    },
                    {
                        "name": "佐藤 大介",
                        "role": "特別会員",
                        "org": "カーネギーメロン大学",
                        "image": "media/member-sato.png",
                        "href": "https://www.ri.cmu.edu/ri-people/daisuke-sato/",
                    },
                ],
            },
            "supporting": {
                "title": "賛助会員",
                "members": [
                    {"name": "慶應義塾大学", "href": None},
                    {"name": "早稲田大学 先進理工学研究科 物理学及応用物理学専攻 森島繁生研究室", "href": None},
                    {"name": "日本盲導犬協会", "href": "https://www.moudouken.net/"},
                    {"name": "エース株式会社", "href": "https://www.ace.jp/"},
                    {"name": "日本科学未来館", "href": "https://www.miraikan.jst.go.jp/"},
                    {"name": "産業技術総合研究所 人間社会拡張研究部門", "href": "https://unit.aist.go.jp/rihsa/"},
                    {"name": "HEROZ株式会社", "href": "https://heroz.co.jp/"},
                ],
            },
        },
        "document": {
            "title": "定款",
            "label": "定款を開く",
        },
        "technology": {
            "eyebrow": "each member has a role",
            "title": "Our technology",
            "label": "Learn More",
            "cards": [
                {
                    "title": "触覚インターフェイス",
                    "image": "media/tech-tactile.png",
                    "sponsor_image": "media/about-tech-sponsor-alps-jp.png",
                    "sponsor_name": "アルプスアルパイン株式会社",
                    "sponsor_href": "https://www.alpsalpine.com/j/",
                },
                {
                    "title": "画像認識",
                    "image": "media/tech-vision.png",
                    "sponsor_image": "media/about-tech-sponsor-omron-jp.png",
                    "sponsor_name": "オムロン株式会社",
                    "sponsor_href": "https://www.omron.co.jp/",
                },
                {
                    "title": "対話AI・行動/環境認識・クラウド技術",
                    "image": "media/about-tech-dialogue.png",
                    "sponsor_image": "media/about-tech-sponsor-ibm-jp.png",
                    "sponsor_name": "日本アイ・ビー・エム株式会社",
                    "sponsor_href": "https://www.ibm.com/jp-ja/about",
                },
                {
                    "title": "ロボット技術・測位/ナビゲーション",
                    "image": "media/tech-navigation.png",
                    "sponsor_image": "media/about-tech-sponsor-shimizu-jp.png",
                    "sponsor_name": "清水建設株式会社",
                    "sponsor_href": "https://www.shimz.co.jp/",
                },
                {
                    "title": "モビリティサービス",
                    "image": "media/tech-mobility.png",
                    "sponsor_image": None,
                    "sponsor_name": None,
                    "sponsor_href": None,
                },
                {
                    "title": "視覚障がい者支援技術",
                    "image": "media/tech-accessibility.png",
                    "sponsor_image": "media/about-tech-sponsor-cmu.png",
                    "sponsor_name": "カーネギーメロン大学",
                    "sponsor_href": "https://www.cmu.edu/",
                },
            ],
        },
        "contact_cta": {
            "title": "Any Questions?",
            "body": "AIスーツケース・コンソーシアムでは、実験に参加していただけるユーザーや活用可能なデータを提供していただける企業からの連絡をお待ちしています。その他ご質問、取材等もお気軽にお問い合わせください。",
            "label": "Contact Us",
            "image_alt": "実験中のメンバーの様子",
            "show_image": True,
        },
    },
    "en": {
        "page_title": "About",
        "mission": {
            "body": "Consortium for Advanced Assistive Mobility Platform (CAAMP, a.k.a. the AI Suitcase Consortium) is working to improve accessibility and quality of life for blind and visually impaired people through real-world deployment of assistive AI technologies.",
            "media": {
                "type": "video",
                "image": "media/about-mission-en.jpg",
                "image_alt": "Field test scene with AI Suitcase",
            },
        },
        "team": {
            "title": "Our Team",
            "board": {
                "title": "Board of Directors",
                "members": [
                    {
                        "name": "Takeshi Fukuda",
                        "role": "Representative Director",
                        "org": "IBM Japan, Ltd.",
                        "image": "media/member-fukuda.jpg",
                    },
                    {
                        "name": "Shuji Kakegawa",
                        "role": "Director",
                        "org": "Shimizu Corporation",
                        "image": "media/member-kakegawa.jpg",
                    },
                    {
                        "name": "Masaki Suwa",
                        "role": "Director",
                        "org": "OMRON Corporation",
                        "image": "media/member-suwa.jpg",
                    },
                    {
                        "name": "Naoki Ito",
                        "role": "Auditor",
                        "org": "Alps Alpine Co., Ltd.",
                        "image": "media/member-ito.jpeg",
                    },
                ],
            },
            "primary": {
                "title": "Primary Members",
                "members": [
                    {
                        "name": "Alps Alpine Co., Ltd.",
                        "image": "media/about-primary-alps-en.png",
                        "href": "https://www.alpsalpine.com/j/",
                    },
                    {
                        "name": "IBM Japan, Ltd.",
                        "image": "media/about-primary-ibm-en.png",
                        "href": "https://www.ibm.com/jp-ja",
                    },
                    {
                        "name": "OMRON Corporation",
                        "image": "media/about-primary-omron-en.png",
                        "href": "https://www.omron.co.jp/",
                    },
                    {
                        "name": "Shimizu Corporation",
                        "image": "media/about-primary-shimizu-en.png",
                        "href": "https://www.shimz.co.jp/",
                    },
                ],
            },
            "associate": {
                "title": "Associate Members",
            },
            "distinguished": {
                "title": "Distinguished Members",
                "members": [
                    {
                        "name": "Chieko Asakawa",
                        "role": "Distinguished Member",
                        "org": "Carnegie Mellon University / IBM Corporation",
                        "image": "media/member-asakawa-en.jpg",
                        "href": "https://researcher.watson.ibm.com/researcher/view.php?person=us-chiekoa",
                    },
                    {
                        "name": "Daisuke Sato",
                        "role": "Distinguished Member",
                        "org": "Carnegie Mellon University",
                        "image": "media/member-sato-en.jpg",
                        "href": "https://www.ri.cmu.edu/ri-people/daisuke-sato/",
                    },
                ],
            },
            "supporting": {
                "title": "Supporting Members",
                "members": [
                    {"name": "Keio University", "href": None},
                    {"name": "Waseda University Morishima Lab.", "href": None},
                    {"name": "Japan Guide Dog Association", "href": "https://www.moudouken.net/"},
                    {"name": "ACE Co., Ltd.", "href": "https://www.ace.jp/"},
                    {
                        "name": "The National Museum of Emerging Science and Innovation",
                        "href": "https://www.miraikan.jst.go.jp/",
                    },
                    {"name": "Santen Pharmaceutical Co., Ltd.", "href": "https://www.santen.co.jp/ja/"},
                    {
                        "name": "Research Institute on Human and Societal Augmentation",
                        "href": "https://unit.aist.go.jp/rihsa/en/",
                    },
                ],
            },
        },
        "document": {
            "title": "Article of Incorporation",
            "label": "Open",
        },
        "technology": {
            "eyebrow": "each member has a role",
            "title": "Our Technology",
            "label": "Learn More",
            "cards": [
                {
                    "title": "Tactile Interface",
                    "image": "media/tech-tactile.png",
                    "sponsor_image": "media/about-tech-sponsor-alps-en.png",
                    "sponsor_name": "Alps Alpine Co., Ltd.",
                    "sponsor_href": "https://www.alpsalpine.com/j/",
                },
                {
                    "title": "Visual Recognition",
                    "image": "media/tech-vision.png",
                    "sponsor_image": "media/about-tech-sponsor-omron-en.png",
                    "sponsor_name": "OMRON Corporation",
                    "sponsor_href": "https://www.omron.co.jp/",
                },
                {
                    "title": "Interactive AI, Behavior and Environment Recognition, Cloud",
                    "image": "media/about-tech-dialogue.png",
                    "sponsor_image": "media/about-tech-sponsor-ibm-en.png",
                    "sponsor_name": "IBM Japan, Ltd.",
                    "sponsor_href": "https://www.ibm.com/jp-ja/about",
                },
                {
                    "title": "Robotics, Localization and Navigation",
                    "image": "media/tech-navigation.png",
                    "sponsor_image": "media/about-tech-sponsor-shimizu-en.png",
                    "sponsor_name": "Shimizu Corporation",
                    "sponsor_href": "https://www.shimz.co.jp/",
                },
                {
                    "title": "Mobility Service",
                    "image": "media/tech-mobility.png",
                    "sponsor_image": None,
                    "sponsor_name": None,
                    "sponsor_href": None,
                },
                {
                    "title": "Assistive Technologies for Visual Impairment",
                    "image": "media/tech-accessibility.png",
                    "sponsor_image": "media/about-tech-sponsor-cmu.png",
                    "sponsor_name": "Carnegie Mellon University",
                    "sponsor_href": "https://www.cmu.edu/",
                },
            ],
        },
        "contact_cta": {
            "title": "Any Questions?",
            "body": "We welcome feedback and questions from users, corporate communities and academia. Please feel free to drop in and let us know.",
            "label": "Contact Us",
            "image_alt": "Consortium members during an experiment",
            "show_image": True,
        },
    },
}

TECH_CONTENT = {
    "jp": {
        "page_title": "Technology",
        "main_video_id": "af9440zWCGo",
        "main_video_title": "Technology Demo@The National Museum of Emerging Science and Innovation (Miraikan) 2023 Winter",
        "system_title": "Our System",
        "system_image": "media/tech-system.png",
        "system_image_alt": "AIスーツケースのシステム構成図",
        "system_labels": [
            "距離センサー",
            "PC",
            "電源",
            "駆動部",
            "カメラ",
            "操作スイッチ",
            "外部通信ユニット",
            "加速度センサー",
            "触覚デバイス",
        ],
        "technology_title_html": "Our<br>Technology",
        "technology_cards": [
            ("触覚インターフェイス", "media/tech-tactile.png", "media/about-tech-sponsor-alps-jp.png", "アルプスアルパイン株式会社", "https://www.alpsalpine.com/j/"),
            ("画像認識", "media/tech-vision.png", "media/about-tech-sponsor-omron-jp.png", "オムロン株式会社", "https://www.omron.co.jp/"),
            ("対話AI・行動/環境認識・クラウド技術", "media/tech-dialogue.png", "media/about-tech-sponsor-ibm-jp.png", "日本アイ・ビー・エム株式会社", "https://www.ibm.com/jp-ja/about"),
            ("ロボット技術・測位/ナビゲーション", "media/tech-navigation.png", "media/about-tech-sponsor-shimizu-jp.png", "清水建設株式会社", "https://www.shimz.co.jp/"),
            ("モビリティサービス", "media/tech-mobility.png", None, None, None),
            ("視覚障がい者支援技術", "media/tech-accessibility.png", "media/about-tech-sponsor-cmu.png", "カーネギーメロン大学", "https://www.cmu.edu/"),
        ],
        "other_videos_title": "Other Videos",
        "other_videos": [
            ("7sMxygc9zfk", "AI Suitcase related video 1"),
            ("KU1x1Vv0Fgg", "AI Suitcase related video 2"),
        ],
        "contact_title": "Any Questions?",
        "contact_body": "AIスーツケース・コンソーシアムでは実験に参加していただけるユーザーや活用可能なデータを提供していただける企業からの連絡をお待ちしています。その他ご質問、取材等もお気軽にお問い合わせください。",
        "contact_label": "Contact Us",
        "contact_image": "media/home-contact.jpg",
        "contact_image_alt": "実験中のメンバーの様子",
    },
    "en": {
        "page_title": "Technology",
        "main_video_id": "af9440zWCGo",
        "main_video_title": "Technology Demo@The National Museum of Emerging Science and Innovation (Miraikan) 2023 Winter",
        "system_title": "Our System",
        "system_image": "media/tech-system.png",
        "system_image_alt": "System diagram of the AI Suitcase",
        "system_labels": [
            "Distance Sensor",
            "PC",
            "Power Supply",
            "Drive Unit",
            "Camera",
            "Control Switch",
            "External Communication Unit",
            "Accelerometer",
            "Tactile Device",
        ],
        "technology_title_html": "Our Technology",
        "technology_cards": [
            ("Tactile Interface", "media/tech-tactile.png", "media/logo-alps.png", "Alps Alpine Co., Ltd.", "https://www.alpsalpine.com/j/"),
            ("Visual Recognition", "media/tech-vision.png", "media/logo-omron.png", "OMRON Corporation", "https://www.omron.co.jp/"),
            ("Interactive AI, Behavior and Environment Recognition, Cloud", "media/tech-dialogue.png", "media/logo-ibm.png", "IBM Japan, Ltd.", "https://www.ibm.com/jp-ja/about"),
            ("Robotics, Localization and Navigation", "media/tech-navigation.png", "media/logo-shimizu.png", "Shimizu Corporation", "https://www.shimz.co.jp/"),
            ("Mobility Service", "media/tech-mobility.png", None, None, None),
            ("Assistive Technologies for Visual Impairment", "media/tech-accessibility.png", "media/about-tech-sponsor-cmu.png", "Carnegie Mellon University", "https://www.cmu.edu/"),
        ],
        "other_videos_title": "Other Videos",
        "other_videos": [
            ("7sMxygc9zfk", "AI Suitcase related video 1"),
            ("KU1x1Vv0Fgg", "AI Suitcase related video 2"),
        ],
        "contact_title": "Any Questions?",
        "contact_body": "We welcome feedback and questions from users, corporate communities and academia. Please feel free to drop in and let us know.",
        "contact_label": "Contact Us",
        "contact_image": None,
        "contact_image_alt": "",
    },
}

RELATED_CONTENT = {
    "jp": {
        "intro": "AIスーツケースの前身となる、Carnegie Mellon University Cognitive Assistant Labでの研究他、関連する活動を紹介します。",
        "open_source": [
            ("Cabot", "AIスーツケースのソフトウェアとハードウェアの設計データ。", "https://github.com/CMU-cabot"),
            ("Hulop", "AIスーツケースでも利用しているナビゲーションアプリNavCogのオープンソース。", "https://github.com/hulop/"),
        ],
        "resources": [
            ("Cognitive Assistance Lab", "研究の源流となる Carnegie Mellon University の研究室。", "https://www.cs.cmu.edu/~NavCog/"),
            ("NavCog", "屋内ナビゲーション研究から広がったアプリケーション。", "https://www.facebook.com/navcog/"),
            ("インクルーシブ・ナビ", "東京の商業施設で使われた視覚障がい者向けナビゲーションアプリ。", "https://www.shimz.co.jp/company/about/news-release/2019/2019020.html"),
            ("BBeep", "周囲歩行者との衝突回避を支援する音響システム。", "https://wotipati.github.io/projects/BBeep/BBeep.html"),
        ],
    },
    "en": {
        "intro": "Introducing related works including those of Carnegie Mellon University Cognitive Assistance Lab created prior to AI Suitcase.",
        "open_source": [
            ("CaBot", "Technical specs and design data for AI Suitcase software and hardware.", "https://github.com/CMU-cabot"),
            ("HULOP", "An open-source navigation stack including NavCog, also used in AI Suitcase.", "https://github.com/hulop/"),
        ],
        "resources": [
            ("Miraikan Accessibility Lab.", "Accessibility-focused research and public engagement connected to the consortium.", "https://www.miraikan.jst.go.jp/en/research/AccessibilityLab/"),
            ("Cognitive Assistance Lab.", "The CMU research lab behind much of the earlier navigation work.", "https://www.cs.cmu.edu/~NavCog/"),
            ("NavCog", "The broader indoor navigation effort connected to this work.", "https://www.facebook.com/navcog/"),
            ("IncNavi", "A Japanese navigation app previously used in a Tokyo shopping mall.", "https://www.shimz.co.jp/company/about/news-release/2019/2019020.html"),
            ("BBeep", "A sonic collision-avoidance system for blind travelers and nearby pedestrians.", "https://wotipati.github.io/projects/BBeep/BBeep.html"),
        ],
    },
}

NEWS_PAGE_CONTENT = {
    "jp": {
        "twitter_title": "SNS",
        "twitter_body": "最新情報は公式 X アカウントでも案内しています。",
        "twitter_label": "Follow Us on X",
    },
    "en": {
        "twitter_title": "SNS",
        "twitter_body": "Latest updates are also posted on the official X account.",
        "twitter_label": "Follow Us on X",
    },
}

CONTACT_CONTENT = {
    "jp": {
        "page_title": "Contact",
        "title": "Consortium for Advanced Assistive Mobility Platform",
        "address": "19-21 Nihonbashi Hakozaki-cho, C/O IBM Japan, Ltd., Chuo-ku, Tokyo 103-8510 Japan",
        "email": "pmo.caamp.japan@gmail.com",
        "notice": "静的サイトではフォームを外し、メールでの問い合わせに一本化しています。",
        "map_embed": "https://maps.google.com/maps?q=19-21%20Nihonbashi%20Hakozaki-cho%20C%2FO%20IBM%20Japan%2C%20Ltd.&t=m&z=15&output=embed&iwloc=near",
        "layout": "split",
        "button_label": "Email Us",
    },
    "en": {
        "page_title": "Contact",
        "title": "Consortium for Advanced Assistive Mobility Platform",
        "address": "19-21 Nihonbashi Hakozaki-cho, C/O IBM Japan, Ltd., Chuo-ku, Tokyo 103-8510 Japan",
        "email": "pmo.caamp.japan@gmail.com",
        "notice": "The original form has been replaced with a direct email contact so the page stays fully static.",
        "map_embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3240.937293936208!2d139.78263913088836!3d35.678545974390985!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x601889439bb79c1b%3A0x12dc0bcd65c5bec0!2sIBM%20Japan!5e0!3m2!1sen!2sca!4v1677812981221!5m2!1sen!2sca",
        "layout": "split",
        "button_label": "Email Us",
    },
}

FOOTER_CONTENT = {
    "jp": {
        "logo": "media/logo-footer.png",
        "copyright": "© 2020 All Rights Reserved.",
        "top_action": "language",
        "bottom_action": "follow",
    },
    "en": {
        "logo": "media/logo-footer-en.png",
        "copyright": "© 2023 All Rights Reserved.",
        "top_action": "follow",
        "bottom_action": "language",
    },
}


def normalize_space(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split())


def route_dir(locale: str, route: str) -> str:
    if locale == "jp":
        return route
    return "en" if not route else f"en/{route}"


def route_href(current_dir: str, target_dir: str) -> str:
    start = current_dir or "."
    target = target_dir or "."
    rel = os.path.relpath(target, start)
    return "./" if rel == "." else rel.rstrip("/") + "/"


def file_href(current_dir: str, target_file: str) -> str:
    return os.path.relpath(target_file, current_dir or ".")


def asset_href(current_dir: str, relative_path: str) -> str:
    return file_href(current_dir, f"assets/{relative_path}")


def page_output_path(locale: str, route: str) -> Path:
    target_dir = OUTPUT_ROOT / route_dir(locale, route)
    return target_dir / "index.html" if route_dir(locale, route) else OUTPUT_ROOT / "index.html"


def make_dir_for_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def external_link(href: str, label: str, class_name: str = "", extra: str = "") -> str:
    class_attr = f' class="{class_name}"' if class_name else ""
    extra_attr = f" {extra}" if extra else ""
    return f'<a{class_attr} href="{html.escape(href)}" target="_blank" rel="noreferrer"{extra_attr}>{html.escape(label)}</a>'


def local_link(href: str, label: str, class_name: str = "") -> str:
    class_attr = f' class="{class_name}"' if class_name else ""
    return f'<a{class_attr} href="{html.escape(href)}">{html.escape(label)}</a>'


def strip_script_tags(raw_html: str) -> str:
    return re.sub(r"<script\b[^>]*>.*?</script>", "", raw_html, flags=re.IGNORECASE | re.DOTALL).strip()


def load_x_embeds() -> list[str]:
    if not X_EMBED_SOURCE.exists():
        return []
    cleaned_html = strip_script_tags(X_EMBED_SOURCE.read_text(encoding="utf-8"))
    embeds = re.findall(r"<blockquote\b.*?</blockquote>", cleaned_html, flags=re.IGNORECASE | re.DOTALL)
    return [embed.strip() for embed in embeds if embed.strip()]


def render_link_list(items: list[tuple[str, str | None]], external: bool = False) -> str:
    parts = ["<ul class=\"link-list\">"]
    for label, href in items:
        if href:
            link = external_link(href, label) if external else local_link(href, label)
            parts.append(f"<li>{link}</li>")
        else:
            parts.append(f"<li>{html.escape(label)}</li>")
    parts.append("</ul>")
    return "\n".join(parts)


def render_page_title_panel(title: str) -> str:
    return dedent(
        f"""
        <section class="section page-title-section reveal">
          <div class="surface page-title-panel">
            <h1>{html.escape(title)}</h1>
          </div>
        </section>
        """
    ).strip()


def render_footer_icon(name: str) -> str:
    if name == "globe":
        return (
            '<svg viewBox="0 0 24 24" aria-hidden="true">'
            '<circle cx="12" cy="12" r="9"></circle>'
            '<path d="M3 12h18"></path>'
            '<path d="M12 3a15 15 0 0 1 0 18"></path>'
            '<path d="M12 3a15 15 0 0 0 0 18"></path>'
            "</svg>"
        )
    return (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path d="M4 4l16 16"></path>'
        '<path d="M20 4L4 20"></path>'
        "</svg>"
    )


def render_footer_follow_link(href: str, label: str, aria_label: str) -> str:
    return (
        f'<a class="footer-follow-link" href="{href}" target="_blank" rel="noreferrer"'
        f' aria-label="{html.escape(aria_label)}">'
        f"{html.escape(label)}</a>"
    )


def render_footer_language_link(label: str, href: str) -> str:
    return (
        f'<a class="footer-language-link" href="{html.escape(href)}">'
        f'{render_footer_icon("globe")}<span>{html.escape(label)}</span></a>'
    )


def render_footer(locale: str, current_dir: str, home_href: str, lang_switch_href: str, lang_switch_label: str) -> str:
    content = FOOTER_CONTENT[locale]
    follow_href = SITE_SETTINGS["follow_href"]
    follow_label = SITE_SETTINGS["follow_label"][locale]
    follow_aria_label = SITE_SETTINGS["follow_aria_label"][locale]
    logo_href = asset_href(current_dir, content["logo"])
    logo_alt = SITE_SETTINGS["brand_alt"][locale]
    top_action = (
        render_footer_language_link(lang_switch_label, lang_switch_href)
        if content["top_action"] == "language"
        else render_footer_follow_link(follow_href, follow_label, follow_aria_label)
    )
    bottom_action = (
        render_footer_follow_link(follow_href, follow_label, follow_aria_label)
        if content["bottom_action"] == "follow"
        else render_footer_language_link(lang_switch_label, lang_switch_href)
    )
    return dedent(
        f"""
        <footer class="site-footer">
          <div class="footer-shell">
            <div class="footer-row footer-row-top">
              <a class="footer-brand" href="{home_href}">
                <img src="{logo_href}" alt="{html.escape(logo_alt)}" loading="lazy">
              </a>
              <div class="footer-row-action">
                {top_action}
              </div>
            </div>
            <div class="footer-rule"></div>
            <div class="footer-row footer-row-bottom">
              <div class="footer-row-action">
                {bottom_action}
              </div>
              <p class="footer-copy">{html.escape(content["copyright"])}</p>
            </div>
          </div>
        </footer>
        """
    ).strip()


def render_section_divider_title(title_html: str) -> str:
    return (
        '<div class="section-divider-title">'
        '<span class="section-divider-line"></span>'
        f"<h2>{title_html}</h2>"
        '<span class="section-divider-line"></span>'
        "</div>"
    )


def render_logo_strip(locale: str, current_dir: str) -> str:
    items = []
    for logo in SITE_SETTINGS["home_logos"]:
        items.append(
            f'<a class="logo-chip" href="{html.escape(logo["href"])}" target="_blank" rel="noreferrer">'
            f'<img src="{asset_href(current_dir, logo["asset"])}" alt="{html.escape(logo["name"][locale])}" loading="lazy"></a>'
        )
    return '<div class="logo-strip">' + "".join(items) + "</div>"


def parse_publications(locale: str) -> list[dict[str, object]]:
    from bs4 import BeautifulSoup

    source = RAW_ROOT / ("publications/index.html" if locale == "jp" else "en/publications/index.html")
    soup = BeautifulSoup(source.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    main = soup.find("main")
    groups: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for widget in main.select("[data-widget_type]"):
        widget_type = widget.get("data-widget_type", "")
        if widget_type == "heading.default":
            text = normalize_space(widget.get_text(" ", strip=True))
            if text.isdigit():
                current = {"year": text, "items": []}
                groups.append(current)
        elif widget_type == "text-editor.default" and current is not None:
            entries = [normalize_space(li.get_text(" ", strip=True)) for li in widget.find_all("li")]
            current["items"] = entries
    return groups


def merge_publications(jp_groups: list[dict[str, object]], en_groups: list[dict[str, object]]) -> list[dict[str, object]]:
    merged = [group for group in en_groups if int(group["year"]) >= 2023]
    merged.extend(group for group in jp_groups if int(group["year"]) < 2023)
    return merged


def parse_news(locale: str) -> dict[str, list[dict[str, object]]]:
    from bs4 import BeautifulSoup

    source = RAW_ROOT / ("news/index.html" if locale == "jp" else "en/news/index.html")
    soup = BeautifulSoup(source.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    main = soup.find("main")
    sections = {"press_releases": [], "media": []}
    current_section: str | None = None
    current_group: dict[str, object] | None = None

    for widget in main.select("[data-widget_type]"):
        widget_type = widget.get("data-widget_type", "")
        text = normalize_space(widget.get_text(" ", strip=True))
        if widget_type == "heading.default":
            if text in {"Press Releases", "Media"}:
                current_section = "press_releases" if text == "Press Releases" else "media"
                current_group = None
            elif text in {"News", "We Update regularly!", "Twitter", "Follow Us"} or text.startswith("©"):
                continue
            elif current_section:
                current_group = {"kind": "group", "title": text, "items": []}
                sections[current_section].append(current_group)
        elif widget_type == "icon-list.default" and current_group is not None:
            items = []
            for anchor in widget.find_all("a", href=True):
                label = normalize_space(anchor.get_text(" ", strip=True))
                items.append({"text": label, "href": anchor["href"]})
            if items:
                current_group["items"] = items
        elif widget_type == "eael-info-box.default" and current_section == "press_releases":
            paragraph = widget.select_one(".infobox-content p")
            anchor = widget.find("a", href=True)
            if paragraph and anchor:
                sections["press_releases"].append(
                    {
                        "kind": "card",
                        "title": normalize_space(paragraph.get_text(" ", strip=True)),
                        "href": anchor["href"],
                        "label": normalize_space(anchor.get_text(" ", strip=True)),
                    }
                )
    return sections


def render_news_sections(data: dict[str, list[dict[str, object]]], current_dir: str) -> str:
    locale = "en" if current_dir.startswith("en") or current_dir == "en" else "jp"
    page = NEWS_PAGE_CONTENT[locale]
    titles = SITE_SETTINGS["news_titles"][locale]
    twitter_href = SITE_SETTINGS["follow_href"]
    twitter_embeds = load_x_embeds()
    embeds_html = ""
    if twitter_embeds:
        embeds_html = (
            '<div class="news-twitter-embed-list">'
            + "".join(f'<div class="news-twitter-embed">{embed_html}</div>' for embed_html in twitter_embeds)
            + "</div>"
        )
    parts = [render_page_title_panel(titles["page_title"])]
    parts.append(
        '<section class="section reveal">'
        f'{render_section_divider_title(html.escape(page["twitter_title"]))}'
        '<div class="surface news-twitter-panel">'
        f'<p>{html.escape(page["twitter_body"])}</p>'
        f"{embeds_html}"
        f'<p>{external_link(twitter_href, page["twitter_label"], "button button-secondary")}</p>'
        "</div></section>"
    )

    press_grid_class = "news-release-grid news-release-grid-cards" if locale == "en" else "news-release-grid"
    press_items = []
    for item in data["press_releases"]:
        if item["kind"] == "group":
            links = "".join(
                f'<li>{external_link(entry["href"], entry["text"])}</li>' for entry in item["items"]  # type: ignore[index]
            )
            press_items.append(
                "<article class=\"surface news-release-card\">"
                f"<h3>{html.escape(item['title'])}</h3>"
                f'<ul class="link-list">{links}</ul>'
                "</article>"
            )
        else:
            press_items.append(
                "<article class=\"surface news-release-card news-release-card-cta\">"
                f"<h3>{html.escape(item['title'])}</h3>"
                f"<p>{external_link(item['href'], item['label'], 'button button-secondary')}</p>"
                "</article>"
            )
    parts.append(
        '<section class="section reveal">'
        f'{render_section_divider_title(html.escape(titles["press_releases"]))}'
        f'<div class="{press_grid_class}">'
        f'{"".join(press_items)}'
        "</div></section>"
    )

    media_groups = []
    for item in data["media"]:
        links = "".join(
            f'<li>{external_link(entry["href"], entry["text"])}</li>' for entry in item["items"]  # type: ignore[index]
        )
        media_groups.append(
            '<article class="surface news-media-year">'
            f'<div class="section-kicker">{html.escape(item["title"])}</div>'
            f'<ul class="link-list dense">{links}</ul>'
            "</article>"
        )
    parts.append(
        '<section class="section reveal">'
        f'{render_section_divider_title(html.escape(titles["media"]))}'
        '<div class="news-media-stack">'
        f'{"".join(media_groups)}'
        "</div></section>"
    )
    if twitter_embeds:
        parts.append('<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>')
    return "\n".join(parts)


def render_publications(locale: str, groups: list[dict[str, object]]) -> str:
    parts = [
        render_page_title_panel(SITE_SETTINGS["publications_titles"][locale]["page_title"]),
        '<section class="section reveal"><div class="publication-archive">',
    ]
    for group in groups:
        items = "".join(f"<li>{html.escape(item)}</li>" for item in group["items"])  # type: ignore[index]
        parts.append(
            f'<article class="surface publication-year publication-year-static" id="year-{html.escape(group["year"])}">'
            f'<h2 class="publication-year-heading">{html.escape(group["year"])}</h2>'
            f'<ul class="publication-list">{items}</ul>'
            "</article>"
        )
    parts.append("</div></section>")
    return "\n".join(parts)


def render_home(locale: str, current_dir: str) -> str:
    content = HOME_CONTENT[locale]
    technology_href = route_href(current_dir, route_dir(locale, "technology"))
    about_href = route_href(current_dir, route_dir(locale, "about"))
    news_href = route_href(current_dir, route_dir(locale, "news"))
    contact_href = route_href(current_dir, route_dir(locale, "contact"))
    hero_image = content.get("hero_image", "media/hero-home.jpg")

    return dedent(
        f"""
        <section class="hero hero-home reveal">
          <div class="hero-copy">
            <p class="eyebrow">{html.escape(content["eyebrow"])}</p>
            <h1>{html.escape(content["title"])}</h1>
            <p class="lede">{html.escape(content["lede"])}</p>
            <div class="button-row">
              {local_link(technology_href, content["technology_label"], "button")}
            </div>
          </div>
          <div class="hero-media">
            <div class="hero-image-frame">
              <img src="{asset_href(current_dir, hero_image)}" alt="{html.escape(content['hero_image_alt'])}" loading="eager">
            </div>
          </div>
        </section>

        <section class="section split-section reveal home-intro">
          <div class="split-media surface">
            <img src="{asset_href(current_dir, content['intro_image'])}" alt="{html.escape(content['intro_image_alt'])}" loading="lazy">
          </div>
          <div class="split-copy">
            <div class="section-heading">
              <p class="eyebrow">{html.escape(content["intro_eyebrow"])}</p>
              <h2>{html.escape(content["intro_title"])}</h2>
              <p>{html.escape(content["intro_body"])}</p>
            </div>
            <div class="button-row">
              {local_link(about_href, content["intro_cta"], "button")}
            </div>
          </div>
        </section>

        <section class="section reveal">
          <article class="surface home-callout">
            <div class="section-heading">
              <p class="eyebrow">{html.escape(content["news_eyebrow"])}</p>
              <h2>{html.escape(content["news_title"])}</h2>
            </div>
            <div class="button-row">
              {local_link(news_href, content["news_cta"], "button")}
            </div>
          </article>
        </section>

        <section class="section reveal">
          <div class="section-heading">
            <p class="eyebrow">{html.escape(content["membership_eyebrow"])}</p>
            <h2>{html.escape(content["membership_title"])}</h2>
            <p>{html.escape(content["membership_body"])}</p>
          </div>
          {render_logo_strip(locale, current_dir)}
        </section>

        <section class="section split-section reveal home-contact">
          <div class="split-copy">
            <div class="section-heading">
              <p class="eyebrow">{html.escape(content["contact_eyebrow"])}</p>
              <h2>{html.escape(content["contact_title"])}</h2>
              <p>{html.escape(content["contact_body"])}</p>
            </div>
            <div class="button-row">
              {local_link(contact_href, content["contact_cta"], "button")}
            </div>
          </div>
          <div class="split-media surface">
            <img src="{asset_href(current_dir, content['contact_image'])}" alt="{html.escape(content['contact_image_alt'])}" loading="lazy">
          </div>
        </section>
        """
    ).strip()


def render_member_cards(
    members: list[dict[str, str]],
    current_dir: str,
    locale: str,
    show_role: bool = True,
    compact: bool = False,
) -> str:
    cards = []
    for member in members:
        title = html.escape(member["name"])
        if member.get("href"):
            title = external_link(member["href"], member["name"])
        details: list[str] = []
        if show_role and member.get("role"):
            details.append(html.escape(member["role"]))
        org_lines = [html.escape(part.strip()) for part in member["org"].split(" / ") if part.strip()]
        if org_lines:
            if show_role and locale == "jp":
                details.append(f"({org_lines[0]})")
                details.extend(org_lines[1:])
            else:
                details.extend(org_lines)
        detail_html = "<br>".join(details)
        image = asset_href(current_dir, member["image"])
        compact_class = " member-card-compact" if compact else ""
        cards.append(
            f"<article class=\"member-card surface reveal{compact_class}\">"
            f"<img src=\"{image}\" alt=\"{html.escape(member['name'])}\" loading=\"lazy\">"
            f"<div><h3>{title}</h3><p>{detail_html}</p></div>"
            "</article>"
        )
    return "".join(cards)


def render_about_rule(title: str) -> str:
    return (
        '<div class="about-rule reveal">'
        '<span class="about-rule-line"></span>'
        f"<h3>{html.escape(title)}</h3>"
        '<span class="about-rule-line"></span>'
        "</div>"
    )


def render_logo_panels(current_dir: str, logos: list[dict[str, str]]) -> str:
    items = []
    for logo in logos:
        items.append(
            '<a class="about-logo-panel surface reveal"'
            f' href="{html.escape(logo["href"])}" target="_blank" rel="noreferrer">'
            f'<img src="{asset_href(current_dir, logo["image"])}" alt="{html.escape(logo["name"])}" loading="lazy"></a>'
        )
    return '<div class="about-logo-grid">' + "".join(items) + "</div>"


def render_about_supporting_list(items: list[dict[str, str | None]]) -> str:
    parts = ['<ul class="about-support-list surface reveal">']
    for item in items:
        content = external_link(item["href"], item["name"]) if item["href"] else html.escape(item["name"])
        parts.append(f"<li>{content}</li>")
    parts.append("</ul>")
    return "".join(parts)


def render_about_tech_cards(cards_data: list[dict[str, str | None]], current_dir: str) -> str:
    cards = []
    for card in cards_data:
        sponsor_html = ""
        sponsor = card["sponsor_image"]
        sponsor_name = card["sponsor_name"]
        sponsor_href = card["sponsor_href"]
        if sponsor and sponsor_href and sponsor_name:
            sponsor_html = (
                '<a class="about-tech-sponsor"'
                f' href="{html.escape(sponsor_href)}" target="_blank" rel="noreferrer">'
                f'<img src="{asset_href(current_dir, sponsor)}" alt="{html.escape(sponsor_name)}" loading="lazy"></a>'
            )
        cards.append(
            '<article class="about-tech-card surface reveal">'
            f'<img class="about-tech-icon" src="{asset_href(current_dir, card["image"])}" alt="{html.escape(card["title"])}" loading="lazy">'
            f"<h3>{html.escape(card['title'])}</h3>"
            f"{sponsor_html}"
            "</article>"
        )
    return '<div class="about-tech-grid">' + "".join(cards) + "</div>"


def render_about(locale: str, current_dir: str) -> str:
    page = ABOUT_PAGE_DATA[locale]
    home_content = HOME_CONTENT[locale]
    mission = page["mission"]
    mission_media = mission["media"]
    team = page["team"]
    document = page["document"]
    technology = page["technology"]
    contact_cta = page["contact_cta"]
    mission_title = SITE_SETTINGS["about_mission_title"][locale]
    article_href = asset_href(current_dir, "docs/article-of-incorporation.pdf")
    technology_href = route_href(current_dir, route_dir(locale, "technology"))
    contact_href = route_href(current_dir, route_dir(locale, "contact"))
    video_src = asset_href(current_dir, "media/ai-suitcase.mp4")
    video_poster = asset_href(current_dir, home_content.get("hero_image", "media/hero-home.jpg"))
    contact_section_class = "section split-section about-contact-grid reveal" if contact_cta["show_image"] else "section reveal"
    mission_parts = [
        '<section class="section about-page-title reveal">',
        f'<h1>{html.escape(page["page_title"])}</h1>',
        "</section>",
    ]
    if mission_media["type"] == "video":
        mission_parts.extend(
            [
                '<section class="section about-mission-grid reveal">',
                '<div class="surface about-mission-copy">',
                f'<h2>{html.escape(mission_title)}</h2>',
                f'<p>{html.escape(mission["body"])}</p>',
                "</div>",
                '<div class="video-shell surface about-inline-video">',
                f'<video autoplay muted loop playsinline preload="metadata" poster="{video_poster}">',
                f'<source src="{video_src}" type="video/mp4">',
                "</video></div></section>",
            ]
        )
    else:
        mission_parts.extend(
            [
                '<section class="section reveal">',
                '<div class="surface about-mission-copy about-mission-copy-single">',
                f'<h2>{html.escape(mission_title)}</h2>',
                f'<p>{html.escape(mission["body"])}</p>',
                "</div></section>",
                '<section class="section about-media-grid reveal">',
                f'<div class="split-media surface"><img src="{asset_href(current_dir, mission_media["image"])}" alt="{html.escape(mission_media["image_alt"])}" loading="lazy"></div>',
                '<div class="video-shell surface about-inline-video">',
                f'<video autoplay muted loop playsinline preload="metadata" poster="{video_poster}">',
                f'<source src="{video_src}" type="video/mp4">',
                "</video></div></section>",
            ]
        )

    team_members = render_member_cards(team["board"]["members"], current_dir, locale, show_role=True)
    distinguished_members = render_member_cards(
        team["distinguished"]["members"], current_dir, locale, show_role=False, compact=True
    )
    contact_media = ""
    if contact_cta["show_image"]:
        contact_media = (
            '<div class="split-media surface">'
            f'<img src="{asset_href(current_dir, "media/home-contact.jpg")}" alt="{html.escape(contact_cta["image_alt"])}" loading="lazy"></div>'
        )

    return dedent(
        f"""
        {' '.join(mission_parts)}

        <section class="section reveal">
          <div class="section-heading">
            <h2>{html.escape(team["title"])}</h2>
          </div>
          {render_about_rule(team["board"]["title"])}
          <div class="about-member-grid about-member-grid-board">
            {team_members}
          </div>
          {render_about_rule(team["primary"]["title"])}
          {render_logo_panels(current_dir, team["primary"]["members"])}
          {render_about_rule(team["associate"]["title"])}
          <div class="about-empty reveal"></div>
          {render_about_rule(team["distinguished"]["title"])}
          <div class="about-member-grid about-member-grid-distinguished">
            {distinguished_members}
          </div>
          {render_about_rule(team["supporting"]["title"])}
          {render_about_supporting_list(team["supporting"]["members"])}
        </section>

        <section class="section reveal">
          <div class="surface about-document">
            <h2>{html.escape(document["title"])}</h2>
            <p>{local_link(article_href, document["label"], "button")}</p>
          </div>
        </section>

        <section class="section reveal">
          <div class="about-tech-head">
            <div class="section-heading">
              <p class="eyebrow">{html.escape(technology["eyebrow"])}</p>
              <h2>{html.escape(technology["title"])}</h2>
            </div>
            <div class="button-row">
              {local_link(technology_href, technology["label"], "button")}
            </div>
          </div>
          {render_about_tech_cards(technology["cards"], current_dir)}
        </section>

        <section class="{contact_section_class}">
          <div class="surface about-contact-copy">
            <h2>{html.escape(contact_cta["title"])}</h2>
            <p>{html.escape(contact_cta["body"])}</p>
            <div class="button-row">
              {local_link(contact_href, contact_cta["label"], "button")}
            </div>
          </div>
          {contact_media}
        </section>
        """
    ).strip()


def youtube_embed_src(video_id: str, locale: str) -> str:
    params = ["modestbranding=1", "rel=0", "playsinline=1"]
    if locale == "en":
        params.extend(["hl=en", "cc_lang_pref=en", "cc_load_policy=1"])
    return f"https://www.youtube.com/embed/{video_id}?{'&'.join(params)}"


def render_youtube_embed(video_id: str, title: str, locale: str, loading: str = "lazy") -> str:
    return (
        '<div class="video-shell surface technology-video-frame">'
        f'<iframe src="{youtube_embed_src(video_id, locale)}" title="{html.escape(title)}"'
        f' loading="{html.escape(loading)}" frameborder="0"'
        ' allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"'
        " referrerpolicy=\"strict-origin-when-cross-origin\" allowfullscreen></iframe>"
        "</div>"
    )


def render_technology_cards(locale: str, current_dir: str) -> str:
    cards = []
    for title, image, sponsor, sponsor_name, sponsor_href in TECH_CONTENT[locale]["technology_cards"]:
        sponsor_html = '<div class="technology-card-sponsor technology-card-sponsor-empty"></div>'
        if sponsor and sponsor_href and sponsor_name:
            sponsor_html = (
                '<a class="technology-card-sponsor"'
                f' href="{html.escape(sponsor_href)}" target="_blank" rel="noreferrer">'
                f'<img src="{asset_href(current_dir, sponsor)}" alt="{html.escape(sponsor_name)}" loading="lazy"></a>'
            )
        cards.append(
            '<article class="technology-card surface reveal">'
            f'<img class="technology-card-image" src="{asset_href(current_dir, image)}" alt="{html.escape(title)}" loading="lazy">'
            f"<h3>{html.escape(title)}</h3>"
            f"{sponsor_html}"
            "</article>"
        )
    return '<div class="technology-card-grid">' + "".join(cards) + "</div>"


def render_technology_system_labels(labels: list[str]) -> str:
    if not labels:
        return ""
    items = "".join(f"<li>{html.escape(label)}</li>" for label in labels)
    return f'<ul class="technology-system-labels">{items}</ul>'


def render_technology(locale: str, current_dir: str) -> str:
    content = TECH_CONTENT[locale]
    contact_href = route_href(current_dir, route_dir(locale, "contact"))
    system_media = ""
    if content["system_image"]:
        system_media = (
            '<div class="technology-system-media surface reveal">'
            f'<img src="{asset_href(current_dir, content["system_image"])}" alt="{html.escape(content["system_image_alt"])}" loading="lazy">'
            f"{render_technology_system_labels(content['system_labels'])}"
            "</div>"
        )

    contact_section_class = "section split-section technology-contact reveal" if content["contact_image"] else "section reveal"
    contact_media = ""
    if content["contact_image"]:
        contact_media = (
            '<div class="split-media surface">'
            f'<img src="{asset_href(current_dir, content["contact_image"])}" alt="{html.escape(content["contact_image_alt"])}" loading="lazy"></div>'
        )

    other_videos = "".join(
        f'<div class="reveal">{render_youtube_embed(video_id, title, locale)}</div>'
        for video_id, title in content["other_videos"]
    )

    return dedent(
        f"""
        <section class="section technology-page-title reveal">
          <div class="surface technology-title-panel">
            <h1>{html.escape(content["page_title"])}</h1>
          </div>
        </section>

        <section class="section reveal">
          {render_youtube_embed(content["main_video_id"], content["main_video_title"], locale, loading="eager")}
        </section>

        <section class="section technology-system-section reveal">
          <div class="technology-system-copy">
            <h2>{html.escape(content["system_title"])}</h2>
          </div>
          {system_media}
        </section>

        <section class="section reveal">
          <div class="technology-section-title">
            <h2>{content["technology_title_html"]}</h2>
          </div>
          {render_technology_cards(locale, current_dir)}
        </section>

        <section class="section reveal">
          <div class="technology-section-title">
            <h2>{html.escape(content["other_videos_title"])}</h2>
          </div>
          <div class="technology-video-grid">
            {other_videos}
          </div>
        </section>

        <section class="{contact_section_class}">
          <div class="surface technology-contact-copy">
            <h2>{html.escape(content["contact_title"])}</h2>
            <p>{html.escape(content["contact_body"])}</p>
            <div class="button-row">
              {local_link(contact_href, content["contact_label"], "button")}
            </div>
          </div>
          {contact_media}
        </section>
        """
    ).strip()


def render_related_work(locale: str, current_dir: str) -> str:
    content = RELATED_CONTENT[locale]
    titles = SITE_SETTINGS["related_titles"][locale]
    open_source_cards = "".join(
        "<article class=\"surface resource-card reveal\">"
        f"<h3>{html.escape(title)}</h3><p>{html.escape(body)}</p><p>{external_link(href, 'Open Resource', 'button button-secondary')}</p>"
        "</article>"
        for title, body, href in content["open_source"]
    )
    resource_cards = "".join(
        "<article class=\"surface resource-card reveal\">"
        f"<h3>{html.escape(title)}</h3><p>{html.escape(body)}</p><p>{external_link(href, 'Visit', 'button button-secondary')}</p>"
        "</article>"
        for title, body, href in content["resources"]
    )
    return dedent(
        f"""
        {render_page_title_panel(titles["page_title"])}

        <section class="section reveal">
          <div class="surface related-intro-panel">
            <p>{html.escape(content["intro"])}</p>
          </div>
        </section>

        <section class="section reveal">
          {render_section_divider_title(html.escape(titles["open_source"]))}
          <div class="card-grid card-grid-2">
            {open_source_cards}
          </div>
        </section>

        <section class="section reveal">
          {render_section_divider_title(html.escape(titles["resources"]))}
          <div class="card-grid card-grid-2">
            {resource_cards}
          </div>
        </section>
        """
    ).strip()


def render_contact(locale: str, current_dir: str) -> str:
    content = CONTACT_CONTENT[locale]
    labels = SITE_SETTINGS["contact_labels"][locale]
    email_href = f"mailto:{content['email']}"
    details_html = (
        '<div class="contact-detail-stack">'
        '<div class="contact-detail-item">'
        f'<p class="section-kicker">{html.escape(labels["address"])}</p>'
        f'<p>{html.escape(content["address"])}</p>'
        "</div>"
        '<div class="contact-detail-item">'
        f'<p class="section-kicker">{html.escape(labels["email"])}</p>'
        f'<p>{html.escape(content["email"])}</p>'
        "</div></div>"
    )
    info_panel = dedent(
        f"""
        <div class="surface contact-panel">
          {details_html}
          <div class="button-row">
            {local_link(email_href, content["button_label"], "button")}
          </div>
        </div>
        """
    ).strip()
    map_panel = dedent(
        f"""
        <div class="surface contact-map-frame">
          <iframe src="{html.escape(content["map_embed"])}" title="{html.escape(content["title"])} map" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>
        """
    ).strip()
    if content["layout"] == "split":
        body = (
            '<section class="section split-section contact-page-layout reveal">'
            f"{info_panel}{map_panel}"
            "</section>"
        )
    else:
        body = (
            '<section class="section reveal">'
            f"{info_panel}"
            "</section>"
            '<section class="section reveal">'
            f"{map_panel}"
            "</section>"
        )
    return dedent(
        f"""
        {render_page_title_panel(content["page_title"])}
        {body}
        """
    ).strip()


def render_nav(locale: str, route: str, current_dir: str) -> str:
    items = []
    for nav_route, label in NAV_LABELS[locale].items():
        href = route_href(current_dir, route_dir(locale, nav_route))
        active = " is-active" if nav_route == route else ""
        items.append(f'<a class="nav-link{active}" href="{href}">{html.escape(label)}</a>')
    return "".join(items)


def render_page(locale: str, route: str, body_html: str) -> str:
    current_dir = route_dir(locale, route)
    meta = PAGE_META[locale][route]
    other_locale = "en" if locale == "jp" else "jp"
    lang_switch_label = "English" if locale == "jp" else "日本語"
    lang_switch_href = route_href(current_dir, route_dir(other_locale, route))
    home_href = route_href(current_dir, route_dir(locale, ""))
    css_href = asset_href(current_dir, "site.css")
    js_href = asset_href(current_dir, "site.js")
    logo_header = asset_href(current_dir, "media/logo-header-en.png" if locale == "en" else "media/logo-header.png")
    lang_attr = "ja" if locale == "jp" else "en"
    menu_label = SITE_SETTINGS["menu_label"][locale]
    brand_alt = SITE_SETTINGS["brand_alt"][locale]

    return dedent(
        f"""<!doctype html>
        <html lang="{lang_attr}">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>{html.escape(meta["title"])}</title>
          <meta name="description" content="{html.escape(meta["description"])}">
          <link rel="preconnect" href="https://fonts.googleapis.com">
          <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
          <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Noto+Sans+JP:wght@400;500;700;800&display=swap" rel="stylesheet">
          <link rel="stylesheet" href="{css_href}">
        </head>
        <body class="locale-{locale} route-{route or 'home'}">
          <div class="page-chrome"></div>
          <header class="site-header">
            <div class="header-inner">
              <a class="brand" href="{home_href}">
                <img class="brand-logo" src="{logo_header}" alt="{html.escape(brand_alt)}">
              </a>
              <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">{html.escape(menu_label)}</button>
              <nav class="site-nav" id="site-nav">
                {render_nav(locale, route, current_dir)}
                <a class="lang-switch" href="{lang_switch_href}">{lang_switch_label}</a>
              </nav>
            </div>
          </header>

          <main class="site-main">
            {body_html}
          </main>

          {render_footer(locale, current_dir, home_href, lang_switch_href, lang_switch_label)}

          <script src="{js_href}" defer></script>
        </body>
        </html>
        """
    ).strip() + "\n"


def copy_curated_assets() -> None:
    for relative_target, source in CURATED_ASSETS.items():
        target = ASSETS_DIR / relative_target
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def write_file(path: Path, content: str) -> None:
    make_dir_for_file(path)
    path.write_text(content, encoding="utf-8")


CONTENT_GLOBAL_MAP = {
    "site_settings": "SITE_SETTINGS",
    "nav_labels": "NAV_LABELS",
    "page_meta": "PAGE_META",
    "home_content": "HOME_CONTENT",
    "about_page_data": "ABOUT_PAGE_DATA",
    "tech_content": "TECH_CONTENT",
    "related_content": "RELATED_CONTENT",
    "news_page_content": "NEWS_PAGE_CONTENT",
    "contact_content": "CONTACT_CONTENT",
    "footer_content": "FOOTER_CONTENT",
}


def _snapshot_content_globals() -> dict[str, object]:
    return {name: deepcopy(globals()[target]) for name, target in CONTENT_GLOBAL_MAP.items()}


def _apply_content_globals(content_data: dict[str, object]) -> None:
    for name, target in CONTENT_GLOBAL_MAP.items():
        globals()[target] = deepcopy(content_data[name])


def _render_site(
    news_by_locale: dict[str, dict[str, list[dict[str, object]]]],
    publications_by_locale: dict[str, list[dict[str, object]]],
    copy_assets: bool,
) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    write_file(OUTPUT_ROOT / ".nojekyll", "")
    if copy_assets:
        copy_curated_assets()

    renderers = {
        "": lambda locale, current_dir: render_home(locale, current_dir),
        "about": lambda locale, current_dir: render_about(locale, current_dir),
        "technology": lambda locale, current_dir: render_technology(locale, current_dir),
        "related-work": lambda locale, current_dir: render_related_work(locale, current_dir),
        "news": lambda locale, current_dir: render_news_sections(news_by_locale[locale], current_dir),
        "publications": lambda locale, current_dir: render_publications(locale, publications_by_locale[locale]),
        "contact": lambda locale, current_dir: render_contact(locale, current_dir),
    }

    for locale in ("jp", "en"):
        for route in ROUTES:
            current_dir = route_dir(locale, route)
            body_html = renderers[route](locale, current_dir)
            output = render_page(locale, route, body_html)
            write_file(page_output_path(locale, route), output)


def build_from_content_data(content_data: dict[str, object], copy_assets: bool = False) -> None:
    previous = _snapshot_content_globals()
    try:
        _apply_content_globals(content_data)
        _render_site(content_data["news_sections"], content_data["publications"], copy_assets)
    finally:
        _apply_content_globals(previous)


def build() -> None:
    jp_news = parse_news("jp")
    en_news = parse_news("en")
    jp_publications = parse_publications("jp")
    en_publications = parse_publications("en")
    merged_jp_publications = merge_publications(jp_publications, en_publications)
    _render_site(
        {"jp": jp_news, "en": en_news},
        {"jp": merged_jp_publications, "en": en_publications},
        copy_assets=True,
    )


if __name__ == "__main__":
    build()
