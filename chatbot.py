from langchain_openai import OpenAI
import os
'''
    url = "https://apps.aws-london-novaprd1.svc.singlestore.com:8000/modelasaservice/5708b167-035c-45f5-8c47-daa5f1c0dfbb/v1"
    token = "eyJhbGciOiJFUzUxMiIsImtpZCI6IjhhNmVjNWFmLThlNWEtNDQxOS04NmM4LWRkMDkxN2U1YWNlMSIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsibm92YXB1YmxpYyJdLCJleHAiOjE3NDU4NzkwNjUsIm5iZiI6MTc0MzI4NzA2MCwiaWF0IjoxNzQzMjg3MDY1LCJzdWIiOiIyM2VmMGViMy0yZTMwLTQ1MjMtODc3NS1hMWVkZjAzZjAxYWUiLCJlbWFpbCI6ImRyb2RyaWd1ZXNAc2luZ2xlc3RvcmUuY29tIiwiaWRwSUQiOiJiNmQ2YTZiZC04NjYyLTQzYjItYjlkZS1hZjNhMjdlMGZhYzgiLCJlbWFpbFZlcmlmaWVkIjp0cnVlLCJzc29TdWJqZWN0IjoiMjNlZjBlYjMtMmUzMC00NTIzLTg3NzUtYTFlZGYwM2YwMWFlIiwidmFsaWRGb3JQb3J0YWwiOmZhbHNlLCJyZWFkT25seSI6ZmFsc2UsIm5vdmFBcHBJbmZvIjp7InNlcnZpY2VJRCI6IjU3MDhiMTY3LTAzNWMtNDVmNS04YzQ3LWRhYTVmMWMwZGZiYiIsImFwcElEIjoiZTI4N2QyZWEtNThkMy00MmJlLWEzOWItOTBlMWRjNjk3MzEzIiwiYXBwVHlwZSI6Ik1vZGVsQXNBU2VydmljZSJ9fQ.ASVeBTryqeSN865zhXGVt7ijI0I42_6keWjerbb5TM4kFUZLnjVfwKtAtUIl6iQkEOOXVVv3l5jRuzL-Dg14JyRLAR79XN5eSOpSa3_BviEAeja5WX3ZZvMpYMGZjHyeXaZwTbyAeolZ0NnSLZNU9OPQiWlIys3mTlkmZFlLSxJLtx5g"
'''
def reply_to_prompt(prompt):
    url =""
    token = ""

    llm = OpenAI(
        model_name="unsloth/Meta-Llama-3.1-8B-Instruct",  # Adjust based on your model name
        temperature=0.6,
        openai_api_key=token,
        openai_api_base=url  # External Llama LLM endpoint
    )

    response = llm.invoke(prompt)
    
    return response