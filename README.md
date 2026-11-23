# 💅 Agenda & Finanças da Manicure

Site responsivo (feito para celular) para controlar agendamentos, serviços, finanças e separar o **salário** do **caixa da empresa**.

**Tecnologias:** Python 3.10+ · Flask · SQLite (o banco é um arquivo, não precisa instalar nada)

## Telas
| Tela | O que faz |
|------|-----------|
| Início | Atendimentos da semana, botão de novo agendamento, concluir/cancelar/remarcar |
| Serviços | Ver, cadastrar, editar e remover serviços (preço, custo e horas) |
| Novo agendamento | Cadastro com data, cliente, contato e procedimento (clientes ficam salvas) |
| Finanças | Recebido, gastos, lucro, serviços mais/menos pedidos, filtro de período |
| Salário × Caixa | Divisão do lucro, % do salário e compras de materiais |

---

## Requisitos
- **Python 3.10 ou superior** (`python3 --version` para conferir)
- **Git** (`git --version`)

## Rodar localmente

### 1. Baixar o projeto
```bash
git clone https://github.com/SEU-USUARIO/agenda-manicure.git
cd agenda-manicure
```

### 2. Criar o ambiente virtual (só na primeira vez)

**Linux / WSL / Mac**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Quando ativado, o terminal mostra `(.venv)` no começo da linha.

### 3. Instalar as dependências
```bash
python -m pip install -r requirements.txt
```

### 4. Iniciar o site
```bash
python app.py
```

Abra no navegador: **http://localhost:5000**

O arquivo `manicure.db` é criado automaticamente na primeira execução, já com os 8 serviços padrão.

### Nas próximas vezes
```bash
cd agenda-manicure
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
python app.py
```
Para parar o site: `Ctrl + C`.

---

## Testar no celular (mesma rede Wi-Fi)
1. Descubra o IP do computador (`ipconfig` no Windows, `hostname -I` no Linux).
2. No celular, abra `http://IP-DO-COMPUTADOR:5000`.

> No **WSL**, o IP do Linux não é acessível pelo celular. Use o IP do Windows (`ipconfig`) e, se não abrir, libere a porta 5000 no firewall do Windows.

---

## Problemas comuns

| Erro | Solução |
|------|---------|
| `externally-managed-environment` | Não use `pip` direto. Crie o `.venv` (passo 2) e use `python -m pip install ...` |
| `No module named 'flask'` | O ambiente não está ativado ou as dependências não foram instaladas (passos 2 e 3) |
| `Address already in use` | A porta 5000 está ocupada. Feche o outro programa ou mude a porta no final do `app.py` |
| `python: command not found` | Use `python3` em vez de `python` (fora do ambiente virtual) |
| Quero zerar os dados | Pare o site e apague o arquivo `manicure.db` |

---

## Estrutura
```
├── app.py              # rotas, regras e banco de dados
├── requirements.txt    # dependências
├── static/style.css    # visual (rosa pastel, rose gold e dourado)
└── templates/          # telas HTML
```

## Como as contas funcionam
- Só atendimentos marcados como **Concluído** contam como receita.
- **Lucro** = recebido − custo direto dos serviços − compras avulsas de materiais.
- O lucro é dividido entre **salário** e **reserva da empresa** pela porcentagem definida na tela *Salário × Caixa* (padrão 60% / 40%).
- Preço e custo ficam gravados em cada agendamento, então mudar o valor de um serviço não altera o histórico.

## Trabalhando em equipe
1. `git pull` antes de começar.
2. Crie uma branch por alteração: `git checkout -b nome-da-alteracao`
3. Commit e push: `git add . && git commit -m "descrição" && git push -u origin nome-da-alteracao`
4. Abra um **Pull Request** no GitHub e peça revisão antes do merge na `main`.

⚠️ **Nunca suba o `manicure.db`** (tem dados reais das clientes). Ele já está no `.gitignore`.

## Variáveis de ambiente
| Variável | Para que serve |
|----------|----------------|
| `SECRET_KEY` | Chave de segurança das sessões. Defina um valor próprio em produção |
