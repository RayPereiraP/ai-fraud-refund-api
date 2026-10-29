# 🛡️ AI Fraud Shield & Refund Triage API

Uma Micro-API desenvolvida com **FastAPI** e **OpenAI** para automatizar a tomada de decisão em solicitações de reembolso no ecossistema de delivery, equilibrando a experiência do usuário (CX) e a prevenção a fraudes.

## 🎯 Problema de Negócio (O Caso iFood)
Processar estornos é caro. Se um cliente fiel tem um problema genuíno com o pedido e a plataforma demora dias para avaliar, a frustração gera churn. Por outro lado, aprovar todos os pedidos automaticamente abre portas para redes de fraudadores que criam contas falsas para comer de graça. 

Este agente atua como uma "API sem backend profundo", que pode ser facilmente plugada no orquestrador principal (como n8n ou Make) para julgar as solicitações em menos de 1 segundo.

### ⚙️ Como a IA atua
A API recebe um payload com o histórico relacional do usuário (idade da conta, volume de compras, estornos passados) e a reclamação atual. Através de *Prompt Engineering* estruturado com `Pydantic` e *JSON outputs*, a LLM atua como um motor de regras inteligente, retornando instantaneamente se o caso deve ser aprovado na hora (wallet credit), negado, ou enviado para auditoria humana de N2.

## 🚀 Como Executar e Testar

### 1. Instalação e Execução
Certifique-se de ter o Python 3.9+ instalado.
\`\`\`bash
git clone https://github.com/seu-usuario/ai-fraud-refund-api.git
cd ai-fraud-refund-api
pip install -r requirements.txt
export OPENAI_API_KEY="sua_chave_da_openai"
uvicorn src.api:app --reload
\`\`\`

### 2. Acessando a Documentação (Swagger Nativo)
O FastAPI gera a interface de documentação automaticamente. Abra no navegador:
* `http://localhost:8000/docs`

### 3. Teste cURL (Simulando um Cliente Fiel)
\`\`\`bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/analyze-refund' \
  -H 'Content-Type: application/json' \
  -d '{
  "order_id": "ORD-5512",
  "customer_id": "CUST-992",
  "account_age_days": 450,
  "total_orders": 85,
  "previous_refunds": 1,
  "claim_reason": "Veio faltando a batata frita e o refrigerante derramou.",
  "order_value_brl": 45.90
}'
\`\`\`

**Resposta Esperada:**
\`\`\`json
{
  "action": "APPROVE",
  "fraud_risk_score": 5,
  "justification": "Cliente altamente engajado, histórico limpo de fraudes e valor do estorno baixo."
}
\`\`\`