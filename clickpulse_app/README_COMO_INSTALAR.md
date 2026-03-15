# ClickPulse — Mouse Activity Tracker

## O que é

ClickPulse é um aplicativo desktop para Windows que monitora a atividade do mouse em tempo real. Ele rastreia cliques por hora, tempo ativo vs pausas, tipos de clique (esquerdo, direito, meio) e mantém histórico com dashboard visual e exportação CSV.

## Requisitos

- Windows 10 ou superior
- Python 3.11 ou superior

## Como instalar

### 1. Instalar o Python

Se ainda não tem o Python instalado:
1. Acesse https://www.python.org/downloads/
2. Baixe a versão mais recente do Python 3
3. Durante a instalação, marque a opção "Add Python to PATH"

### 2. Baixar o ClickPulse

Copie toda a pasta `clickpulse_app` para o local desejado no seu computador.

### 3. Instalar dependências

Abra o terminal (CMD ou PowerShell) na pasta `clickpulse_app` e execute:

```
pip install -r requirements.txt
```

### 4. Executar o aplicativo

Na mesma pasta, execute:

```
python main.py
```

O aplicativo vai abrir com o dashboard e um ícone vai aparecer na bandeja do sistema (perto do relógio).

## Como usar

### Dashboard
- Mostra cliques do dia, tempo ativo, pausas e taxa de cliques por hora
- Gráfico de barras com cliques por hora
- Gráfico de pizza com distribuição por tipo de clique
- Timeline mostrando períodos ativos (verde) e pausas (vermelho)
- Atualiza automaticamente a cada 5 segundos

### Histórico
- Selecione uma data e período (dia, semana ou mês)
- Veja a tabela com estatísticas horárias
- Exporte os dados para CSV

### Configurações
- Threshold de pausa: tempo de inatividade para considerar pausa (padrão: 3 minutos)
- Alerta de pausa longa: avisa quando a pausa é muito longa (padrão: 30 minutos)
- Milestone de cliques: notifica a cada N cliques (padrão: 100)
- Intervalo de verificação: frequência da checagem de atividade (padrão: 10 segundos)

### Bandeja do sistema (System Tray)
- Fechar a janela apenas minimiza para a bandeja
- Clique duplo no ícone para reabrir
- Clique direito para ver o menu com opções
- Para sair de verdade, use "Sair" no menu da bandeja

### Exportação CSV
- Use o botão "Exportar CSV" na toolbar ou na aba Histórico
- O arquivo inclui todos os cliques individuais e um resumo horário

## Como gerar o .exe (opcional)

Para criar um executável standalone que não precisa do Python instalado:

### 1. Instalar o PyInstaller

```
pip install pyinstaller
```

### 2. Gerar o executável

Na pasta `clickpulse_app`, execute:

```
pyinstaller --onefile --windowed --icon=assets/icon.png --name=ClickPulse main.py
```

### 3. Encontrar o executável

O arquivo `ClickPulse.exe` será gerado na pasta `dist/`. Você pode copiar esse arquivo para qualquer lugar e executar diretamente.

## Dados

- O banco de dados (`clickpulse.db`) é criado automaticamente na mesma pasta do aplicativo
- Todos os dados ficam armazenados localmente no seu computador
- Nenhum dado é enviado para a internet

## Solução de problemas

**O app não abre:**
- Verifique se o Python está instalado: `python --version`
- Verifique se as dependências estão instaladas: `pip list`
- Reinstale as dependências: `pip install -r requirements.txt`

**Gráficos não aparecem:**
- Verifique se o pyqtgraph está instalado: `pip install pyqtgraph`

**Notificações não funcionam:**
- Verifique se o plyer está instalado: `pip install plyer`
- As notificações funcionam apenas no Windows
