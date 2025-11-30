# **Cognos - Projeto PCS3643**

### **Integrantes do Grupo**

-   **Bernardo Asztalos Teixeira**
-   **Beatriz Barreto Tavora**
-   **Hugo Spadete Arrivabene**
-   **Caique Granja Maia**

## **Descrição do Projeto**

Este repositório contém o **backend** do projeto *Cognos*.\
Aqui estão implementadas todas as rotas necessárias para o funcionamento
do site, bem como sua integração com a base de dados.

Você pode testar cada rota independentemente do frontend acessando:\
http://localhost:8000/docs

## **Execução do Projeto**

Backend e frontend devem rodar simultaneamente:

-   Backend: 8000\
-   Frontend: 8081

## Observação Importante

O arquivo `.env` está no repositório apenas para facilitar a correção,
apesar de não ser uma boa prática.

## **Como rodar localmente**

1.  Instale dependências:

```
    pip install uvicorn[standard]
    pip install -r requirements.txt
```

2.  Execute:

```
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
