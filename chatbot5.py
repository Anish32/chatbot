import torch
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering

# Load pre-trained DistilBERT model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased-distilled-squad')
model = DistilBertForQuestionAnswering.from_pretrained('distilbert-base-uncased-distilled-squad')

# Function to generate an answer
def generate_answer(question, context):
    inputs = tokenizer(question, context, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get the most likely beginning and end of the answer
    start_scores = outputs.start_logits
    end_scores = outputs.end_logits

    # Get the tokens from input IDs and find the best span for the answer
    all_tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    answer_tokens = all_tokens[torch.argmax(start_scores): torch.argmax(end_scores) + 1]
    
    # Convert tokens back to string and clean it
    answer = tokenizer.convert_tokens_to_string(answer_tokens)
    
    return answer.strip()

# Test the chatbot
def chat():
    # Define the factual context
    context = "Python was created by Guido van Rossum and was released in 1991."
    
    while True:
        question = input("Ask a question: ")
        if question.lower() == 'exit':
            break
        answer = generate_answer(question, context)
        print(f"Answer: {answer}")

chat()
