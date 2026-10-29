from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI
import os
import json

# Inicializa a API web e o cliente da OpenAI
app = FastAPI(title="AI Refund & Fraud API", version="1.0")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "SUA_CHAVE_AQUI"))

# 1. O que a API espera receber (Input)
class RefundRequest(BaseModel):
    order_id: str
    customer_id: str
    account_age_days: int
    total_orders: int
    previous_refunds: int
    claim_reason: str
    order_value_brl: float

# 2. O que a LLM é forçada a devolver (Output Estruturado)
class RefundDecision(BaseModel):
    action: str = Field(..., description="'APPROVE', 'DENY', ou 'MANUAL_REVIEW'")
    fraud_risk_score: int = Field(..., description="Nota de risco de 0 a 100")
    justification: str = Field(..., description="Justificativa curta da decisão")

@app.post("/api/v1/analyze-refund", response_model=RefundDecision)
async def analyze_refund(request: RefundRequest):
    """
    Endpoint que recebe o pedido de reembolso e usa IA para julgar a solicitação.
    """
    
    # Montagem do prompt com as regras de negócio de risco
    system_prompt = """
    Você é um agente de risco e prevenção a fraudes de um app de delivery.
    Sua missão é analisar pedidos de reembolso e decidir a melhor ação.
    
    Regras da Empresa:
    - Clientes com mais de 30 pedidos e histórico limpo (0 reembolsos): APPROVE automático para valores < R$ 100.
    - Contas novas (menos de 7 dias) pedindo reembolso de valor alto: DENY ou MANUAL_REVIEW (alto risco).
    - Se a taxa de reembolso do cliente (reembolsos / total_orders) for > 10%, marque como alto risco.
    
    Responda apenas com o JSON correspondente à estrutura solicitada.
    """
    
    user_prompt = f"""
    Dados do Cliente e do Pedido:
    - Idade da conta: {request.account_age_days} dias
    - Total de pedidos na vida: {request.total_orders}
    - Reembolsos anteriores: {request.previous_refunds}
    - Valor deste pedido: R$ {request.order_value_brl}
    - Reclamação do cliente: "{request.claim_reason}"
    """

    try:
        # Chamada à LLM forçando a saída em formato JSON correspondente ao Pydantic
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0 # Temperatura 0 para decisões lógicas e determinísticas
        )
        
        # Converte a string de texto da OpenAI em um dicionário Python real
        decision_data = json.loads(response.choices[0].message.content)
        return decision_data
        
    except Exception as e:
        # Se a API da OpenAI falhar, encaminha para análise humana por segurança
        raise HTTPException(status_code=500, detail=f"Erro no processamento da IA: {str(e)}")