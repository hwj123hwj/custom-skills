<div align="center">

<a href="https://weread.qq.com/r/weread-skills"><img src="https://rescdn.qqmail.com/node/wr/wrpage/style/images/independent/appleTouchIcon/apple-touch-icon-144x144.png" width="48" alt="WeRead" /></a>

# WeRead SKILLS

**Let AI be your reading partner**

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Auto--Sync-blue?logo=github-actions)](.github/workflows/sync.yml)
[![Agent Skills](https://img.shields.io/badge/Agent-Skills-purple)](https://skills.sh/gandli/weread-skills)
[![中文文档](https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-green)](README.zh.md)

---

Connect your WeRead account, let AI assistant access your reading records anytime.
This is the official WeRead Agent Skills collection, automatically synced via GitHub Actions.

</div>

## Quick Setup

### Step 1: Install the Skill

Copy the following command and send it to your AI assistant:

```
Download https://cdn.weread.qq.com/skills/weread-skills.zip and install the skill
```

Or install directly via CLI:

```bash
npx skills add gandli/weread-skills
```

### Step 2: Get Your API Key

1. Go to [WeRead Official Skill Page](https://weread.qq.com/r/weread-skills)
2. Log in with your WeRead account
3. Copy your API Key (format: `wrk-xxxxxxxx`)

### Step 3: Connect Your Account

Send the following command to your AI assistant with your API Key:

```
export WEREAD_API_KEY=<your-api-key>
```

> **Note:** The API Key is used to connect your WeRead account. Your data is only visible to you.

## Features

| Feature | Description |
|---------|-------------|
| 📚 **Bookshelf Access** | Browse your personal bookshelf, get a complete overview of your collection |
| 📊 **Reading Statistics** | In-depth analysis of duration, days, and preferences to quantify your reading habits |
| 📝 **Notes & Highlights** | View personal highlights and thoughts, export notes, review your thinking |
| 🔍 **Book Search** | Search any book in the library, quickly get title, author, rating, and more |
| 📖 **Book Details** | View book details, table of contents, reading progress, understand your reading journey |
| ✨ **Smart Recommendations** | Personalized or similar book recommendations based on your reading preferences |

## Usage

After setup, just talk to your AI assistant naturally:

```
Search for books about artificial intelligence
```

```
View my weekly reading statistics
```

```
Export all notes from "Sapiens"
```

```
Show my bookshelf and recommend similar books
```

```
How many books have I read this year?
```

## How It Works

The Skill connects to WeRead's Agent API Gateway using your API Key:

```
POST https://i.weread.qq.com/api/agent/gateway
Authorization: Bearer $WEREAD_API_KEY
```

The API Key binds to your WeRead identity (vid), so all personal data requests are automatically scoped to your account — no need to manually pass user IDs.

## Structure

```
weread-skills/
├── skills/
│   └── weread/               # Skill subdirectory
│       ├── SKILL.md          # Main skill file with frontmatter
│       ├── book.md           # Book related functions
│       ├── search.md         # Search related functions
│       ├── shelf.md          # Shelf management
│       ├── notes.md          # Notes and highlights
│       ├── review.md         # Reviews and thoughts
│       ├── profile.md        # Profile information
│       ├── readdata.md       # Reading statistics
│       ├── discover.md       # Discovery and recommendations
│       ├── SKILL-README.md   # Skill documentation
│       └── metadata.json     # Metadata
├── README.md                 # English documentation (main)
├── README.zh.md              # Chinese documentation
├── CHANGELOG.md              # Changelog
└── .github/workflows/
    └── sync.yml              # Auto-sync workflow
```

## Automatic Sync

This repository automatically syncs the latest SKILLS files from the [official WeRead source](https://weread.qq.com/r/weread-skills) daily via GitHub Actions.

Sync schedule: Daily at UTC 00:00 (Beijing time 08:00)

## Official Resources

- 🌐 **Official Website**: [https://weread.qq.com/](https://weread.qq.com/)
- 📖 **Skill Introduction**: [https://weread.qq.com/r/weread-skills](https://weread.qq.com/r/weread-skills)
- ⬇️ **Official Download**: `https://cdn.weread.qq.com/skills/weread-skills.zip`

## Disclaimer

This repository is for technical research and learning purposes only. All SKILLS files are copyrighted by WeRead.

---

*Note: This is a community-maintained mirror of the official WeRead Skills. For the most up-to-date version, always check the [official website](https://weread.qq.com/r/weread-skills).*
