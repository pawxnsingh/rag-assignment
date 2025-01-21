from django.db import models
from pgvector.django import VectorField
from django.contrib.postgres.fields import ArrayField
# this will store all the name of the document
class Documents(models.Model):
    title = models.CharField(max_length=200, blank=True)    
    pdf_file = models.FileField(upload_to='pdfs/', null=True, blank=True)    
    class Meta:
        db_table = 'documents'  
    def __str__(self):
        return self.title or f"Document {self.pk}"
    
class Tags(models.Model):
    name = models.TextField()
    class Meta:
        db_table = 'tags'
        
class Questions(models.Model):
    document = models.ForeignKey(Documents,related_name="questions",on_delete=models.CASCADE) # this is to tell which document is getting astk
    refrences = ArrayField(models.CharField(),blank=True,default=list)
    question = models.TextField()
    answer = models.TextField()
    
    class Meta:
        db_table = 'questions'
    
class DocumentTags(models.Model):
    document = models.ForeignKey(Documents,related_name="document_tags",on_delete=models.CASCADE)
    tag = models.ForeignKey(Tags,related_name="document_tags",on_delete=models.CASCADE)
    class Meta:
        db_table = 'document_tags'

class DocumentInformationChunks(models.Model):
    document = models.ForeignKey(Documents,related_name="document_information_chunks",on_delete=models.CASCADE)
    chunk = models.TextField()
    data = models.TextField(null=True, blank = True)
    embedding = VectorField(dimensions=1536)
    class Meta:
        db_table = 'document_information_chunks'
    
def set_openai_api_key():
    with connection.cursor() as cursor:
        cursor.execute("""
            SET ai.openai_api_key = %s;
            SELECT pg_catalog.current_setting('ai.openai_api_key', true) AS api_key;
        """, [getenv("OPENAI_API_KEY")])
