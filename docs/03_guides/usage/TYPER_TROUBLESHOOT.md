Absolutely understandable—Typer is designed to make CLIs easier, but its flexibility can cause confusion, especially around command structure and entry points. Here are the **key concepts you need to know to confidently use Typer for CLI apps**:

---

## **Key Concepts for Typer CLI Apps**

### 1. **Single-Command vs Multi-Command Apps**
- **Single-Command CLI:**  
  - Use `@app.callback()` and set `invoke_without_command=True` in your `Typer()` app.
  - Users run your CLI with just options, e.g.:
    ```
    mycli --option1 foo --option2 bar
    ```
- **Multi-Command CLI:**  
  - Use `@app.command()` for each subcommand.
  - Users must specify a subcommand, e.g.:
    ```
    mycli subcommand --option1 foo
    ```

### 2. **How Typer Parses Arguments**
- **Positional arguments:**  
  - Defined as function parameters without a default value.
  - Called as: `mycli foo`
- **Options:**  
  - Defined using `typer.Option` (or a default value).
  - Called as: `mycli --option foo`

### 3. **Entry Points and Installation**
- In `pyproject.toml`, use `[project.scripts]` to expose your CLI as a command.
- The entry should point to your Typer app object, e.g.:
  ```
  mycli = "my_package.cli:app"
  ```
- After installing (`uv add -e .`), you can run `mycli` from anywhere.

### 4. **Help and Usability**
- Typer auto-generates help and usage from your function signatures and docstrings.
- Always provide clear `help=` text for every option and command.

### 5. **Common Pitfalls**
- **If you see `[OPTIONS] COMMAND [ARGS]...` in help:**  
  - Typer expects a subcommand. You likely need a single-command app structure.
- **If you see "Missing command":**  
  - You are running a multi-command CLI without specifying a subcommand.
- **If options aren’t recognized:**  
  - You may have defined them as positional arguments instead of options.

### 6. **Reinstallation is Required**
- Any time you change the CLI code or entry point, you must reinstall your package for changes to take effect.

### 7. **Testing and Debugging**
- Use `yourcli --help` to check the CLI structure.
- Run the CLI directly with `python path/to/your_script.py ...` to debug without reinstalling.

---

## **Summary Table**

| Use Case            | Decorator           | How to Call Example              | Typer App Creation                        |
|---------------------|---------------------|----------------------------------|-------------------------------------------|
| Single-command CLI  | `@app.callback()`   | `mycli --foo bar`                | `Typer(invoke_without_command=True)`      |
| Multi-command CLI   | `@app.command()`    | `mycli subcmd --foo bar`         | `Typer()`                                 |

---

## **Why Typer Can Feel Convoluted**

- Typer tries to be both simple and flexible (single- and multi-command).
- The distinction between callback and command, and the need for `invoke_without_command=True`, is subtle but crucial.
- Python packaging/entry points add another layer of complexity.

---

## **If You Remember Only Three Things:**

1. **For a CLI with only options, use `@app.callback()` and `Typer(invoke_without_command=True)`.**
2. **For a CLI with subcommands, use `@app.command()` for each, and always specify a subcommand on the command line.**
3. **Always reinstall your package after changing CLI code or entry points.**

---

**You are not alone—many find these details confusing at first!**  
Once you internalize these core concepts, Typer becomes much more predictable and powerful.

---
Answer from Perplexity: pplx.ai/share