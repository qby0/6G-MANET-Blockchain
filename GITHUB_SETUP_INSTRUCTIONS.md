# Instructions for Setting Up GitHub Repository
# Инструкции по настройке репозитория GitHub

[English](#english) | [Русский](#русский)

## English <a name="english"></a>

## Setting Up a Repository for 6G-MANET-Blockchain Simulation

### Step 1: Create a New Repository on GitHub
1. Go to [GitHub](https://github.com/) and log in to your account
2. Click on the "+" button in the top right corner and select "New repository"
3. Name your repository (e.g., "6G-MANET-Blockchain-Simulation")
4. Add a description: "Blockchain system simulation at the junction of 6G and MANET networks"
5. Choose public or private repository based on your preference
6. Initialize with a README (optional)
7. Add an MIT license (or another license of your choice)
8. Click "Create repository"

### Step 2: Clone the Repository Locally
```bash
git clone https://github.com/YOUR_USERNAME/6G-MANET-Blockchain-Simulation.git
cd 6G-MANET-Blockchain-Simulation
```

### Step 3: Organize Files and Directories
1. Copy the prepared project structure to the cloned repository:
   - Copy the entire `test_ns3_blocksim` directory
   - Rename the main `6G-MANET-Blockchain-Simulation.md` file to `README.md`
   - Make sure to include the English versions of the documentation

2. Directory structure should look like:
```
6G-MANET-Blockchain-Simulation/
├── LICENSE
├── README.md
└── test_ns3_blocksim/
    ├── config/
    ├── models/
    ├── scripts/
    ├── visualization/
    ├── results/
    ├── external/
    ├── README.md
    ├── README_EN.md
    ├── README_IMPLEMENTATION_STATUS.md
    └── README_IMPLEMENTATION_STATUS_EN.md
```

### Step 4: Add and Commit Files
```bash
git add .
git commit -m "Initial commit with simulation framework"
git push origin main
```

### Step 5: Set Up GitHub Pages (Optional)
1. Go to your repository on GitHub
2. Click on "Settings"
3. Scroll down to "GitHub Pages" section
4. Select "main" branch as the source and click "Save"
5. Your documentation will be available at `https://YOUR_USERNAME.github.io/6G-MANET-Blockchain-Simulation/`

### Step 6: Add Collaborators (Optional)
1. Go to repository "Settings"
2. Click on "Manage access"
3. Click "Invite a collaborator" and enter their GitHub username or email

---

## Русский <a name="русский"></a>

## Настройка репозитория для симуляции блокчейна в сетях 6G-MANET

### Шаг 1: Создание нового репозитория на GitHub
1. Перейдите на [GitHub](https://github.com/) и войдите в свой аккаунт
2. Нажмите на кнопку "+" в правом верхнем углу и выберите "New repository"
3. Назовите ваш репозиторий (например, "6G-MANET-Blockchain-Simulation")
4. Добавьте описание: "Симуляция блокчейн-системы на стыке сетей 6G и MANET"
5. Выберите публичный или приватный репозиторий по вашему усмотрению
6. Инициализируйте с README (опционально)
7. Добавьте лицензию MIT (или другую лицензию по вашему выбору)
8. Нажмите "Create repository"

### Шаг 2: Клонирование репозитория локально
```bash
git clone https://github.com/ВАШ_ЛОГИН/6G-MANET-Blockchain-Simulation.git
cd 6G-MANET-Blockchain-Simulation
```

### Шаг 3: Организация файлов и директорий
1. Скопируйте подготовленную структуру проекта в клонированный репозиторий:
   - Скопируйте всю директорию `test_ns3_blocksim`
   - Переименуйте основной файл `6G-MANET-Blockchain-Simulation.md` в `README.md`
   - Убедитесь, что включены английские версии документации

2. Структура директорий должна выглядеть так:
```
6G-MANET-Blockchain-Simulation/
├── LICENSE
├── README.md
└── test_ns3_blocksim/
    ├── config/
    ├── models/
    ├── scripts/
    ├── visualization/
    ├── results/
    ├── external/
    ├── README.md
    ├── README_EN.md
    ├── README_IMPLEMENTATION_STATUS.md
    └── README_IMPLEMENTATION_STATUS_EN.md
```

### Шаг 4: Добавление и коммит файлов
```bash
git add .
git commit -m "Начальный коммит с фреймворком симуляции"
git push origin main
```

### Шаг 5: Настройка GitHub Pages (опционально)
1. Перейдите в ваш репозиторий на GitHub
2. Нажмите на "Settings"
3. Прокрутите вниз до раздела "GitHub Pages"
4. Выберите ветку "main" в качестве источника и нажмите "Save"
5. Ваша документация будет доступна по адресу `https://ВАШ_ЛОГИН.github.io/6G-MANET-Blockchain-Simulation/`

### Шаг 6: Добавление соавторов (опционально)
1. Перейдите в настройки репозитория "Settings"
2. Нажмите на "Manage access"
3. Нажмите "Invite a collaborator" и введите их имя пользователя GitHub или email 