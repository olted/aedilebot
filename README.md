# AedileBot 🏛️

> **A Discord bot for Foxhole damage calculations**

AedileBot is a Discord bot designed for the Foxhole gaming community, providing damage calculations and bunker health analysis tools.

## ✨ Key Features

- 🎯**Advanced Damage Calculations** - Combat math for weapons vs. targets
- 🏰**Bunker Analysis Tools** - Complex health, mitigation, and repair cost calculations
- 🧠**Intelligent Fuzzy Matching** - Natural language processing for user-friendly commands
- ⚡**Discord Slash Commands** - Modern interface with autocomplete functionality
- 🐳**Docker Support** - Easy deployment and scaling

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
  - [Prerequisites](#prerequisites)
  - [Docker Deployment](#docker-deployment)
  - [Manual Installation](#manual-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
  - [Basic Commands](#basic-commands)
  - [Advanced Bunker Calculations](#advanced-bunker-calculations)
  - [Natural Language Queries](#natural-language-queries)
- [Core Commands](#-core-commands)
- [Dependencies](#-Dependencies)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

### For Discord Server Administrators

1. **Invite the Bot** (if hosted):

   ```
   [Bot invitation link will be provided by maintainers]
   ```

2. **Basic Usage**:

   ```
   /kill target:Silverhand weapon:75mm
   /bunker_kill weapon:satchel total_size:15 tier:Tier 3
   /help
   ```

### For Self-Hosting

1. **Clone and Setup**:

   ```bash
   git clone https://github.com/your-repo/aedilebot.git
   cd aedilebot
   cp src/.env.sample src/.env
   # Edit src/.env with your Discord bot token
   ```
2. **Run with Docker**:

   ```bash
   docker compose up -d
   ```
3. **Invite Bot to Server**:

   - Use Discord Developer Portal to get bot invitation link
   - Ensure bot has necessary permissions (Send Messages, Use Slash Commands)

## 🔧 Installation

### Prerequisites

- **Python 3.12+** (for manual installation)
- **Docker & Docker Compose** (for containerized deployment)
- **Discord Bot Token** from [Discord Developer Portal](https://discord.com/developers/applications)

### Docker Deployment (Recommended)

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-repo/aedilebot.git
   cd aedilebot
   ```
2. **Configure environment**:

   ```bash
   cp src/.env.sample src/.env
   ```

   Edit [`src/.env`](src/.env.sample):

   ```env
   DEPLOYMENT_TOKEN=your_production_bot_token_here
   DEV_SERVER_TOKEN=your_development_bot_token_here
   ```
3. **Set Discord bot token for Docker**:

   ```bash
   export DISCORD_BOT_TOKEN=your_bot_token_here
   ```
4. **Deploy with Docker Compose**:

   ```bash
   docker compose up -d
   ```
5. **Verify deployment**:

   ```bash
   docker compose logs aedile
   ```

### Manual Installation

1. **Clone and setup Python environment**:

   ```bash
   git clone https://github.com/your-repo/aedilebot.git
   cd aedilebot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment**:

   ```bash
   cp src/.env.sample src/.env
   # Edit src/.env with your bot tokens
   ```
4. **Run the bot**:

   ```bash
   cd src
   python main.py
   ```

## ⚙️ Configuration

### Environment Variables

Configure the bot using the [`src/.env`](src/.env.sample) file:

| Variable             | Description                       | Required |
| -------------------- | --------------------------------- | -------- |
| `DEPLOYMENT_TOKEN` | Discord bot token for production  | Yes      |
| `DEV_SERVER_TOKEN` | Discord bot token for development | Optional |
| `https_proxy`      | HTTP proxy URL if needed          | Optional |

### Discord Bot Setup

1. **Create Application**:

   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application and bot
   - Copy bot token to your`.env` file
2. **Bot Permissions**:
   Required permissions for the bot:

   - `Send Messages`
   - `Use Slash Commands`
   - `Embed Links`
   - `Read Message History`
3. **Invite Bot**:
   Generate invitation URL with required permissions and add to your Discord server.

## 📖 Usage

AedileBot supports both slash commands and natural language queries. Below are the available commands with examples and detailed descriptions:

### Slash Commands

#### `/help`
- **Purpose**: Display help information and available commands.
- **Example**:
  ```bash
  /help
  ```
  Displays a list of all available commands and their usage.

#### `/kill target:<target> weapon:<weapon>`
- **Purpose**: Calculate shots needed to kill a target.
- **Parameters**:
  - `target` (string, required): Target name with autocomplete.
  - `weapon` (string, required): Weapon name with autocomplete.
- **Example**:
  ```bash
  /kill target:Silverhand weapon:75mm
  ```
  Result: It takes 3 75mm to kill a Silverhand - Mk. IV (SvH)

#### `/statsheet entity:<entity>`
- **Purpose**: Show detailed statistics for any entity (weapons, vehicles, or structures).
- **Parameters**:
  - `entity` (string, required): Entity name with autocomplete.
- **Example**:
  ```bash
  /statsheet entity:Bunker Core
  ```
  Displays health, mitigation, and repair costs for the specified entity.

#### `/bunker_kill`
- **Purpose**: Advanced bunker damage calculations.
- **Parameters**:
  - `weapon` (string, required): Weapon for attack.
  - `total_size` (integer, required): Total bunker pieces (including garrisons).
  - `tier` (choice, required): Bunker tier (1, 2, or 3).
  - `green_dots` (integer, optional): Internal edges (estimated if not provided).
  - `red_dots` (integer, optional): External edges (estimated if not provided).
  - `mg`, `atg`, `howi`, etc. (integer, optional): Number of each garrison type.
- **Example**:
  ```bash
  /bunker_kill weapon:satchel total_size:15 tier:Tier 3 mg:2 atg:1 howi:1
  ```
  Result: It takes 61 Alligator Charge to kill a meta with 24225 health (56.94% breachable) and 1800 bmat repair cost (13.46 health/bmat) (tier 3, 15 pieces, 22 green, 16 red, 2 mg, 1 atg, 1 hg) (red or green estimated due to not being specified)

### Natural Language Queries

AedileBot understands natural language for intuitive usage:

- **Examples**:

  ```plaintext
  How many 40mm to kill trench?
  How much 150mm to destroy Patridia?
  How many satchels to kill t3 bunker core husk?
  How many 68mm to disable HTD?
  ```

  The bot uses fuzzy matching to understand variations in spelling and terminology.

### Data Structure

The bot uses JSON databases for game data:

- **[`data/Weapons.json`](data/Weapons.json)** - Weapon statistics and damage types
- **[`data/Targets.json`](data/Targets.json)** - Vehicle and structure data
- **[`data/Damage.json`](data/Damage.json)** - Damage type mitigation values
- **[`data/Location_names.json`](data/Location_names.json)** - Town and relic names

### Calculation Engine

The [`DamageCalculator`](src/calculator.py#L13) class handles:

- **Damage mitigation** based on target type and weapon damage type
- **Bunker complexity modeling** with structural integrity calculations
- **Multi-tier structure** support with different mitigation values
- **Veterancy and location bonuses** for enhanced accuracy

## 💻 Dependencies

Core Python packages (see [`requirements.txt`](requirements.txt)):

```txt
discord>=2.0.0          # Discord API integration
fuzzywuzzy>=0.18.0      # Fuzzy string matching
python-levenshtein>=0.12.0  # String distance calculations
python-dotenv>=0.19.0   # Environment variable management
dnspython>=1.16.0       # DNS resolution
PyNaCl>=1.4.0          # Voice support (optional)
async-timeout>=3.0.1    # Async operation timeouts
```

## 🚀 Deployment

### Production Deployment with Docker

1. **Prepare production environment**:

   ```bash
   # Clone repository
   git clone https://github.com/your-repo/aedilebot.git
   cd aedilebot

   # Set production token
   export DISCORD_BOT_TOKEN=your_production_token
   ```
2. **Deploy with Docker Compose**:

   ```bash
   docker compose up -d
   ```
3. **Monitor deployment**:

   ```bash
   # Check logs
   docker compose logs -f aedile

   # Check status
   docker compose ps
   ```
4. **Update deployment**:

   ```bash
   git pull origin main
   docker compose down
   docker compose up -d --build
   ```

### Manual Production Deployment

1. **Setup production environment**:

   ```bash
   # Create dedicated user
   sudo useradd -m -s /bin/bash aedilebot
   sudo su - aedilebot

   # Clone and setup
   git clone https://github.com/your-repo/aedilebot.git
   cd aedilebot
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Configure systemd service** (Linux):

   ```ini
   # /etc/systemd/system/aedilebot.service
   [Unit]
   Description=AedileBot Discord Bot
   After=network.target

   [Service]
   Type=simple
   User=aedilebot
   WorkingDirectory=/home/aedilebot/aedilebot/src
   Environment=PATH=/home/aedilebot/aedilebot/venv/bin
   ExecStart=/home/aedilebot/aedilebot/venv/bin/python main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
3. **Start and enable service**:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable aedilebot
   sudo systemctl start aedilebot
   ```

## 🔍 Troubleshooting

### Common Issues

#### Bot Not Responding

```bash
# Check bot status
docker compose logs aedile

# Common causes:
# - Invalid bot token
# - Missing permissions
# - Network connectivity issues
```

**Solutions**:

1. Verify bot token in`.env` file
2. Check bot permissions in Discord server
3. Ensure bot is online in Discord Developer Portal

#### Command Not Found

```
The application did not respond
```

**Solutions**:

1. Ensure slash commands are synced:
   ```python
   # Check logs for: "Synced X commands"
   ```
2. Wait up to 1 hour for Discord to propagate commands globally
3. Try commands in DM with bot first

#### Calculation Errors

```
This weapon does no damage to this entity
```

**Solutions**:

1. Check weapon and target names with`/statsheet`
2. Verify entities exist in database
3. Some combinations may be intentionally impossible

#### Memory Issues

```bash
# Monitor memory usage
docker stats aedile
```

**Solutions**:

1. Increase container memory limits
2. Restart bot periodically for memory cleanup
3. Consider upgrading server specifications

### Debug Mode

Enable debug mode by setting in [`src/main.py`](src/main.py#L14):

```python
utils.debugging = True
```

This provides detailed calculation logs and error information.

## 🤝 Contributing

We welcome contributions to AedileBot! Whether you're fixing bugs, adding features, or improving documentation, your help makes the project better for everyone.

### Development Setup

1. **Fork and clone**:

   ```bash
   git fork https://github.com/your-repo/aedilebot.git
   git clone https://github.com/your-username/aedilebot.git
   cd aedilebot
   ```
2. **Setup development environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure development bot**:

   ```bash
   cp src/.env.sample src/.env
   # Add your development bot token to DEV_SERVER_TOKEN
   ```

### Code Standards

- **Python Style**: Follow PEP 8 guidelines
- **Documentation**: Add docstrings for new functions and classes
- **Testing**: Test changes with various weapon/target combinations
- **Commit Messages**: Use clear, descriptive commit messages

### Project Structure

```
aedilebot/
├── src/                    # Main application code
│   ├── main.py            # Entry point and utilities
│   ├── bot.py             # Discord bot interface and commands
│   ├── calculator.py      # Damage calculation engine
│   ├── parse.py           # Data parsing and management
│   ├── fuzzy.py           # Fuzzy matching algorithms
│   └── utils.py           # Utility functions
├── data/                  # Game data files
│   ├── Weapons.json       # Weapon statistics
│   ├── Targets.json       # Vehicle/structure data
│   ├── Damage.json        # Damage type definitions
│   └── *.json            # Other game data
├── scripts/               # Data processing scripts
├── data_manual/           # Manual data overrides
└── docs/                  # Documentation
```

### Adding New Features

1. **Game Data Updates**:

   - Currently undocumented
2. **New Commands**:

   - Add command handler in [`src/bot.py`](src/bot.py)
   - Implement calculation logic in [`src/calculator.py`](src/calculator.py)
   - Add fuzzy matching support in [`src/fuzzy.py`](src/fuzzy.py)
3. **Calculation Improvements**:

   - Modify [`DamageCalculator`](src/calculator.py#L13) class
   - Update damage type handling
   - Add new mitigation calculations

### Pull Request Process

1. **Create feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make changes and test**:

   ```bash
   # Test your changes thoroughly
   python src/main.py
   ```
3. **Commit and push**:

   ```bash
   git add .
   git commit -m "Add: descriptive commit message"
   git push origin feature/your-feature-name
   ```
4. **Create Pull Request**:

   - Describe changes and motivation
   - Include testing steps
   - Reference any related issues

### Reporting Issues

When reporting bugs or requesting features:

1. **Use GitHub Issues** with appropriate labels
2. **Include reproduction steps** for bugs
3. **Provide context** for feature requests
4. **Check existing issues** to avoid duplicates

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).

### Key Points

- ✅**Commercial use** allowed
- ✅**Modification** allowed
- ✅**Distribution** allowed
- ✅**Private use** allowed
- ❗**Network use is distribution** - source must be provided
- ❗**Same license** required for derivatives
- ❗**State changes** must be documented

### Full License

See the [`LICENSE`](LICENSE) file for complete terms and conditions.

### Third-Party Licenses

This project uses several open-source libraries:

- **Discord.py**: MIT License
- **FuzzyWuzzy**: GPL v2 License
- **Python-Levenshtein**: GPL v2 License
