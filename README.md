<p align="center">
  <img src="assets/icon.png" alt="ClickPulse Logo" width="120" height="120">
</p>

<h1 align="center">ClickPulse</h1>

<p align="center">
  <strong>Monitor de atividade do mouse em tempo real para Windows</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-UI%20Framework-41CD52?logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/Chrome-Extension-4285F4?logo=googlechrome&logoColor=white" alt="Chrome Extension">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<p align="center">
  Acompanhe seus cliques, tempo ativo, pausas e produtividade ao longo do dia com um dashboard visual elegante.
</p>

---

## Sobre o Projeto

O **ClickPulse** nasceu da necessidade de entender como uso meu mouse ao longo do dia de trabalho. Ele roda silenciosamente na bandeja do sistema, rastreando cada clique e detectando automaticamente quando estou ativo ou em pausa. Tudo isso com um visual moderno, gráficos em tempo real e notificações inteligentes.

Ideal para quem quer monitorar a produtividade pessoal de forma simples e visual.

---

## Screenshots

<table>
  <tr>
    <td align="center"><strong>Dashboard</strong></td>
    <td align="center"><strong>Historico</strong></td>
  </tr>
  <tr>
    <td>

```
 ┌─────────────────────────────────────────┐
 │  🖱 Cliques hoje    ⏱ Tempo ativo      │
 │     1.247              4h 32m           │
 │  ⏸ Pausas           📊 Cliques/hora    │
 │     1h 15m              275             │
 │─────────────────────────────────────────│
 │  [████▓▓▓▓░░░░░░░░░░░░░░░░] Hora a hora│
 │  [🔵 65% Left 🔴 28% Right 🟡 7% Mid] │
 │─────────────────────────────────────────│
 │  ⬛⬛🟩🟩🟩🟩🟥🟩🟩🟩🟩🟥🟥🟩🟩🟩  │
 │  Timeline de atividade                  │
 └─────────────────────────────────────────┘
```

</td>
    <td>

```
 ┌─────────────────────────────────────────┐
 │  📅 Data: 15/03/2026  Periodo: Semana  │
 │─────────────────────────────────────────│
 │  Hora  Total  Esq  Dir  Meio  Ativo    │
 │  09h    142    98   38    6    52min    │
 │  10h    203   145   49    9    58min    │
 │  11h    178   120   48   10    55min    │
 │─────────────────────────────────────────│
 │  [█████ ████ ███ █████ ██]              │
 │  Comparativo por dia                    │
 │─────────────────────────────────────────│
 │  Total: 1.247 cliques | Ativo: 4h 32m  │
 └─────────────────────────────────────────┘
```

</td>
  </tr>
</table>

---

## Funcionalidades

| Funcionalidade | Descricao |
|---|---|
| **Dashboard em tempo real** | Cards com total de cliques, tempo ativo/pausa e taxa de cliques por hora |
| **Grafico de barras** | Visualize seus cliques hora a hora ao longo do dia |
| **Grafico de pizza** | Distribuicao entre cliques esquerdo, direito e do meio |
| **Timeline de atividade** | Barra visual mostrando periodos ativos e pausas |
| **Historico completo** | Consulte dados por dia, semana ou mes com tabela detalhada |
| **Grafico comparativo** | Compare o total de cliques entre diferentes dias |
| **Exportacao CSV** | Exporte seus dados para analise em planilhas |
| **Notificacoes inteligentes** | Alertas de milestones de cliques, pausas longas e resumo horario |
| **Bandeja do sistema** | Roda discretamente com tooltip mostrando cliques/hora e estado |
| **Instancia unica** | Impede abrir o app duas vezes acidentalmente |
| **Tema escuro** | Interface moderna com paleta de cores confortavel para os olhos |
| **Banco local** | Todos os dados ficam no seu computador em SQLite |

---

## Tecnologias

- **Python 3.11+** — Linguagem principal
- **PyQt6** — Interface grafica nativa e moderna
- **pyqtgraph** — Graficos de alto desempenho em tempo real
- **pynput** — Captura de eventos do mouse
- **plyer** — Notificacoes nativas do Windows
- **SQLite** — Banco de dados local embutido

---

## Instalacao

### Pre-requisitos

- Windows 10 ou superior
- Python 3.11 ou superior

### Passo a passo

```bash
# 1. Clone o repositorio
git clone https://github.com/elton2024br/ClickPulse.git
cd ClickPulse

# 2. Crie um ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate

# 3. Instale as dependencias
pip install -r requirements.txt

# 4. Execute o app
python main.py
```

### Gerar executavel (.exe)

```bash
# Instale o PyInstaller
pip install pyinstaller

# Gere o executavel
pyinstaller --onefile --windowed --icon=assets/icon.png --name=ClickPulse --add-data="assets;assets" main.py
```

O executavel sera gerado em `dist/ClickPulse.exe`.

---

## Estrutura do Projeto

```
ClickPulse/
├── main.py                          # Ponto de entrada do app
├── requirements.txt                 # Dependencias Python
├── assets/
│   └── icon.png                     # Icone do app
├── clickpulse_local/
│   ├── clickpulse.py                # Versao local (Python + pynput)
│   ├── dashboard.html               # Dashboard web (servido pelo Python)
│   └── ClickPulse.html              # Versao simples (apenas na pagina)
├── clickpulse_extension/            # Extensao Chrome (Side Panel)
└── clickpulse/
    ├── __init__.py
    ├── database.py                  # Banco de dados SQLite
    ├── config.py                    # Gerenciamento de configuracoes
    ├── tracker.py                   # Rastreamento de cliques e movimento
    ├── activity.py                  # Deteccao de atividade vs pausa
    ├── aggregator.py                # Agregacao de estatisticas por hora
    ├── notifier.py                  # Notificacoes do Windows
    ├── exporter.py                  # Exportacao para CSV
    └── ui/
        ├── __init__.py
        ├── main_window.py           # Janela principal com abas
        ├── dashboard.py             # Dashboard com graficos em tempo real
        ├── history.py               # Historico com tabela e comparativos
        ├── settings_ui.py           # Tela de configuracoes
        └── tray.py                  # Icone na bandeja do sistema
```

---

## Configuracoes

Todas as configuracoes podem ser ajustadas pela interface:

| Configuracao | Padrao | Descricao |
|---|---|---|
| Threshold de pausa | 3 min | Tempo de inatividade para considerar pausa |
| Alerta de pausa longa | 30 min | Notifica apos X minutos em pausa |
| Milestone de cliques | 100 | Notifica a cada X cliques atingidos |
| Intervalo de verificacao | 10 seg | Frequencia de checagem de atividade |

---

## Versao Local (Web Dashboard + Python)

O ClickPulse tambem tem uma versao leve que roda localmente no seu computador. Usa Python + pynput para capturar **cliques globais** (em qualquer janela ou programa) e exibe um dashboard em tempo real no navegador.

### Como usar

```bash
# 1. Instale a dependencia
pip install pynput

# 2. Entre na pasta
cd clickpulse_local

# 3. Execute
python clickpulse.py
```

O dashboard abre automaticamente no navegador em `http://127.0.0.1:5555`.

### Funcionalidades

- **Rastreamento global** — Captura cliques em TODAS as janelas e programas (nao apenas no navegador)
- **Dashboard em tempo real** — Atualiza a cada 500ms com dados reais do Python
- **Leve** — Apenas 1 dependencia (pynput), sem framework web pesado
- **Persistencia** — Dados salvos em arquivo JSON local com reset diario automatico
- **Pausar/Retomar** — Controle o rastreamento pela aba de configuracoes
- **Tema escuro** — Visual identico ao app desktop e extensao Chrome

---

## Extensao Chrome

O ClickPulse tambem esta disponivel como extensao para Google Chrome! A extensao abre como um painel lateral (side panel) e rastreia todos os cliques do mouse diretamente no navegador.

### Funcionalidades da Extensao

- **Side Panel** — Abre como painel lateral ao clicar no icone da extensao
- **Rastreamento real** — Captura cliques esquerdo, direito e meio em todas as abas
- **Dashboard completo** — Cards de estatisticas, grafico de barras por hora, grafico de pizza, live feed e timeline
- **Persistencia** — Dados salvos via chrome.storage.local com reset diario automatico
- **Configuracoes** — Pause/retome o rastreamento e resete os dados a qualquer momento
- **Tema escuro** — Visual consistente com o app desktop

### Instalacao da Extensao

1. Baixe ou clone este repositorio
2. Abra o Chrome e va em `chrome://extensions/`
3. Ative o **Modo do desenvolvedor** (canto superior direito)
4. Clique em **Carregar sem compactacao**
5. Selecione a pasta `clickpulse_extension/`
6. Clique no icone do ClickPulse na barra de ferramentas para abrir o painel lateral

### Estrutura da Extensao

```
clickpulse_extension/
├── manifest.json          # Configuracao Manifest V3
├── background.js          # Service worker (agregacao de dados)
├── content.js             # Content script (captura de cliques)
├── sidepanel.html         # Interface do painel lateral
├── sidepanel.css          # Estilos (tema escuro)
├── sidepanel.js           # Logica do dashboard (vanilla JS)
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

---

## Privacidade

O ClickPulse **nao envia nenhum dado para a internet**. Todos os dados ficam armazenados localmente no arquivo `clickpulse.db` ao lado do executavel. Voce tem controle total sobre seus dados e pode apagar o banco a qualquer momento.

---

## Autor

Desenvolvido por **Elton** com dedicacao para a comunidade.

- GitHub: [@elton2024br](https://github.com/elton2024br)

---

## Licenca

Este projeto esta sob a licenca MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">
  Feito com muita dedicacao por <strong>Elton</strong>
</p>
