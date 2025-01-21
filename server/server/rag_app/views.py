import os
import json
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
import pdfplumber
from anyio import sleep
from .constants import IDEAL_CHUNK_LENGTH, CREATE_FACT_CHUNKS_SYSTEM_PROMPT, RESPOND_TO_MESSAGE_SYSTEM_PROMPT
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pgvector.django import CosineDistance
from .openai_client import client
from .models import Documents, DocumentInformationChunks, Questions

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),timeout=20,max_retries=0)

# this is the post request that will handle the upload pdf thing,
# parse pdf to text create chunks out of it, and make and store embedding for same
def pdf_to_text(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def upload_documents(request:HttpRequest) -> HttpResponse:
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']

        if not pdf_file.name.endswith('.pdf'):
            return HttpResponse("Only PDF files are allowed.", status=400)

        document = Documents.objects.create(
            title=request.POST.get('title', 'Untitled Document'),
            pdf_file=pdf_file
        )
        # now i have to do llm stuff
        # STEP 1: parse the pdf
        try:
            pdf_text = pdf_to_text(pdf_file)
            pdf_text_chunks:list[str] = []

            for i in range(0, len(pdf_text), IDEAL_CHUNK_LENGTH):
                pdf_text_chunks.append(pdf_text[i:i+IDEAL_CHUNK_LENGTH])
            
            for index, chunks in enumerate(pdf_text_chunks):
                fact_extraction = client.chat.completions.create(
                    model="gpt-4o-2024-08-06",
                    messages = [
                        {"role": "developer", "content": f"{CREATE_FACT_CHUNKS_SYSTEM_PROMPT}"},
                        {"role": "user", "content": f"{chunks}"}
                    ],
                    temperature=0.0,
                    max_tokens=150
                )
                facts = fact_extraction.choices[0].message.content
                
                embedding_response = client.embeddings.create(model="text-embedding-ada-002", input=facts)                
                embedding = embedding_response.data[0].embedding
                document_chunk = DocumentInformationChunks.objects.create(
                    document_id = document.id,
                    data = chunks,
                    chunk = facts,
                    embedding = embedding                    
                )
            
            return JsonResponse({"success":True, "document_id" : document.id, "document_title":document.title}, status = 201)                

        except Exception as e:
            return HttpResponse(f"Error parsing PDF: {str(e)}", status=500)


    return HttpResponse("Invalid request", status=400)


def search_similar_chunks(user_embedding, limit=5):
    return (
        DocumentInformationChunks.objects
        # order_by(CosineDistance(..)) directly.
        .annotate(distance=CosineDistance('embedding', user_embedding))
        .order_by('distance')[:limit]
    )
    
def chatDocuments(request:HttpRequest) -> HttpResponse:
    if (request.method == 'POST'):
        # parse body in the django
        body_bytes = request.body        
        body_str = body_bytes.decode('utf-8')
        data = json.loads(body_str)
        
        document_id = data['document_id']
        if not document_id:
            return JsonResponse({"error":"no document_id provided"}, status=400)
        
        question = data['question']
        if not question:
            return JsonResponse({"error": "No query provided"}, status=400)
        
        # now create the embedd of the question and then do the cosine similarity search
        embedding_response = client.embeddings.create(model="text-embedding-ada-002", input=question)
        question_embedding = embedding_response.data[0].embedding
        relevant_chunks = search_similar_chunks(question_embedding)        
        
        data = [
            {
                "chunk_id": c.id,
                "document_id": c.document_id,
                "chunk_text": c.chunk,
                "chunk_data": c.data,
                "distance": c.distance
            }
            for c in relevant_chunks
        ]
                
        context = "\n\n".join([
            f"{d['chunk_text']}"
            for _, d in enumerate(data)
        ])
        context = context.replace("\n-"," ")
        
        chunk_refrences_list = [item["chunk_data"] for item in data]                
        # now do the db entry
        # get the relevant chunks and data now do the llm call
        answer_response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages = [
                {"role": "developer", "content": f"{RESPOND_TO_MESSAGE_SYSTEM_PROMPT.replace('{{knowledge}}',context)}"},
                {"role": "user", "content": f"{question}"}
            ],
            temperature=0.0,
        )
                
        response = answer_response.choices[0].message.content
        
        question_db_entry = Questions.objects.create(
            document_id = document_id,
            question = question,
            answer = response,
            refrences = chunk_refrences_list
        )
                
        return JsonResponse({"document_id":question_db_entry.document_id,"question":question_db_entry.question, "answer":question_db_entry.answer, "refrences":question_db_entry.refrences})
    
    return JsonResponse({"error: ":"Invalid request"}, status=400)

    