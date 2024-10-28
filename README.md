## Thinga

![GitHub repo status](https://img.shields.io/badge/status-active-green?style=flat)
![GitHub license](https://img.shields.io/github/license/sheikhartin/thinga)
![GitHub contributors](https://img.shields.io/github/contributors/sheikhartin/thinga)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/sheikhartin/thinga)
![GitHub repo size](https://img.shields.io/github/repo-size/sheikhartin/thinga)

Compare and vote for the option you want to get a better rating!

### How to Use

Install [uv](https://github.com/astral-sh/uv) ("An extremely fast Python package and project manager, written in Rust."):

| macOS and Linux                                    | Windows                                                                               | Using pip        |
|----------------------------------------------------|---------------------------------------------------------------------------------------|------------------|
| `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` | `pip install uv` |

To develop and contribute, install these tools:

- [Ruff](https://pypi.org/project/ruff/)
- [Pytest](https://pypi.org/project/pytest/)

Or run this code on your Unix-like operating system:

```bash
tools=(ruff pytest)
for tool in "${tools[@]}"; do
  uv tool install --force "${tool}"@latest
done
```

Make sure the tests pass before running the server:

```
pytest -rSp
```

Run the Thinga web application:

```
uv run uvicorn thinga.main:app --port 9906
```

Now go to http://127.0.0.1:9906 and use it!

The front-end codebase for this project is available on [GitHub](https://github.com/sheikhartin/thinga-website).

#### Automation Scripts

Collect images from DuckDuckGo based on a query easily:

```
uv run python scripts/image_collector.py 'Hollywood celebrities' --max-images 15
```

Upload collected images to the Thinga API:

```
./scripts/upload_collected_images.sh -u root -p toor
```

### License

This project is licensed under the MIT license found in the [LICENSE](LICENSE) file in the root directory of this repository.
