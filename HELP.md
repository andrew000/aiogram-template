# Helpful information

### In this file, you can find answers to frequently asked questions and useful commands.

***

<details>
    <summary><b>💬 Useful commands</b></summary>

#### Update Dependencies

First, run `make outdated` to check for outdated dependencies. Then, edit `pyproject.toml` file and run the
following command to update dependencies:

```shell
make outdated

# Edit pyproject.toml

uv lock --upgrade
make sync
```

#### Check Dependencies Updates

```shell
make outdated
```

#### Linting

```shell
make lint
```

#### MyPy

```shell
make mypy
```

#### Formatting

```shell
make format
```

</details>

***

<details>
  <summary>💢 The term 'make' is not recognized as the name of a cmdlet, function, script file, or operable program.</summary>

#### ⚠️ You, as developer, **MUST** have `make` installed on your system to use `Makefile` commands. 

#### [Windows] Answer:

1. Open PowerShell as Administrator.
2. Install Chocolatey by running the following command:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```
3. Close and reopen PowerShell with administrative privileges.
4. Install Make by running the following command:
   ```powershell
   choco install make
   ```
5. Verify the installation by running:
   ```powershell
   make --version
   ```
6. If the command is still not recognized, ensure that the Make installation path is added to your system's PATH
   environment variable.
   ```powershell
   $currentPath = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
   [System.Environment]::SetEnvironmentVariable('PATH', $currentPath + ';C:\Program Files (x86)\GnuWin32\bin', 'Machine')
   ```
7. Restart PowerShell and try running `make` again.

#### [Linux] Answer:

1. Open your terminal.
2. Install Make using your package manager.
3. ```bash
   # For Debian/Ubuntu-based systems
   sudo apt update
   sudo apt install make -y
   ```
   ```bash
   # Fedora
   sudo dnf install make -y
   ```
4. Verify the installation by running:
   ```bash
   make --version
   ```

</details>

***

<details>
    <summary>❓ How to install UV?</summary>

#### [Windows] Answer:

1. Open PowerShell
2. Install UV using the following command:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. Restart PowerShell to apply changes.
4. Verify the installation by running:
   ```powershell
   uv --version
   ```

#### [Linux] Answer:

1. Open your terminal.
2. Install UV using the following command:
   ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
3. Restart your terminal to apply changes.
4. Verify the installation by running:
   ```bash
   uv --version
   ```

</details>

***

<details>
    <summary>❓ How to install Docker?</summary>

#### [Windows] Answer:

1. Download Docker Desktop from the official Docker website: https://www.docker.com/products/docker-desktop
2. Run the installer and follow the on-screen instructions.
3. After installation, Docker Desktop should start automatically. If not, you can start it from the Start menu.
4. Verify the installation by opening PowerShell and running:
   ```powershell
   docker --version
   ```
5. You may need to log in to Docker Desktop with your Docker Hub account or create a new one.
6. Ensure that WSL 2 is enabled on your system for better performance.
7. Restart your computer if prompted.

#### [Linux] Answer:

1. Open https://docs.docker.com/engine/install
2. Follow the instructions for your specific Linux distribution.
3. After installation, you may need to start the Docker service:
   ```bash
   sudo systemctl start docker
   ```
4. Enable Docker to start on boot:
   ```bash
   sudo systemctl enable --now docker
   ```
5. Verify the installation by running:
   ```bash
   docker --version
   ```

</details>

***

<details>
    <summary>❓ Why PyCharm marks import with red color?</summary>

I use "unique" project structure, where app directory contains code, but root directory contains configuration files.

In PyCharm, right-click on the bot directory and select Mark Directory as -> Sources Root. Also, unmark project root
directory Unmark as Sources Root. This will fix the problem.

![image](https://github.com/user-attachments/assets/f4acbd42-f4e7-4e1b-9e16-a40db71ac672)

![image](https://github.com/user-attachments/assets/01f4f030-46e0-4267-a5bc-4b05ae0b9015)

![image](https://github.com/user-attachments/assets/f2e02548-173b-4be6-944f-623ff7dc2207)

</details>

***

<details>
    <summary>❓ Why You use __import__?</summary>

My inclinations make me do this to avoid some attack vector invented by my "paranoia"
</details>

***

<details>
    <summary>❓ Why not use aiogram-cli?</summary>

It's a good library, but I prefer to use my own code 🤷‍♂️
</details>

***

<details>
    <summary>❓ How to properly set up .env file?</summary>

1. After cloning the repository, navigate to the project root.
2. Copy the example file based on your development environment:
    - For Docker: `cp .env.example .env.docker`
    - For local: `cp env.example .env`

3. Open the new `.env` file in a text editor.
4. Fill in the required variables:
    - `BOT_TOKEN`: Your Telegram bot token from BotFather.
    - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: PostgreSQL credentials.
    - `REDIS_PASSWORD`: Redis password (if using authentication).
    - `WEBHOOKS`: Set to `True` if using webhooks, otherwise False.
    - `WEBHOOK_URL` and `WEBHOOK_SECRET_TOKEN`: Required if webhooks are enabled.
5. Save the file. Avoid committing `.env` to version control - add it to `.gitignore` if not already.

</details>

***

<details>
    <summary>❓ How to enable and configure webhooks?</summary>

1. In your `.env` file, set `WEBHOOKS=True`.
2. Set `WEBHOOK_URL` to your bot's webhook endpoint (e.g., `https://example.com/webhook`).
3. Set `WEBHOOK_SECRET_TOKEN` to a secure random string.
4. Uncomment the `caddy` service in `docker-compose.yml` to enable Caddy.

</details>

***

