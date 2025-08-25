````markdown
# BitBot
Event-driven, modular IRC bot for Python 3.

---

## Quick start (Linux/macOS)

### 0) System prerequisites
- Python **3.11+** (tested on **3.13**)
- Git
- Build tools only if wheels aren’t available:
  - **Fedora/RHEL**: `sudo dnf install -y gcc python3-devel libxml2-devel libxslt-devel pkgconf-pkg-config`
  - **Debian/Ubuntu**: `sudo apt-get install -y build-essential python3-dev libxml2-dev libxslt1-dev pkg-config`

### 1) Get the code
```bash
git clone https://github.com/bitbot-irc/bitbot.git
cd bitbot
````

### 2) Create a virtualenv

**bash/zsh**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**fish**

```fish
python3 -m venv .venv
source .venv/bin/activate.fish
```

### 3) Install dependencies

`requirements.txt` targets modern Python (includes `lxml>=6,<7`, `requests-toolbelt>=1.0.0`, and `legacy-cgi` for Py3.13 compatibility).

```bash
pip install -U pip wheel
pip install -r requirements.txt
# If pip compiles lxml from source, install the -devel headers from step 0.
```

### 4) Configure

```bash
mkdir -p ~/.bitbot
cp docs/bot.conf.example ~/.bitbot/bot.conf
# Edit ~/.bitbot/bot.conf: set nick/ident/realname, servers/channels, and enable modules.
# Some modules (google/youtube/spotify/…​) require API keys; add them here before enabling.
# The 'user_time' module depends on the 'location' module being configured.
```

### 5) First run

```bash
./bitbotd -a   # add your network(s)
./bitbotd      # start the bot (foreground)
```

### 6) Master admin password

```bash
./bitbotctl command master-password
# Use this in IRC to register your admin account.
```

---

## Run as a service (optional)

```ini
# /etc/systemd/system/bitbot.service
[Unit]
Description=BitBot IRC bot
After=network-online.target
Wants=network-online.target

[Service]
User=bitbot
WorkingDirectory=/opt/bitbot
Environment=PATH=/opt/bitbot/.venv/bin
ExecStart=/opt/bitbot/bitbotd
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Deploy:

```bash
sudo useradd -r -s /usr/sbin/nologin bitbot 2>/dev/null || true
sudo cp -r ~/bitbot /opt/bitbot && sudo chown -R bitbot:bitbot /opt/bitbot
cd /opt/bitbot
sudo -u bitbot python3 -m venv .venv
sudo -u bitbot .venv/bin/pip install -U pip wheel
sudo -u bitbot .venv/bin/pip install --only-binary=:all: -r requirements.txt
sudo systemctl daemon-reload
sudo systemctl enable --now bitbot
```

**Upgrade:**

```bash
cd /opt/bitbot
sudo -u bitbot git pull
sudo -u bitbot .venv/bin/pip install -U -r requirements.txt
sudo systemctl restart bitbot
```

---

## Backups

Back up the entire `~/.bitbot` directory (config, database, rotated logs). Tools like
[borgbackup](https://borgbackup.readthedocs.io/en/stable/) work well.

---

## Docs, Support, License

* Configuration help: see `docs/help/config.md`.
* Chat: `#bitbot` on irc.libera.chat.
* License: GNU GPL v2.0 — see [LICENSE](LICENSE).

