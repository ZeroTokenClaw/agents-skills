# agents-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Skills](https://img.shields.io/badge/skills-305-blue.svg)](./SKILLS.md)
[![GitHub](https://img.shields.io/badge/GitHub-ZeroTokenClaw%2Fagents--skills-181717?logo=github)](https://github.com/ZeroTokenClaw/agents-skills)

**寮€婧?*鐨?Cursor / Agent Skills 鍚堥泦涓庡浠介暅鍍忋€?
瀵瑰簲鏈満鐩綍锛歚~/.agents/skills`锛圵indows锛歚%USERPROFILE%\.agents\skills`锛夈€?
| 椤?| 鍊?|
| --- | --- |
| 缁存姢璐﹀彿 | [ZeroTokenClaw](https://github.com/ZeroTokenClaw) |
| Skill 鏁伴噺 | **305**锛堟瘡涓瓙鐩綍鍚?`SKILL.md`锛?|
| 鍙鎬?| **Public** |
| 涓诲垎鏀?| `main` |
| 浠撳簱璁稿彲 | [MIT](./LICENSE)锛堝瓙鐩綍鍙彟鏈夌涓夋柟璁稿彲锛?|
| 瀹屾暣鐩綍 | [`SKILLS.md`](./SKILLS.md) |

> Cursor 杩愯鏃惰鍙栫殑鏄湰鏈?skills 鐩綍锛涙湰浠撳簱鐢ㄤ簬澶囦唤銆佸垎浜笌璺ㄦ満鍚屾銆?
---

## 鐩綍

- [浠撳簱缁撴瀯](#浠撳簱缁撴瀯)
- [蹇€熷紑濮媇(#蹇€熷紑濮?
- [鍦?Cursor 涓娇鐢╙(#鍦?cursor-涓娇鐢?
- [濡備綍閫?Skill](#濡備綍閫?skill)
- [鑳藉姏鍩熸瑙圿(#鑳藉姏鍩熸瑙?
- [Skill 缂栧啓绾﹀畾](#skill-缂栧啓绾﹀畾)
- [璐＄尞鎸囧崡](#璐＄尞鎸囧崡)
- [璁稿彲涓庡綊灞瀅(#璁稿彲涓庡綊灞?
- [FAQ](#faq)
- [鐩稿叧閾炬帴](#鐩稿叧閾炬帴)

---

## 浠撳簱缁撴瀯

```text
agents-skills/
鈹溾攢鈹€ README.md                 # 鏈鏄?鈹溾攢鈹€ LICENSE                   # 浠撳簱绾?MIT + 绗笁鏂瑰０鏄?鈹溾攢鈹€ SKILLS.md                 # 303 涓?skill 瀹屾暣鐩綍
鈹溾攢鈹€ cursor-rules/             # 绮鹃€?Cursor Rules 闀滃儚锛堝畨瑁呭埌 ~/.cursor/rules锛?鈹溾攢鈹€ .gitignore
鈹溾攢鈹€ practical-skills-index/   # 鎬昏矾鐢辩储寮曪紙浼樺厛璇伙級
鈹溾攢鈹€ anbeime-skills-index/     # 涓枃鍨傜洿鎶€鑳借矾鐢?鈹溾攢鈹€ <skill-name>/
鈹?  鈹溾攢鈹€ SKILL.md              # 蹇呴渶锛歠rontmatter + 浣跨敤璇存槑
鈹?  鈹溾攢鈹€ LICENSE*              # 鍙€夛細璇?skill 鑷韩璁稿彲
鈹?  鈹溾攢鈹€ references/           # 鍙€夛細璧勬枡銆佹簮閾炬帴
鈹?  鈹溾攢鈹€ scripts/              # 鍙€夛細杈呭姪鑴氭湰
鈹?  鈹溾攢鈹€ agents/               # 鍙€夛細openai.yaml 绛?鈹?  鈹斺攢鈹€ ...
鈹斺攢鈹€ ...
```

姣忎釜涓€绾у瓙鐩綍 = 涓€涓嫭绔?skill銆侫gent 閫氳繃 `SKILL.md` 澶撮儴鐨?`name` / `description` 鍋氳Е鍙戝尮閰嶃€?
---

## 蹇€熷紑濮?
### 鍏ㄦ柊瀹夎鍒版湰鏈?
```bash
# 寤鸿鍏堝浠藉凡鏈夌洰褰?mv ~/.agents/skills ~/.agents/skills.bak 2>/dev/null || true

git clone https://github.com/ZeroTokenClaw/agents-skills.git ~/.agents/skills
```

Windows锛圥owerShell锛夛細

```powershell
$dest = "$env:USERPROFILE\.agents\skills"
if (Test-Path $dest) { Rename-Item $dest "skills.bak.$(Get-Date -Format yyyyMMdd)" }
git clone https://github.com/ZeroTokenClaw/agents-skills.git $dest
```

### 娴呭厠闅嗭紙浣撶Н鏇村皬銆佹洿蹇級

```bash
git clone --depth 1 https://github.com/ZeroTokenClaw/agents-skills.git ~/.agents/skills
```

### 鍙彇鏌愪竴涓?skill

```bash
# 绋€鐤忔鍑虹ず渚嬶細鍙 megaflow
git clone --filter=blob:none --sparse https://github.com/ZeroTokenClaw/agents-skills.git /tmp/agents-skills
cd /tmp/agents-skills
git sparse-checkout set megaflow
cp -r megaflow ~/.agents/skills/
```

### 宸叉湁鏈湴鐩綍锛屽彧鎷夊彇鏇存柊

```bash
cd ~/.agents/skills
git pull origin main
```

### 鏈湴鏀瑰畬鍚庢帹鍥?GitHub锛堢淮鎶よ€咃級

```bash
cd ~/.agents/skills
git add -A
git status
git commit -m "feat(skills): update ..."
git push origin main
```

---

## 鍦?Cursor 涓娇鐢?
1. 纭 skills 钀藉湪 Cursor 鍙彂鐜拌矾寰勶紙甯歌涓?`~/.agents/skills` 鎴?Cursor Agent Stores 鍚屾鐩綍锛夈€?2. 鏂板紑 Agent 瀵硅瘽锛岀洿鎺ユ弿杩颁换鍔★紱妯″瀷浼氭寜鍚?skill 鐨?`description` 鑷姩鍖归厤銆?3. 涔熷彲鏄惧紡鎸囧畾锛氥€屾寜 `practical-skills-index` 閫夊瀷銆嶆垨銆屼娇鐢?`megaflow` skill銆嶃€?4. 淇敼 skill 鍚庝竴鑸棤闇€閲嶅惎锛涜嫢鏈敓鏁堬紝鏂板紑涓€杞璇濆嵆鍙€?
### 璺ㄩ」鐩?Cursor Rules

浠撳簱鍐?[`cursor-rules/`](./cursor-rules/) 涓虹簿閫?`.mdc` 闀滃儚銆傝法椤圭洰鐢熸晥闇€瀹夎鍒扮敤鎴风骇鐩綍锛堥潪椤圭洰 `.cursor/rules`锛夛細

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\rules" | Out-Null
Copy-Item "$env:USERPROFILE\.agents\skills\cursor-rules\*" "$env:USERPROFILE\.cursor\rules\" -Force
```

璇﹁ [`cursor-rules/RULES.md`](./cursor-rules/RULES.md)銆?
鍙€夊彂鐜版笭閬擄細

- 鏈湴绱㈠紩锛歚practical-skills-index` / `anbeime-skills-index`
- 绀惧尯锛歚npx skills find <鍏抽敭璇?` 路 [skills.sh](https://skills.sh/)

---

## 濡備綍閫?Skill

涓嶈浠?300+ 鐩綍閲岀洸缈汇€傛寜鍦烘櫙璇荤储寮曪細

| 鍦烘櫙 | 鍏ュ彛 Skill |
| --- | --- |
| 鎬昏矾鐢憋紙鍔炲叕 / Web / 浜у搧 / 绠楁硶 / 鏈哄櫒浜?/ 鍐呭锛?| **`practical-skills-index`** |
| 鍐呭鍒涗綔銆佺煭瑙嗛銆佺數鍟嗐€乀TS銆佹暟瀛椾汉銆丱bsidian | **`anbeime-skills-index`** |
| LangGraph / 缂栫爜 Agent 缂栨帓 | `langgraph-coding-agent` |
| 璁＄畻 / 璐㈠姟 / 鏁版嵁鍒嗘瀽 | `calc-analysis-skills` |
| 浜у搧 / 鍓嶇 / 娴嬭瘯宸ュ叿閾?| `product-dev-skills` |
| 瀹囨爲鍏疯韩鑳藉姏鍖?| `unitree-embodied-skills` |

### 蹇嵎璺敱锛堟憳鑷€荤储寮曪級

| 浠诲姟 | Skill |
| --- | --- |
| 缃戦〉 / UI | `frontend-design` |
| React 鎬ц兘 | `vercel-react-best-practices` |
| E2E | `playwright-testing` |
| PPT | `pptx` / `ppt-generator` |
| 澶т綅绉诲厜娴?/ 鐐硅窡韪?| `megaflow` |
| 涓撳埄浜ゅ簳 / 鏉冨埄瑕佹眰 | `patent-drafting` |
| 杞憲鐧昏鏉愭枡 | `software-copyright-cn` |
| 浜鸿劯绛惧埌 + 瀵艰璺熼殢 | `tour-checkin-follow` |
| 鐭棰戝叏娴佺▼ | `video-creation-suite` |
| 璺ㄥ鐢靛晢 | `ecommerce-full-pipeline` |
| 鏋舵瀯浜や簰鍥?| `archify` |

瀹屾暣娓呭崟瑙?[`SKILLS.md`](./SKILLS.md)銆?
---

## 鑳藉姏鍩熸瑙?
浠ヤ笅涓轰究浜庢祻瑙堢殑绮楀垎锛堟湁浜ゅ弶锛屼互绱㈠紩琛ㄤ负鍑嗭級锛?
### 绱㈠紩涓?Skill 宸ョ▼

`practical-skills-index` 路 `anbeime-skills-index` 路 `find-skills` 路 `suggesting-skills` 路 `writing-skills` 路 `building-skills-from-patterns` 路 `using-agent-skills` 路 `using-superpowers`

### 璁＄畻鏈鸿瑙?/ 鏈哄櫒浜?/ 鍏疯韩

鍚?YOLO 鍏ㄥ妗躲€丱penCV銆丼LAM/Nav2銆佸畤鏍?G1/Go2銆佷汉鑴哥鍒拌窡闅忋€佸厜娴佺偣璺熻釜绛夛細

`yolo` 路 `yolo-pipeline` 路 `yolo-training` 路 `yolo-models` 路 `yolo-datasets` 路 `yolo-integration` 路 `opencv` 路 `computer-vision-opencv` 路 `computer-vision-pipeline` 路 `megaflow` 路 `multi-object-tracking` 路 `cv-mediapipe` 路 `slam` 路 `laser-slam` 路 `nav-slam` 路 `nav2-integration` 路 `occupancy-map` 路 `unitree-g1` 路 `unitree-go2-sdk-skill` 路 `unitree-robot` 路 `go2-robot-control` 路 `robot-person-follow` 路 `face-checkin-robot` 路 `tour-checkin-follow` 路 `embodied-tour-nav` 路 `embodied-voice-stack` 路 `drone-cv-expert` 路 `deepstream-dev` 路 `kimodo-motion-diffusion` 路 `motion-control` 路 `spacemit-robot-vision` 路 鈥?
### 鍐呭鍒涗綔 / 鐭棰?/ 鐢靛晢 / 璇煶

`intelligent-content-system` 路 `content-creation-publisher` 路 `video-creation-suite` 路 `viral-video-copywriting` 路 `ecommerce-full-pipeline` 路 `infinitetalk` 路 `digital-avatar-shopping-video` 路 `tts-voice-synthesis` 路 `qwen3-tts-local` 路 `qwen3-asr-assistant` 路 `baoyu-*` 路 `wechat-hotspot-publisher` 路 `xiaohongshu-makeup` 路 鈥?
### 鍓嶇 / UI / 璁捐

`frontend-design` 路 `design-system` 路 `ui-design` 路 `ui-ux-pro-max` 路 `web-design-guidelines` 路 `figma-generate-design` 路 `canvas-design` 路 `mobile-app-ui-design` 路 `vercel-react-best-practices` 路 `nextjs-react-typescript` 路 `accessibility-a11y` 路 鈥?
### 鍚庣 / DevOps / 瀹夊叏

`fastapi-backend-template` 路 `backend-api-design` 路 `api-architect` 路 `mcp-builder` 路 `docker-patterns` 路 `multi-stage-dockerfile` 路 `kubernetes-deploying` 路 `ci-cd-and-automation` 路 `setting-up-ci` 路 `frontend-security` 路 `security-and-hardening` 路 `antinet-security-scan` 路 鈥?
### 鏁版嵁 / 閲戣瀺 / 鍔炲叕鏂囨。

`data-analysis` 路 `exploratory-data-analysis` 路 `financial-modeling` 路 `dcf-model` 路 `3-statement-model` 路 `stock-analysis` 路 `xlsx` 路 `docx` 路 `pdf` 路 `pptx` 路 `ppt-generator` 路 `meeting-notes` 路 `excel` 路 鈥?
### 鐭ヨ瘑浜ф潈锛堜笓鍒?/ 杞憲锛?
`patent-drafting` 路 `software-copyright-cn` 路 `contract-review` 路 `law-to-markdown`

### Agent 鍗忎綔涓庡伐绋嬫祦绋?
`agent-plan-mode` 路 `agent-team` 路 `agent-subagent-orchestration` 路 `agent-spec-creator` 路 `langgraph-coding-agent` 路 `spec-driven-development` 路 `test-driven-development` 路 `systematic-debugging` 路 `creating-pr` 路 `git-workflow-and-versioning` 路 `parallel-code-review` 路 `brainstorming` 路 `writing-plans` 路 鈥?
---

## Skill 缂栧啓绾﹀畾

鏂板鎴栦慨鏀?skill 鏃跺缓璁伒瀹堬細

1. **鐩綍鍚?* = skill `name`锛堝皬鍐欍€佺煭妯嚎锛?2. **`SKILL.md` 蹇呴渶**锛孻AML frontmatter 鑷冲皯鍖呭惈锛?
   ```yaml
   ---
   name: example-skill
   description: >-
     浣曟椂瑙﹀彂銆佸叧閿瘝銆侀€傜敤浠诲姟锛堜腑鑻卞潎鍙級銆?   ---
   ```

3. 姝ｆ枃鍐欐竻锛氱幆澧冧緷璧栥€佽緭鍏ヨ緭鍑恒€佸懡浠?API銆侀闄╀笌閫夊瀷瀵规瘮
4. 闀胯祫鏂欐斁 `references/`锛屽彲鎵ц閫昏緫鏀?`scripts/`
5. 鑻ユ湁涓婃父锛屽湪 `references/source.md` 鍐欐槑浠撳簱 / 璁烘枃 / License
6. 鎻愪氦鍓嶇‘璁ゆ棤 `.env`銆佸瘑閽ャ€佹湰鍦扮粷瀵硅矾寰勯殣绉?
鍙弬鑰冿細`writing-skills`銆乣building-skills-from-patterns`銆?
---

## 璐＄尞鎸囧崡

娆㈣繋 PR / Issue锛?
1. Fork 鏈粨搴撳苟鍩轰簬 `main` 寮€鍒嗘敮
2. 姣忎釜 PR 灏介噺鍙敼涓€涓?skill锛堟垨涓€缁勫己鐩稿叧 skill锛?3. 鏇存柊 `SKILL.md` 鏃跺悓姝ユ鏌?description 瑙﹀彂璇嶆槸鍚﹀噯纭?4. 鏂板 skill 鍚庢洿鏂?[`SKILLS.md`](./SKILLS.md)锛堟垨璇存槑鐢辩淮鎶よ€呬唬鏇达級
5. 涓嶈鎻愪氦锛歚node_modules/`銆佹潈閲嶆枃浠躲€佹暟鎹泦銆佸瘑閽?
Issue 寤鸿鍖呭惈锛歴kill 鍚嶃€佹湡鏈涜涓恒€佸鐜板璇濇憳瑕併€?
---

## 璁稿彲涓庡綊灞?
- **浠撳簱绾?*锛歁IT锛堣 [`LICENSE`](./LICENSE)锛?- **瀛愮洰褰?*锛氶儴鍒?skill 鑷甫 `LICENSE` / `LICENSE.txt`锛屼互鍏朵负鍑?- **鏉ユ簮绀轰緥**锛?  - 涓枃鍨傜洿鍚堥泦璺敱鍙傝€?[anbeime/skill](https://github.com/anbeime/skill)
  - 涓埆 skill 鍐?`references/source.md`锛堝 MegaFlow 鈫?[cvg/megaflow](https://github.com/cvg/megaflow)锛?
鍐嶅垎鍙戝瓙闆嗘椂璇蜂繚鐣欏搴斿瓙鐩綍鐨勮鍙笌褰掑睘淇℃伅銆?
---

## FAQ

**Q: Clone 鍚?Cursor 浠嶆壘涓嶅埌 skill锛?*  
A: 纭璺緞鏄惁涓?Cursor 瀹為檯鎵弿鐩綍锛涘繀瑕佹椂鍦ㄥ璇濅腑鏄惧紡鐐瑰悕 skill锛屾垨妫€鏌?Agent Stores 鏄惁鍙︽湁鍓湰銆?
**Q: 鍙互鍙閮ㄥ垎 skill 鍚楋紵**  
A: 鍙互銆傜敤绋€鐤忔鍑猴紝鎴栫洿鎺ュ鍒跺崟涓瓙鐩綍鍒?`~/.agents/skills/<name>/`銆?
**Q: 浠撳簱寰堝ぇ鍚楋紵**  
A: 绾︽暟鍗?MB 閲忕骇锛堜互鏂囨。涓庤剼鏈负涓伙級銆傚彲鐢?`--depth 1` 娴呭厠闅嗐€?
**Q: 涓?skills.sh / 瀹樻柟鍟嗗簵鏄粈涔堝叧绯伙紵**  
A: 鏈粨搴撴槸涓汉缁存姢鐨勫悎闆嗛暅鍍忥紝涓嶆浛浠ｅ畼鏂瑰晢搴楋紱鍙苟瀛橈紝鎸夊悕绉板幓閲嶅嵆鍙€?
---

## 甯哥敤鍛戒护閫熸煡

```bash
# 浠撳簱鐘舵€?git -C ~/.agents/skills status -sb

# 缁熻 skill 鏁?find ~/.agents/skills -mindepth 1 -maxdepth 1 -type d ! -name '.git' | wc -l

# 鎼滅储鍚煇鍏抽敭璇嶇殑 skill
rg -l "MegaFlow|鍏夋祦" ~/.agents/skills --glob 'SKILL.md'

# 鍒楀嚭鍏ㄩ儴鐩綍鍚?git -C ~/.agents/skills ls-tree -d --name-only HEAD
```

---

## 鐩稿叧閾炬帴

- 浠撳簱锛歨ttps://github.com/ZeroTokenClaw/agents-skills
- 瀹屾暣鐩綍锛歔`SKILLS.md`](./SKILLS.md)
- 鎬荤储寮曪細[`practical-skills-index/SKILL.md`](./practical-skills-index/SKILL.md)
- 涓枃鍨傜洿绱㈠紩锛歔`anbeime-skills-index/SKILL.md`](./anbeime-skills-index/SKILL.md)
- 绀惧尯鍙戠幇锛歔skills.sh](https://skills.sh/) 路 [anbeime/skill](https://github.com/anbeime/skill)
