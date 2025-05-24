To manage and target multiple background Claude Code instances in tmux, you need a systematic way to launch, name, and reference each session. Here’s a recommended approach for your use case:

---

## 1. **Launch 8 Named tmux Sessions with Claude Code**

Give each session a unique, predictable name (e.g., `claude1`, `claude2`, ..., `claude8`). This makes it easy to reference them later.

**Example Bash loop:**
```bash
for i in {1..8}; do
  tmux new-session -d -s claude$i 'claude --dangerously-skip-permissions'
done
```
- `-d` launches detached (in the background).
- `-s claude$i` gives each session a unique name.

---

## 2. **Store or Track Session Names**

- **Static naming:** If you use a naming scheme like `claude1` to `claude8`, you always know how to target each instance.
- **Dynamic tracking:** If you want to automate or scale, store session names in a file or array as you launch them.

**Example:**
```bash
CLAUDE_SESSIONS=()
for i in {1..8}; do
  SESSION="claude$i"
  tmux new-session -d -s $SESSION 'claude --dangerously-skip-permissions'
  CLAUDE_SESSIONS+=($SESSION)
done
# Now CLAUDE_SESSIONS contains all your session names.
```

---

## 3. **Target a Specific Instance to Send a Command**

Use `tmux send-keys` with the session name:
```bash
tmux send-keys -t claude3 "your prompt here" C-m
```
This sends your command to the third Claude instance.

---

## 4. **Scaling Up: Polling a Task Queue**

For each Claude instance to poll a task queue, you need a mechanism inside each tmux session that:
- Periodically checks for new tasks (e.g., via a script or a loop).
- Sends the task to Claude Code for processing.

**Options:**
- **Manual:** You send prompts via `tmux send-keys` as needed.
- **Automated:** Use a wrapper script that runs inside each tmux session, which:
  - Launches Claude Code.
  - Monitors a shared queue (e.g., a file, database, or message queue).
  - Sends tasks to Claude as they appear.

---

## 5. **Listing and Managing Sessions**

To see all running sessions:
```bash
tmux ls
```
To attach to a session (for debugging or output):
```bash
tmux attach -t claude3
```
To detach:  
`Ctrl+b` then `d`[1][2][5].

---

## **Summary Table**

| Task                        | Command/Method                                            |
|-----------------------------|----------------------------------------------------------|
| Launch 8 sessions           | `tmux new-session -d -s claude1 'claude ...'` (repeat)   |
| Store session names         | Use predictable names or a Bash array                    |
| Send command to instance    | `tmux send-keys -t claudeN "command" C-m`               |
| List sessions               | `tmux ls`                                                |
| Attach/detach               | `tmux attach -t claudeN` / `Ctrl+b d`                   |

---

**Recommendation:**  
Use a static, predictable naming scheme for your tmux sessions (`claude1` to `claude8`). This makes it trivial to target any instance from scripts or the terminal. For advanced automation, wrap Claude Code in a script that polls a shared queue, or orchestrate task delivery with `tmux send-keys` from a central dispatcher script[1][2][5].

Citations:
[1] https://www.hostmycode.in/tutorials/use-tmux-for-managing-multiple-server-sessions
[2] https://ostechnix.com/tmux-command-examples-to-manage-multiple-terminal-sessions/
[3] https://superuser.com/questions/845427/tmux-multiple-instances-of-the-same-session
[4] https://www.reddit.com/r/tmux/comments/d22l3x/single_client_multiple_tmux_servers/
[5] https://joshmedeski.com/posts/manage-terminal-sessions-with-tmux/
[6] https://zolmok.org/tmux-multiple-projects-sessions/
[7] https://unix.stackexchange.com/questions/282365/using-multiple-terminal-x-windows-with-one-tmux-session
[8] https://www.sglavoie.com/posts/2021/09/19/managing-multiple-tmux-sessions-at-once/

---
Answer from Perplexity: pplx.ai/share