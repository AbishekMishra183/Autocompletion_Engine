
**Author:** Abhishek Mishra
**Language:** Vanilla JavaScript (ES6+) · HTML5 · CSS3
**Delivery:** Single-file web app — open in any browser, zero install
**Data Structures:** Trie (Prefix Tree) · HashMap (Catalogue) · Comparison Sort

---

## Table of Contents

1. [What This Project Does](#1-what-this-project-does)
2. [How to Run](#2-how-to-run)
3. [File Structure](#3-file-structure)
4. [System Architecture — The Big Picture](#4-system-architecture--the-big-picture)
5. [Deep Dive — Each Class Explained](#5-deep-dive--each-class-explained)
   - 5.1 [TrieNode — The Building Block](#51-trienode--the-building-block)
   - 5.2 [Trie — The Prefix Tree](#52-trie--the-prefix-tree)
   - 5.3 [Catalogue — The Metadata Store](#53-catalogue--the-metadata-store)
   - 5.4 [AutocompleteEngine — The Brain](#54-autocompleteengine--the-brain)
   - 5.5 [UI Controller — The Interface](#55-ui-controller--the-interface)
6. [Data Structure Choice — Why Trie?](#6-data-structure-choice--why-trie)
7. [Ghost Text Feature](#7-ghost-text-feature)
8. [All Four Rules — Where They Live](#8-all-four-rules--where-they-live)
9. [Code Flow — Step by Step](#9-code-flow--step-by-step)
10. [Complete Complexity Analysis](#10-complete-complexity-analysis)
11. [The 40 Preloaded Phrases](#11-the-40-preloaded-phrases)
12. [Architecture Decisions — Why Not Something Else?](#12-architecture-decisions--why-not-something-else)

---

## 1. What This Project Does

This is a **browser-based Autocomplete Engine** — the same mechanism that powers search suggestions on Google, YouTube, and VS Code.

You type a few letters. The engine finds every phrase in its catalogue that starts with those letters, ranks them by how often they have been searched, and shows you the top 5 — all in real time, updating on every single keystroke.

**The four rules it enforces, always:**

| # | Rule |
|---|---|
| 1 | Show the top 5 suggestions that start with the current prefix |
| 2 | If two phrases have the same search count, rank them alphabetically |
| 3 | Selecting a suggestion adds 1 to its count — rankings change live |
| 4 | Typing a phrase that does not exist and pressing Enter adds it with count = 1 |

**What makes it feel polished:**

- Ghost text preview — the top suggestion appears as grey text inside the input, opt-in via Tab
- Dropdown with popularity bars showing relative search counts
- Live activity log and running statistics
- Full keyboard navigation — Tab, →, Enter, Escape all behave intuitively

---

## 2. How to Run

No server. No dependencies. No install.

```
Open  autocomplete_web.html  in any modern browser.
```

That is the entire setup. Everything — data structures, ranking logic, UI, styles — lives inside that one file.

---

## 3. File Structure

```
autocomplete_engine/
│
└── autocomplete_web.html     The complete application
                              ├── <style>   — all CSS, fonts, layout, ghost text
                              ├── <body>    — search card, dropdown, stats panel
                              └── <script>  — four JS classes + UI controller
                                    ├── class TrieNode          (the atom)
                                    ├── class Trie              (prefix search)
                                    ├── class Catalogue         (count tracking)
                                    ├── class AutocompleteEngine (wires all three)
                                    └── UI Controller           (DOM + events)
```

The JavaScript inside `autocomplete_web.html` is structured as four distinct classes — each with a single responsibility — plus a UI controller that wires them to the DOM. The class boundaries mirror what a production multi-file project would look like; they are just co-located for zero-dependency delivery.

---

## 4. System Architecture — The Big Picture

Think of the autocomplete engine as a **very smart library**.

When you type letters into the search bar, the engine does not read every book on every shelf. It walks straight to the correct section, grabs every book in that section, picks the 5 most popular, and hands them to you — in milliseconds.

Four "staff members" (classes) work together:

```
You type "ma"
     │
     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         THE LIBRARY                                 │
│                                                                     │
│  🧱 class TrieNode         — One shelf label (one letter per shelf) │
│  📚 class Trie             — The shelving system (finds the section)│
│  📋 class Catalogue        — The librarian's notebook (counts)      │
│  🧠 class AutocompleteEngine — The head librarian (runs everything) │
└─────────────────────────────────────────────────────────────────────┘
     │
     ▼
Renders: machine learning roadmap (810), microservices architecture (500) ...
```

The UI Controller sits outside these four and is responsible only for reading DOM events and painting results — it contains zero business logic.

---

## 5. Deep Dive — Each Class Explained

---

### 5.1 TrieNode — The Building Block

**What it is in plain terms:**
One junction on a road map. Every road out of this junction is labelled with a single character. Follow the roads and you spell out a word.

**The code:**

```javascript
class TrieNode {
  constructor() {
    this.children        = {};     // { 'a': TrieNode, 'p': TrieNode, ... }
    this.isEndOfPhrase   = false;  // true when a complete phrase ends here
    this.originalPhrase  = null;   // stores the full phrase text at end nodes
  }
}
```

**Why each field exists:**

| Field | Why it's there | What breaks if we remove it |
|---|---|---|
| `children` | Maps one character to the next node — the edges of the tree | Without it there is no tree; navigation is impossible |
| `isEndOfPhrase` | Marks where a phrase ends | Without it we cannot tell `"dat"` (just a prefix) from `"data"` (a real phrase) |
| `originalPhrase` | Stores the full phrase text at the end node | Without it we'd have to reconstruct the phrase by walking back up the tree — requires parent pointers and is significantly slower |

**Alternative representations considered:**

- Plain tuple `[children, isEnd, phrase]` — works but unreadable and error-prone
- Store count on the node itself — couples ranking logic into the tree structure, violates Single Responsibility
- Flat dictionary `{ phrase: count }` — fine for storage, but cannot do prefix search efficiently (see section 6)

The chosen class approach is the standard representation for Trie nodes and maps directly to how the data structure is taught and implemented in production systems.

---

### 5.2 Trie — The Prefix Tree

**What it is in plain terms:**
The entire shelving system. It knows how to store a phrase and how to instantly locate every phrase that starts with what you typed.

**Visual — what the Trie looks like in memory:**

```
After inserting "data", "dark", "day", "javascript":

        root
         ├── 'd'
         │    └── 'a'
         │         ├── 't' ── 'a'  ← [END: "data"]
         │         ├── 'r' ── 'k'  ← [END: "dark"]
         │         └── 'y'         ← [END: "day"]
         └── 'j'
              └── 'a' ── 'v' ── 'a' ── 's' ── 'c' ── 'r' ── 'i' ── 'p' ── 't'
                                                                              ↑
                                                                    [END: "javascript"]
```

Notice how `"data"`, `"dark"`, and `"day"` all share the path `root → d → a`. That shared path is what makes prefix search efficient — you walk to the `"da"` node once and then collect everything below it, without touching `"javascript"` at all.

---

#### `insert(phrase)` — O(m) time

```javascript
insert(phrase) {
  let node = this.root;
  for (const ch of phrase.toLowerCase()) {   // go letter by letter
    if (!node.children[ch])
      node.children[ch] = new TrieNode();    // create if missing
    node = node.children[ch];               // walk one step deeper
  }
  node.isEndOfPhrase  = true;
  node.originalPhrase = phrase;
}
```

**Step by step inserting "data":**
1. Start at root
2. `'d'` → create node for `d`, move there
3. `'a'` → create node for `a`, move there
4. `'t'` → create node for `t`, move there
5. `'a'` → create node for `a`, move there
6. Mark this last node: `isEndOfPhrase = true`, `originalPhrase = "data"`

Time cost: O(m) where m is the number of characters. You visit or create exactly one node per character and never revisit.

---

#### `searchByPrefix(prefix)` — O(m + k) time

```javascript
searchByPrefix(prefix) {
  let node = this.root;

  // Phase 1: walk to where the prefix ends — O(m)
  for (const ch of prefix.toLowerCase()) {
    if (!node.children[ch]) return [];   // prefix does not exist
    node = node.children[ch];
  }

  // Phase 2: collect every phrase in the subtree below — O(k)
  const results = [];
  this._depthFirstCollect(node, results);
  return results;
  // Returns ALL matches, unranked. Ranking is the Engine's job.
}
```

**Searching for prefix `"da"` — step by step:**
1. Start at root
2. Walk to `'d'` node
3. Walk to `'a'` node ← we are now at the end of the prefix `"da"`
4. DFS downward from `'a'`, collecting end-nodes: `"data"`, `"dark"`, `"day"`
5. Return `["data", "dark", "day"]` — unranked, the Engine sorts them

**Why O(m + k) and not O(N)?**
The Trie physically separates phrases by their prefixes into different subtrees. When you search for `"da"`, the structure of the tree means you can never even reach the `"javascript"` subtree — it is in a completely different branch. You only visit nodes that are relevant.

---

#### `_depthFirstCollect(node, results)` — the DFS traversal

```javascript
_depthFirstCollect(node, results) {
  if (node.isEndOfPhrase) results.push(node.originalPhrase);
  for (const child of Object.values(node.children))
    this._depthFirstCollect(child, results);
}
```

Standard recursive DFS. It visits every node in the subtree exactly once.

Layman analogy: exploring every corridor in a building, starting from one floor. Whenever you find a door marked `EXIT`, write down that room number. Keep going until every corridor has been explored.

**Why DFS and not BFS?**
Both give O(k) and find all results correctly. DFS uses the call stack implicitly, requiring no extra data structure. BFS needs an explicit queue. For this use case they are equivalent in performance; DFS requires fewer lines of code.

---

### 5.3 Catalogue — The Metadata Store

**What it is in plain terms:**
A notebook the librarian keeps. For every phrase, it records the exact display text and how many times it has been searched. The Trie tells you where phrases live. The Catalogue tells you what you know about them.

**Why keep them separate?**

| Question | Answered by |
|---|---|
| "Does anything start with `'machine'`?" | Trie |
| "How popular is `'machine learning roadmap'`?" | Catalogue |
| "How do I display the phrase with correct casing?" | Catalogue |

If we stored counts inside TrieNode itself:
- Incrementing a count would require navigating the Trie — O(m) — instead of O(1)
- The Trie would be responsible for two different concerns (prefix structure and count tracking), violating the Single Responsibility Principle
- Testing and debugging each concern independently would be harder

**The internal store:**

```javascript
this._store = Object.create(null);
// key   = "machine learning roadmap"   (lowercase, for O(1) lookup)
// value = { phrase: "machine learning roadmap", count: 810 }
```

**Why lowercase keys?**
So that `"Machine Learning"` and `"machine learning"` both find the same entry without any extra logic at query time. Case is preserved in the `phrase` field for display; only the lookup key is normalised.

**`incrementCount(phrase)` — O(1):**

```javascript
incrementCount(phrase) {
  const key = phrase.toLowerCase().trim();
  if (this._store[key]) {
    this._store[key].count++;
    return this._store[key].count;
  }
  return 0;
}
```

This is O(1) because JavaScript objects use hash-based property lookup. The key is hashed, the bucket is accessed directly — no scanning of other entries.

**What if we used a sorted array instead of an object?**
Lookup would be O(log N) with binary search, and insertion would be O(N) due to shifting. For a catalogue being incremented many times per second, the hash-based object is dramatically faster.

---

### 5.4 AutocompleteEngine — The Brain

**What it is in plain terms:**
The head librarian who coordinates everything. When you ask for suggestions, it asks the shelving system (Trie) for all matching phrases, checks the notebook (Catalogue) for each phrase's popularity, picks the 5 most popular, and returns them to you.

---

#### `getSuggestions(prefix)` — Rules 1 and 2

```javascript
getSuggestions(prefix) {
  prefix = prefix.trim();
  if (!prefix) return [];

  // Step 1: Trie finds ALL phrases matching the prefix — O(m + k)
  const raw = this._trie.searchByPrefix(prefix);
  if (!raw.length) return [];

  // Step 2: Sort by count DESC, then alphabetically for ties — O(k log k)
  raw.sort((a, b) => {
    const diff = this._catalogue.getCount(b) - this._catalogue.getCount(a);
    return diff !== 0 ? diff : a.toLowerCase().localeCompare(b.toLowerCase());
  });

  // Step 3: Return top 5 with display phrase and count — O(1)
  return raw.slice(0, TOP_N).map(p => ({
    phrase: this._catalogue.getDisplay(p),
    count:  this._catalogue.getCount(p)
  }));
}
```

**The tiebreaker — Rule 2:**
The sort comparator first compares counts (descending). When two phrases have identical counts, `diff` is zero and JavaScript falls through to `localeCompare`, which sorts alphabetically. This is Rule 2 implemented in a single expression.

**Why not a Min-Heap for the top-5 extraction?**
A min-heap of size 5 would give O(k log 5) ≈ O(k) — slightly better than O(k log k) for sort. However, with a maximum catalogue of a few thousand phrases, k is never large enough for this difference to be measurable. The sort approach is simpler, more readable, and correct. A heap would be the right choice at scale (millions of phrases).

---

#### `selectSuggestion(phrase)` — Rule 3

```javascript
selectSuggestion(phrase) {
  return this._catalogue.incrementCount(phrase);  // O(1)
}
```

One line. The Catalogue handles the increment. The Engine delegates. The next call to `getSuggestions` for the same prefix will reflect the updated count, so rankings change live as you use the engine.

---

#### `submitPhrase(phrase)` — Rule 4

```javascript
submitPhrase(phrase) {
  phrase = phrase.trim();
  if (!phrase) return null;

  if (!this._catalogue.exists(phrase)) {
    this._catalogue.add(phrase, 1);    // O(1)
    this._trie.insert(phrase);         // O(m)
    return { status: 'added', count: 1 };
  }
  return { status: 'incremented', count: this._catalogue.incrementCount(phrase) };
}
```

New phrases must be inserted into **both** the Trie and the Catalogue:
- Insert into Catalogue only → the phrase has a count but never appears in autocomplete results
- Insert into Trie only → the phrase appears in results but with no count data and no display text

Both insertions are required. They serve different responsibilities.

---

### 5.5 UI Controller — The Interface

The UI Controller is the only part of the code that touches the DOM. It contains no business logic. Its only job is to translate user events into Engine calls, and Engine results into rendered HTML.

**The search input and dropdown:**

```
User types a character
  → 'input' event fires
  → ghostArmed is reset to false (user is typing their own phrase)
  → renderDropdown(inputValue) is called
  → engine.getSuggestions(prefix) is called
  → Results are rendered as suggestion rows with popularity bars
  → setGhostText() is called if ghost is armed
```

**Keyboard shortcuts handled:**

| Key | Behaviour |
|---|---|
| Any character | Triggers live suggestion update |
| `Tab` (first press) | Arms ghost preview — shows top suggestion as grey text |
| `Tab` (second press) or `→` at end | Accepts ghost — fills input with top suggestion |
| `Enter` | Saves exactly what the user typed — never auto-selects a suggestion |
| `Escape` | If ghost is armed, dismisses ghost. Otherwise closes dropdown. |
| Mouse click on suggestion | Selects that suggestion and increments its count |

**Why Enter does not auto-select the top suggestion:**
The engine is designed to respect user intent. When a user types `"data"` and presses Enter, they want to save the phrase `"data"` — not have the engine replace it with `"data structures and algorithms"`. Ghost text (Tab) is the deliberate, opt-in path to accepting a suggestion. Enter is always the user's own phrase.

**The stats panel:**

Three live counters update on every action:
- Total phrases — the size of the full catalogue including newly added phrases
- Searches done — how many times a suggestion has been selected
- New phrases — how many phrases have been added by the user during this session

**The activity log:**

A rolling log of the last six actions with timestamps, showing whether each action was a selection, a count increment, or a new phrase being added.

---

## 6. Data Structure Choice — Why Trie?

### The Problem

Every time the user types a character, the engine must find all phrases starting with the current input — and do it fast enough that the result appears before the user types the next character.

### Alternatives Considered

**Option A — Plain Array**

```javascript
// Find all phrases starting with "ma"
const results = allPhrases.filter(p => p.toLowerCase().startsWith(prefix));
```

| Property | Detail |
|---|---|
| Prefix search | O(N × m) — scans every phrase on every keystroke |
| Space | O(N) — simple |
| Add new phrase | O(1) — fast |
| Verdict | ❌ Catastrophically slow at scale |

At 10,000 phrases and typing 10 characters per second, this performs 100,000 string comparisons per second just for one user.

---

**Option B — Sorted Array + Binary Search**

Sort the catalogue alphabetically. Use binary search to find the start of the matching prefix range.

| Property | Detail |
|---|---|
| Prefix search | O(log N + k) — better |
| Space | O(N) |
| Add new phrase | O(N) — must re-sort after every insertion |
| Verdict | ⚠️ Acceptable for read-only catalogues; unusable when users can add phrases |

---

**Option C — Hash Map / Dictionary**

```javascript
const store = { "machine learning": 840, "python tutorial": 1100, ... };
```

Hash maps are designed for exact-key lookup in O(1). They have no concept of prefix — to find all keys starting with `"ma"` you must iterate every key and call `.startsWith()`, which is O(N × m). This is identical to the plain array.

| Property | Detail |
|---|---|
| Prefix search | O(N × m) — same as array |
| Exact lookup | O(1) — excellent |
| Verdict | ❌ Wrong tool for prefix matching |

The Catalogue in this project uses a HashMap, but only for count tracking (exact lookups). It delegates all prefix matching to the Trie.

---

**Option D — Trie ✅ Our Choice**

| Property | Detail |
|---|---|
| Prefix search | O(m + k) — walk the prefix, collect results below |
| Space | O(total characters, with prefix sharing) |
| Add new phrase | O(m) — follow or create one node per character |
| Verdict | ✅ Purpose-built for autocomplete |

**Why the Trie wins:**

1. Prefix search is O(m + k) regardless of how many total phrases exist. Whether the catalogue has 40 phrases or 4 million, searching for `"ma"` costs the same: walk 2 nodes, collect matches below.
2. Shared prefixes save space. `"machine learning tutorial"` and `"machine learning roadmap"` share the nodes `m → a → c → h → i → n → e → (space) → l → e → a → r → n → i → n → g → (space)` — 17 nodes shared between two phrases.
3. Insertion is O(m) — fast even when users add new phrases in real time.
4. No sorting or re-indexing needed when phrases are added.

---

## 7. Ghost Text Feature

Ghost text is the grey completion preview that appears inside the search input, identical in style to how VS Code and modern IDEs show inline completions.

### How It Works

The ghost is implemented as an absolutely-positioned `<div>` that sits on top of the `<input>` element, pixel-aligned using identical font, size, padding, and border settings.

```
Input layer (z-index: 1):    [sys________________]   ← user types here
Ghost layer (z-index: 0):    [sys]tem design interview]  ← overlay

Visual result the user sees:  sys|tem design interview
                               ^^^  ^^^^^^^^^^^^^^^^^^^
                             real        grey ghost
```

The ghost div contains two spans:
- `ghost-match` — contains the characters the user already typed, rendered in `color: transparent` so it takes up exactly the right space but is invisible
- `ghost-tail` — contains the remaining characters of the top suggestion, rendered in grey with 55% opacity

This alignment trick means the grey text appears to extend directly from the user's cursor without any offset.

### The Two-Step Opt-In Design

Ghost text is **never shown automatically** while the user is typing. It requires deliberate opt-in:

| Action | Effect |
|---|---|
| Type normally | No ghost. The dropdown shows suggestions but the input is untouched. |
| Press `Tab` (first time) | Ghost preview arms and appears — the top suggestion shows as grey text |
| Press `Tab` again or press `→` at end of input | Ghost is accepted — the full suggestion fills the input |
| Press `Escape` | Ghost is dismissed — the user's typed prefix remains |
| Type any character | Ghost is immediately disarmed and cleared |

**Why opt-in and not automatic?**
Automatic ghost text caused the core user frustration: typing `"data"` would show `"data structures and algorithms"` as ghost, and Tab or Enter would replace the intended phrase with the suggestion. The two-step approach means ghost text is always an explicit user choice, never an unwanted side-effect.

---

## 8. All Four Rules — Where They Live

| Rule | Class | Method | How |
|---|---|---|---|
| Top 5 suggestions matching prefix | `AutocompleteEngine` | `getSuggestions()` | Trie collects all, sort + slice to 5 |
| Ties ranked alphabetically | `AutocompleteEngine` | `getSuggestions()` | `localeCompare` tiebreaker in sort comparator |
| Select suggestion → count +1 | `AutocompleteEngine` → `Catalogue` | `selectSuggestion()` → `incrementCount()` | O(1) HashMap update |
| Unknown phrase + Enter → add with count 1 | `AutocompleteEngine` | `submitPhrase()` | Insert into both Trie and Catalogue |

---

## 9. Code Flow — Step by Step

### Scenario A — User types a prefix

```
User types "sys"
  → 'input' event fires on the search input
  → ghostArmed is reset to false
  → renderDropdown("sys") is called
  → engine.getSuggestions("sys") is called
      → trie.searchByPrefix("sys")
          → walk: root → s → y → s
          → DFS collect below: ["system design interview"]
          → return ["system design interview"]
      → catalogue.getCount("system design interview") → 920
      → sort (only one result, no sorting needed)
      → return [{ phrase: "system design interview", count: 920 }]
  → Dropdown renders 1 suggestion row with popularity bar
  → ghost text is NOT shown (ghostArmed is false)
```

---

### Scenario B — User opts into ghost text

```
User has typed "sys", top suggestion is "system design interview"
User presses Tab (first time)
  → ghostArmed is set to true
  → setGhostText("sys", { phrase: "system design interview" })
      → matchPart = "sys"                  → ghost-match span (transparent)
      → tailPart  = "tem design interview" → ghost-tail span (grey)
  → Ghost hint badge appears: "Tab or → to accept"

User presses Tab again
  → acceptGhost() is called
  → searchInput.value = "system design interview"
  → ghostArmed = false, ghost cleared
  → renderDropdown("system design interview") refreshes the dropdown
```

---

### Scenario C — User selects a suggestion by clicking

```
User clicks on "system design interview"
  → handleSelect(0) is called
  → engine.selectSuggestion("system design interview")
      → catalogue.incrementCount("system design interview")
          → store["system design interview"].count++   → 921
          → return 921
  → Log: "Selected 'system design interview' — count 920 → 921"
  → Status bar: "✓ count is now 921"
  → renderCatalogue() — catalogue panel re-renders with updated rank
  → Input is filled with the selected phrase and highlighted
```

---

### Scenario D — User adds a brand-new phrase

```
User types "blockchain for beginners" (not in catalogue)
  → renderDropdown("blockchain for beginners")
      → trie.searchByPrefix("blockchain for beginners") → []
      → No suggestions — dropdown shows: "No matches — press Enter to add"
      → clearGhostText() (no suggestions means no ghost possible)

User presses Enter
  → handleEnter() is called
  → engine.submitPhrase("blockchain for beginners")
      → catalogue.exists("blockchain for beginners") → false
      → catalogue.add("blockchain for beginners", 1)
      → trie.insert("blockchain for beginners")
          → Creates nodes: b→l→o→c→k→c→h→a→i→n→(space)→...→s
          → End node: isEndOfPhrase=true, originalPhrase="blockchain for beginners"
      → return { status: "added", count: 1 }
  → Log: "Added 'blockchain for beginners' with count 1"
  → Status: "✓ New phrase added"
  → Input cleared, catalogue size counter increments to 41
```

---

## 10. Complete Complexity Analysis

### Time Complexity

| Operation | Time | Notes |
|---|---|---|
| Insert a phrase | O(m) | m = phrase length. One node visited or created per character. |
| Prefix search — Trie walk | O(m) | Walk from root to the prefix end node. |
| Prefix search — DFS collect | O(k) | k = total characters across all matching phrases in subtree. |
| **Full prefix search** | **O(m + k)** | Dominant combined cost. Independent of catalogue size N. |
| Sort matches for ranking | O(k log k) | Sort all k matches before slicing to top 5. |
| Slice top 5 | O(1) | After sort, slicing is constant time. |
| **Full getSuggestions** | **O(m + k log k)** | Search + sort combined. |
| Increment count — Rule 3 | O(1) | HashMap direct key access. |
| Add new phrase — Rule 4 | O(m) | Trie insert dominates; Catalogue add is O(1). |
| Render catalogue sorted | O(N log N) | Full sort of catalogue for the display panel only. |

**Why O(m + k) beats O(N × m) — the numbers:**

If the catalogue has 1,000,000 phrases and the user types 4 characters:

| Approach | Operations |
|---|---|
| Plain array scan | 1,000,000 × 4 = **4,000,000** comparisons |
| Trie | Walk 4 nodes + collect k matches = **4 + k** operations |

If only 3 phrases start with that 4-character prefix, the Trie does 7 operations. The array does 4,000,000.

---

### Space Complexity

| Component | Space | Notes |
|---|---|---|
| Trie — worst case | O(N × m) | If no two phrases share any prefix characters |
| Trie — typical case | Less than O(N × m) | Shared prefixes reduce total node count significantly |
| Catalogue (HashMap) | O(N) | One record per phrase |
| DFS result buffer | O(k) | Temporary, freed after each search |
| Top-5 slice | O(5) = O(1) | Bounded constant |
| **Total** | **O(N × m) worst** | Trie dominates; prefix sharing reduces this in practice |

**Shared prefix savings example:**
`"machine learning tutorial"` and `"machine learning roadmap"` share 17 characters (`machine learning `). In a flat array, those 17 characters are stored twice. In the Trie, they are stored once — a shared path to the space node after `"learning"`, then two separate branches from there onward.

---

## 11. The 40 Preloaded Phrases

These phrases are pre-loaded into both the Trie and the Catalogue at startup, with varying search counts designed to demonstrate ranking, tiebreaking, and prefix overlap.

| Rank | Phrase | Search Count |
|---|---|---|
| 1 | data structures and algorithms | 1,200 |
| 2 | artificial intelligence trends | 980 |
| 3 | system design interview | 920 |
| 4 | best python libraries 2024 | 870 |
| 5 | machine learning roadmap | 810 |
| 6 | how to learn javascript | 730 |
| 7 | javascript async await | 690 |
| 8 | react hooks tutorial | 660 |
| 9 | natural language processing | 620 |
| 10 | cloud computing services | 650 |
| 11 | git branching strategies | 560 |
| 12 | deep learning with tensorflow | 540 |
| 13 | sql joins explained | 590 |
| 14 | microservices architecture | 500 |
| 15 | nodejs express rest api | 470 |
| 16 | css grid layout tutorial | 480 |
| 17 | kubernetes deployment guide | 450 |
| 18 | docker container tutorial | 410 |
| 19 | best machine learning courses | 760 |
| 20 | artificial neural networks | 420 |
| 21 | java spring boot tutorial | 385 |
| 22 | object oriented programming | 380 |
| 23 | binary search tree tutorial | 340 |
| 24 | sorting algorithms comparison | 340 |
| 25 | dynamic programming problems | 330 |
| 26 | graph traversal algorithms | 300 |
| 27 | algorithm time complexity | 310 |
| 28 | vector databases explained | 310 |
| 29 | blockchain technology overview | 290 |
| 30 | redis caching strategies | 290 |
| 31 | apple macbook pro review | 275 |
| 32 | linear regression explained | 260 |
| 33 | typescript generics guide | 255 |
| 34 | competitive programming tips | 220 |
| 35 | open source contribution guide | 215 |
| 36 | hash map vs hash set | 195 |
| 37 | autocomplete engine design | 190 |
| 38 | prefix tree trie implementation | 175 |
| 39 | trie vs hash map performance | 140 |
| 40 | python list comprehension | 710 |

**Phrases designed to demonstrate specific rules:**

- `"blockchain technology overview"` (290) and `"redis caching strategies"` (290) — identical counts, so `"blockchain"` ranks above `"redis"` alphabetically. This is Rule 2 in action.
- `"algorithm time complexity"` (310) and `"vector databases explained"` (310) — identical counts, `"algorithm"` ranks above `"vector"` alphabetically. Rule 2 again.
- Typing `"a"` returns five results ranked by count: `"artificial intelligence trends"` (980) first, then `"algorithm time complexity"` (310), `"artificial neural networks"` (420), `"autocomplete engine design"` (190), `"apple macbook pro review"` (275) — demonstrating both count ranking and tiebreaking within a single prefix.

---

## 12. Architecture Decisions — Why Not Something Else?

**Could we do it all in one function, no classes?**
Yes, but debugging a count bug would mean searching through Trie navigation code and UI rendering code simultaneously. Separate classes mean each concern has one place, one test surface, and one owner. The class boundaries also make it trivial to replace one component — swap the Catalogue for a Redis-backed version, for example — without touching the others.

**Could we use a database instead of in-memory structures?**
In a production deployment, yes — Redis sorted sets are a natural fit for the ranking layer, and a persistent Trie stored in a database handles the prefix layer. The Engine class would simply swap its data sources. The Trie and Catalogue classes would remain identical; only their constructors would change to point at external stores.

**Could we use a regular JavaScript object for prefix search instead of a Trie?**
An object gives O(1) for exact key lookups only. To find all keys starting with `"ma"` you must call `Object.keys()` — O(N) — and then filter with `.startsWith()` — O(N × m) total. The Trie gives O(m + k) regardless of N. The Catalogue uses a plain object because it only ever needs exact lookups; the Trie is used for prefix matching specifically because the object cannot do it efficiently.

**Why not keep counts inside the Trie nodes instead of a separate Catalogue?**
Three reasons. First, incrementing a count would cost O(m) — a full Trie walk — instead of O(1). Second, the Trie's responsibility is prefix structure; embedding count management violates Single Responsibility and makes the code harder to reason about. Third, querying the full sorted catalogue for the stats panel would require a complete DFS of the entire Trie, versus a simple `Object.values().sort()` on the Catalogue.

**Why a single HTML file instead of separate JS/CSS/HTML files?**
Zero-dependency delivery. Anyone can download one file and open it. No build step, no npm, no server, no module bundler. For a project whose requirement is "open in any browser", a single self-contained file is the correct architecture — not a compromise of it.

---

